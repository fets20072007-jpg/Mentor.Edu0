from fastapi import APIRouter
from fastapi import Depends

from sqlalchemy.orm import Session

from app.database.dependencies import get_db

from app.database.models import Video

from app.schema.video import (
    VideoCreate,
    VideoResponse
)

from app.services.education.video_service import create_video

router = APIRouter(

    prefix="/library",

    tags=["Library Videos"]

)


@router.post(

    "/chapters/{chapter_id}/videos",

    response_model=VideoResponse

)

def register_video(

    chapter_id: int,

    video: VideoCreate,

    db: Session = Depends(get_db)

):

    return create_video(

        db,

        chapter_id,

        video

    )


@router.get(

    "/chapters/{chapter_id}/videos",

    response_model=list[VideoResponse]

)

def list_videos(

    chapter_id: int,

    db: Session = Depends(get_db)

):

    return (

        db.query(Video)

        .filter(

            Video.chapter_id == chapter_id

        )

        .all()

    )


@router.get(

    "/videos/{video_id}",

    response_model=VideoResponse

)

def get_video(

    video_id: int,

    db: Session = Depends(get_db)

):

    return (

        db.query(Video)

        .filter(

            Video.id == video_id

        )

        .first()

    )