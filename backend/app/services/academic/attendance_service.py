from sqlalchemy.orm import Session

from app.database.models import Attendance

from app.schema.attendance import AttendanceCreate


def register_attendance(

    db: Session,

    teacher_id: int,

    attendance: AttendanceCreate

):

    nova = Attendance(

        teacher_id=teacher_id,

        student_id=attendance.student_id,

        classroom_id=attendance.classroom_id,

        subject_id=attendance.subject_id,

        status=attendance.status,

        justificada=attendance.justificada,

        motivo=attendance.motivo,

        arquivo=attendance.arquivo,

        observacao=attendance.observacao

    )

    db.add(nova)

    db.commit()

    db.refresh(nova)

    return nova

def get_all_attendance(db: Session):
    return db.query(Attendance).all()


def get_attendance_by_id(db: Session, attendance_id: int):
    return (
        db.query(Attendance)
        .filter(Attendance.id == attendance_id)
        .first()
    )