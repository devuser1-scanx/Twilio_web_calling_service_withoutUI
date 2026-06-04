from sqlalchemy import text
from database import SessionLocal


def get_appointment_by_id(appointment_id: str):
    """
    Fetch appointment from PostgreSQL appointment table.
    """

    query = text("""
        SELECT
            appointment_id,
            first_name,
            last_name,
            phone,
            email,
            appointment_type,
            date,
            time,
            calendar,
            status_label
        FROM appointment
        WHERE appointment_id = :appointment_id
        LIMIT 1
    """)

    with SessionLocal() as db:
        row = db.execute(
            query,
            {"appointment_id": appointment_id}
        ).mappings().first()

    return dict(row) if row else None


def get_patient_phone_by_appointment_id(appointment_id: str):
    appointment = get_appointment_by_id(appointment_id)

    if not appointment:
        return None

    return appointment.get("phone")


def create_call_logs_table_if_not_exists():
    """
    Optional call log table.
    """

    query = text("""
        CREATE TABLE IF NOT EXISTS call_logs (
            id SERIAL PRIMARY KEY,
            appointment_id VARCHAR(50),
            staff_phone VARCHAR(50),
            patient_number VARCHAR(20),
            direction VARCHAR(20) NOT NULL,
            call_sid VARCHAR(100),
            status VARCHAR(50),
            duration INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT NOW(),
            updated_at TIMESTAMP DEFAULT NOW()
        );
    """)

    with SessionLocal() as db:
        db.execute(query)
        db.commit()


def log_call(
    appointment_id: str,
    staff_phone: str,
    patient_number: str,
    direction: str,
    call_sid: str,
    status: str = "initiated",
):
    query = text("""
        INSERT INTO call_logs (
            appointment_id,
            staff_phone,
            patient_number,
            direction,
            call_sid,
            status,
            created_at,
            updated_at
        )
        VALUES (
            :appointment_id,
            :staff_phone,
            :patient_number,
            :direction,
            :call_sid,
            :status,
            NOW(),
            NOW()
        )
    """)

    with SessionLocal() as db:
        db.execute(query, {
            "appointment_id": appointment_id,
            "staff_phone": staff_phone,
            "patient_number": patient_number,
            "direction": direction,
            "call_sid": call_sid,
            "status": status,
        })
        db.commit()


def update_call_log(call_sid: str, status: str, duration: int = 0):
    query = text("""
        UPDATE call_logs
        SET
            status = :status,
            duration = :duration,
            updated_at = NOW()
        WHERE call_sid = :call_sid
    """)

    with SessionLocal() as db:
        db.execute(query, {
            "call_sid": call_sid,
            "status": status,
            "duration": duration,
        })
        db.commit()


def get_recent_logs(limit: int = 50):
    query = text("""
        SELECT *
        FROM call_logs
        ORDER BY created_at DESC
        LIMIT :limit
    """)

    with SessionLocal() as db:
        rows = db.execute(query, {"limit": limit}).mappings().all()

    return [dict(row) for row in rows]