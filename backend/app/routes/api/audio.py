import json
import logging
import uuid
from pathlib import Path
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, WebSocket, WebSocketDisconnect
from sqlalchemy.orm import Session
from app.database.base import get_db, SessionLocal
from app.dependencies.auth import get_current_user
from app.models.user import User
from app.models.audio_recording import AudioRecording
from app.core.config import settings
from app.core.security import decode_token
from app.schemas.audio import AudioUploadResponse, AudioTranscriptionResponse

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/audio", tags=["Audio"])


@router.post("/upload", response_model=AudioUploadResponse)
def upload_audio(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if not file.filename:
        raise HTTPException(status_code=400, detail="No file provided")

    upload_dir = Path(settings.UPLOAD_DIR) / "audio"
    upload_dir.mkdir(parents=True, exist_ok=True)

    ext = Path(file.filename).suffix or ".webm"
    stored_name = f"{uuid.uuid4().hex}{ext}"
    dest = upload_dir / stored_name

    content = file.file.read()
    if len(content) > settings.MAX_UPLOAD_SIZE_MB * 1024 * 1024:
        raise HTTPException(
            status_code=400,
            detail=f"File too large. Maximum size is {settings.MAX_UPLOAD_SIZE_MB}MB",
        )
    try:
        with open(dest, "wb") as f:
            f.write(content)
    except Exception as e:
        logger.error(f"Failed to save audio file: {e}")
        raise HTTPException(status_code=500, detail="Failed to save audio file")

    mime_type = file.content_type or "audio/webm"
    record = AudioRecording(
        user_id=str(current_user.id),
        file_path=str(dest),
        mime_type=mime_type,
        processing_status="pending",
    )
    db.add(record)
    db.commit()
    db.refresh(record)

    from app.workers.tasks import transcribe_audio
    transcribe_audio.delay(str(record.id))

    return AudioUploadResponse(
        id=record.id,
        processing_status=record.processing_status,
        message="Audio uploaded successfully. Transcription in progress.",
    )


@router.get("/{audio_id}/status", response_model=AudioTranscriptionResponse)
def get_audio_status(
    audio_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    record = db.query(AudioRecording).filter(
        AudioRecording.id == audio_id,
        AudioRecording.user_id == str(current_user.id),
    ).first()

    if not record:
        raise HTTPException(status_code=404, detail="Audio recording not found")

    return AudioTranscriptionResponse(
        id=record.id,
        transcript=record.transcript,
        ai_feedback=record.ai_feedback,
        processing_status=record.processing_status,
    )


@router.websocket("/ws")
async def audio_websocket(websocket: WebSocket):
    await websocket.accept()
    logger.info("WebSocket audio connection accepted")

    try:
        metadata = await websocket.receive_text()
        meta = json.loads(metadata)
    except Exception:
        await websocket.send_json({"error": "Invalid metadata. Send JSON with token."})
        await websocket.close()
        return

    token = meta.get("token", "")
    payload = decode_token(token)
    if not payload:
        await websocket.send_json({"error": "Authentication required"})
        await websocket.close()
        return

    user_id = payload.get("sub")
    subject = meta.get("subject")
    topic = meta.get("topic")

    audio_chunks = []

    try:
        while True:
            chunk = await websocket.receive_bytes()
            audio_chunks.append(chunk)
    except WebSocketDisconnect:
        logger.info(f"WebSocket disconnected after receiving {len(audio_chunks)} chunks")
    except Exception as e:
        logger.error(f"WebSocket error: {e}")

    if not audio_chunks:
        await websocket.send_json({"error": "No audio data received"})
        return

    upload_dir = Path(settings.UPLOAD_DIR) / "audio"
    upload_dir.mkdir(parents=True, exist_ok=True)
    stored_name = f"ws_{uuid.uuid4().hex}.webm"
    dest = upload_dir / stored_name

    with open(dest, "wb") as f:
        for chunk in audio_chunks:
            f.write(chunk)

    db = SessionLocal()
    try:
        mime_type = "audio/webm"
        record = AudioRecording(
            user_id=user_id or "unknown",
            file_path=str(dest),
            mime_type=mime_type,
            processing_status="processing",
        )
        db.add(record)
        db.commit()
        db.refresh(record)

        from app.services.audio_service import AudioService
        service = AudioService()

        try:
            transcript = service.transcribe(str(dest))
            record.transcript = transcript

            feedback = service.generate_feedback(transcript, subject, topic)
            record.ai_feedback = feedback
            record.processing_status = "completed"
        except Exception as e:
            logger.error(f"Audio processing failed: {e}")
            record.processing_status = "failed"

        db.commit()
        db.refresh(record)

        await websocket.send_json({
            "id": record.id,
            "transcript": record.transcript,
            "ai_feedback": record.ai_feedback,
            "processing_status": record.processing_status,
        })
    except Exception as e:
        logger.error(f"Database error in WebSocket handler: {e}")
        await websocket.send_json({"error": "Processing failed"})
    finally:
        db.close()


@router.post("/process/{audio_id}", response_model=dict)
def process_audio(
    audio_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    record = db.query(AudioRecording).filter(
        AudioRecording.id == audio_id,
        AudioRecording.user_id == str(current_user.id),
    ).first()

    if not record:
        raise HTTPException(status_code=404, detail="Audio recording not found")

    if record.processing_status == "completed":
        return {
            "message": "Already processed",
            "transcript": record.transcript,
            "ai_feedback": record.ai_feedback,
        }

    from app.workers.tasks import transcribe_audio
    transcribe_audio.delay(audio_id)

    return {"message": "Processing started", "audio_id": audio_id}
