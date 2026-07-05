from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database.base import get_db
from app.dependencies.auth import get_current_user
from app.models.user import User
from app.services.live_session_service import LiveSessionService
from app.schemas.live import CreateRoomRequest, RoomResponse, EndSessionRequest, SessionDetailResponse

router = APIRouter(prefix="/live", tags=["Live Teaching"])


@router.post("/rooms", response_model=RoomResponse)
def create_room(
    request: CreateRoomRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    service = LiveSessionService(db)
    result = service.create_room(
        tutor_id=str(current_user.id),
        subject=request.subject,
        topic=request.topic,
        student_id=request.student_id,
    )
    return RoomResponse(**result)


@router.get("/rooms/{room_id}", response_model=SessionDetailResponse)
def get_room(
    room_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    service = LiveSessionService(db)
    session = service.get_session(room_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    uid = str(current_user.id)
    if session.tutor_id != uid and session.student_id != uid:
        raise HTTPException(status_code=403, detail="Access denied")

    return SessionDetailResponse(
        id=session.id,
        room_id=session.room_id,
        subject=session.subject,
        topic=session.topic,
        status=session.status,
        provider=session.provider,
        recording_url=session.recording_url,
        started_at=session.started_at,
        ended_at=session.ended_at,
        created_at=session.created_at,
    )


@router.post("/rooms/{room_id}/start", response_model=SessionDetailResponse)
def start_session(
    room_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    service = LiveSessionService(db)
    session = service.start_session(room_id, str(current_user.id))
    if not session:
        raise HTTPException(status_code=404, detail="Session not found or not your room")

    return SessionDetailResponse(
        id=session.id,
        room_id=session.room_id,
        subject=session.subject,
        topic=session.topic,
        status=session.status,
        provider=session.provider,
        recording_url=session.recording_url,
        started_at=session.started_at,
        ended_at=session.ended_at,
        created_at=session.created_at,
    )


@router.post("/rooms/{room_id}/end", response_model=SessionDetailResponse)
def end_session(
    room_id: str,
    request: EndSessionRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    service = LiveSessionService(db)
    session = service.end_session(
        room_id,
        str(current_user.id),
        recording_url=request.recording_url,
    )
    if not session:
        raise HTTPException(status_code=404, detail="Session not found or not your room")

    return SessionDetailResponse(
        id=session.id,
        room_id=session.room_id,
        subject=session.subject,
        topic=session.topic,
        status=session.status,
        provider=session.provider,
        recording_url=session.recording_url,
        started_at=session.started_at,
        ended_at=session.ended_at,
        created_at=session.created_at,
    )


@router.get("", response_model=list[SessionDetailResponse])
def list_sessions(
    role: str = "tutor",
    skip: int = 0,
    limit: int = 50,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    service = LiveSessionService(db)
    sessions, _ = service.get_user_sessions(
        str(current_user.id), role, skip, limit
    )
    return [
        SessionDetailResponse(
            id=s.id,
            room_id=s.room_id,
            subject=s.subject,
            topic=s.topic,
            status=s.status,
            provider=s.provider,
            recording_url=s.recording_url,
            started_at=s.started_at,
            ended_at=s.ended_at,
            created_at=s.created_at,
        )
        for s in sessions
    ]
