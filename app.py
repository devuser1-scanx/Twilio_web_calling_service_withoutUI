from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from routes.voice import router as voice_router
from models import create_call_logs_table_if_not_exists, get_appointment_by_id

app = FastAPI(title="ScanX Voice Calling Service")

app.include_router(voice_router)

app.mount("/static", StaticFiles(directory="static"), name="static")


@app.on_event("startup")
def startup_event():
    try:
        create_call_logs_table_if_not_exists()
        print("Call logs table checked.")
    except Exception as e:
        print("Could not create/check call_logs table:", str(e))


@app.get("/")
def root():
    return {
        "service": "ScanX Voice Calling Service",
        "status": "running",
    }


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/test-appointment/{appointment_id}")
def test_appointment(appointment_id: str):
    """
    Temporary DB testing route.
    Remove or protect this before production.
    """
    return get_appointment_by_id(appointment_id)