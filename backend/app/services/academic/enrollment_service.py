from sqlalchemy.orm import Session

from app.database.models import Enrollment

from app.schema.enrollment import EnrollmentCreate


def create_enrollment(
    db: Session,
    enrollment: EnrollmentCreate
):

    nova = Enrollment(

        user_id=enrollment.user_id,

        classroom_id=enrollment.classroom_id

    )

    db.add(nova)

    db.commit()

    db.refresh(nova)

    return nova


def get_enrollments(db: Session):

    return db.query(Enrollment).all()