from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.database.base import get_db
from app.dependencies.auth import get_current_user
from app.models.user import User
from app.services.study_group_service import StudyGroupService
from app.schemas.study_group import (
    CreateGroupRequest,
    StudyGroupResponse,
    StudyGroupDetailResponse,
    StudyGroupListResponse,
    StudyGroupMemberResponse,
    SendMessageRequest,
    MessageResponse,
    MessagesResponse,
)

router = APIRouter(prefix="/study-groups", tags=["Study Groups"])


def _group_response(group, member_count: int = 0, creator_name: str = None) -> StudyGroupResponse:
    return StudyGroupResponse(
        id=group.id,
        name=group.name,
        description=group.description,
        subject=group.subject,
        creator_id=group.creator_id,
        max_members=group.max_members,
        is_active=group.is_active,
        created_at=group.created_at,
        member_count=member_count,
        creator_name=creator_name,
    )


@router.post("", response_model=StudyGroupResponse)
def create_group(
    request: CreateGroupRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    service = StudyGroupService(db)
    if not request.name.strip():
        raise HTTPException(status_code=400, detail="Group name is required")
    group = service.create_group(
        user_id=str(current_user.id),
        name=request.name.strip(),
        subject=request.subject,
        description=request.description,
        max_members=request.max_members,
    )
    return _group_response(group, member_count=1, creator_name=current_user.full_name)


@router.get("", response_model=StudyGroupListResponse)
def list_user_groups(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    service = StudyGroupService(db)
    groups = service.get_user_groups(str(current_user.id))
    result = []
    for g in groups:
        result.append(_group_response(g, member_count=len(g.members) if hasattr(g, "members") and g.members else 0))
    return StudyGroupListResponse(groups=result, total=len(result))


@router.get("/browse", response_model=StudyGroupListResponse)
def browse_groups(
    subject: str = Query(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    service = StudyGroupService(db)
    groups = service.browse_groups(subject)
    result = []
    for g in groups:
        member_count = service.repo.get_member_count(g.id)
        result.append(_group_response(g, member_count=member_count))
    return StudyGroupListResponse(groups=result, total=len(result))


@router.get("/{group_id}", response_model=StudyGroupDetailResponse)
def get_group(
    group_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    service = StudyGroupService(db)
    group = service.get_group_detail(group_id)
    if not group:
        raise HTTPException(status_code=404, detail="Group not found")
    members = [
        StudyGroupMemberResponse(
            id=m.id,
            user_id=m.user_id,
            role=m.role,
            joined_at=m.joined_at,
            full_name=m.user.full_name if m.user else None,
        )
        for m in group.members
    ]
    resp = _group_response(group, member_count=len(members), creator_name=group.creator.full_name if group.creator else None)
    return StudyGroupDetailResponse(
        **resp.model_dump(),
        members=members,
    )


@router.post("/{group_id}/join")
def join_group(
    group_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    service = StudyGroupService(db)
    result = service.join_group(group_id, str(current_user.id))
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    return result


@router.post("/{group_id}/leave")
def leave_group(
    group_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    service = StudyGroupService(db)
    result = service.leave_group(group_id, str(current_user.id))
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    return result


@router.get("/{group_id}/messages", response_model=MessagesResponse)
def get_messages(
    group_id: str,
    offset: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    service = StudyGroupService(db)
    result = service.get_messages(group_id, str(current_user.id), offset, limit)
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    messages = [
        MessageResponse(
            id=m.id,
            group_id=m.group_id,
            user_id=m.user_id,
            content=m.content,
            created_at=m.created_at,
            full_name=m.user.full_name if m.user else None,
        )
        for m in result["messages"]
    ]
    return MessagesResponse(messages=messages, total=result["total"])


@router.post("/{group_id}/messages", response_model=MessageResponse)
def send_message(
    group_id: str,
    request: SendMessageRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    service = StudyGroupService(db)
    if not request.content.strip():
        raise HTTPException(status_code=400, detail="Message content is required")
    result = service.send_message(group_id, str(current_user.id), request.content.strip())
    if isinstance(result, dict) and "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    return MessageResponse(
        id=result["id"],
        group_id=result["group_id"],
        user_id=result["user_id"],
        content=result["content"],
        created_at=result["created_at"],
        full_name=current_user.full_name,
    )


@router.delete("/{group_id}")
def delete_group(
    group_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    service = StudyGroupService(db)
    result = service.delete_group(group_id, str(current_user.id))
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    return result
