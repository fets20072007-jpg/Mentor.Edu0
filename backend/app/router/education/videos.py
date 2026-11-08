from fastapi import (
    APIRouter,
    Depends,
    HTTPException
)

from sqlalchemy.orm import Session

from app.database.dependencies import get_db

from app.database.models import (
    Video,
    Chapter,
    User
)

from app.schema.video import (
    VideoCreate,
    VideoResponse
)

from app.services.education.video_service import (
    create_video
)

from app.security.auth import (
    get_current_user
)

from app.core.permissions import (
    require_teacher,
    require_library_reader
)


router = APIRouter(
    prefix="/library",
    tags=["Library Videos"]
)


# =========================================================
# PROFESSOR
# CADASTRAR VÍDEO PEDAGÓGICO
# =========================================================

@router.post(
    "/chapters/{chapter_id}/videos",
    response_model=VideoResponse
)
def register_video(
    chapter_id: int,
    video: VideoCreate,

    current_user: User = Depends(
    require_teacher
),

    db: Session = Depends(get_db)
):

    chapter = (
        db.query(Chapter)
        .filter(
            Chapter.id == chapter_id
        )
        .first()
    )

    if not chapter:
        raise HTTPException(
            status_code=404,
            detail="Capítulo não encontrado."
        )

    return create_video(
        db,
        chapter_id,
        video
    )


# =========================================================
# LISTAR VÍDEOS DO CAPÍTULO
# USUÁRIOS AUTENTICADOS
# =========================================================

@router.get(
    "/chapters/{chapter_id}/videos",
    response_model=list[VideoResponse]
)
def list_videos(
    chapter_id: int,

    current_user: User = Depends(
    require_library_reader
),

    db: Session = Depends(get_db)
):

    chapter = (
        db.query(Chapter)
        .filter(
            Chapter.id == chapter_id
        )
        .first()
    )

    if not chapter:
        raise HTTPException(
            status_code=404,
            detail="Capítulo não encontrado."
        )

    return (
        db.query(Video)
        .filter(
            Video.chapter_id == chapter_id
        )
        .all()
    )


# =========================================================
# CONSULTAR VÍDEO
# USUÁRIOS AUTENTICADOS
# =========================================================

@router.get(
    "/videos/{video_id}",
    response_model=VideoResponse
)
def get_video(
    video_id: int,

   current_user: User = Depends(
    require_library_reader
),

    db: Session = Depends(get_db)
):

    video = (
        db.query(Video)
        .filter(
            Video.id == video_id
        )
        .first()
    )

    if not video:
        raise HTTPException(
            status_code=404,
            detail="Vídeo não encontrado."
        )

    return video