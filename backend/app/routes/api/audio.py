import json
import logging
import uuid
import asyncio
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

    if (file.content_type or "") not in settings.ALLOWED_UPLOAD_TYPES or not (file.content_type or "").startswith("audio/"):
        raise HTTPException(status_code=400, detail="Unsupported audio type")
    ext = Path(file.filename).suffix or ".webm"
    stored_name = f"{uuid.uuid4().hex}{ext}"
    dest = upload_dir / stored_name

    try:
        with open(dest, "wb") as f:
            size = 0
            while chunk := file.file.read(1024 * 1024):
                size += len(chunk)
                if size > settings.MAX_UPLOAD_SIZE_MB * 1024 * 1024:
                    raise HTTPException(status_code=400, detail=f"File too large. Maximum size is {settings.MAX_UPLOAD_SIZE_MB}MB")
                f.write(chunk)
    except Exception as e:
        dest.unlink(missing_ok=True)
        if isinstance(e, HTTPException):
            raise
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

    from app.utils.celery_safe import safe_celery_delay
    safe_celery_delay("app.workers.tasks.transcribe_audio", str(record.id))

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

    if payload.get("type") != "access" or not payload.get("sub"):
        await websocket.close(code=1008)
        return
    user_id = payload["sub"]
    subject = meta.get("subject")
    topic = meta.get("topic")

    max_bytes = settings.MAX_UPLOAD_SIZE_MB * 1024 * 1024
    received = 0
    upload_dir = Path(settings.UPLOAD_DIR) / "audio"
    upload_dir.mkdir(parents=True, exist_ok=True)
    dest = upload_dir / f"ws_{uuid.uuid4().hex}.webm"

    disconnected = False
    try:
        with open(dest, "wb") as f:
            while True:
                chunk = await asyncio.wait_for(websocket.receive_bytes(), timeout=30)
                received += len(chunk)
                if received > max_bytes:
                    try:
                        await websocket.send_json({"error": "Audio exceeds size limit"})
                    except Exception:
                        pass
                    await websocket.close(code=1009)
                    dest.unlink(missing_ok=True)
                    return
                f.write(chunk)
    except WebSocketDisconnect:
        logger.info("WebSocket disconnected after receiving %s bytes", received)
        disconnected = True
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        disconnected = True

    if not received:
        logger.warning("No audio data received via WebSocket")
        return

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
            transcript = await asyncio.to_thread(service.transcribe, str(dest))
            record.transcript = transcript

            feedback = await asyncio.to_thread(service.generate_feedback, transcript, subject, topic)
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

    from app.utils.celery_safe import safe_celery_delay
    safe_celery_delay("app.workers.tasks.transcribe_audio", audio_id)

    return {"message": "Processing started", "audio_id": audio_id}
