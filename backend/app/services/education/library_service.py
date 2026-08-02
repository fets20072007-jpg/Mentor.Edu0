from sqlalchemy.orm import Session

from app.database.models import Library
from app.schema.library import LibraryCreate


def create_library(
    db: Session,
    library_data: LibraryCreate,
):
    new_library = Library(
        **library_data.model_dump()
    )

    db.add(new_library)
    db.commit()
    db.refresh(new_library)

    return new_library