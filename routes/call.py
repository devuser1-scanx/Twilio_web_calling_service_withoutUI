from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import HTMLResponse, Response
from twilio.rest import Client
from twilio.twiml.voice_response import VoiceResponse, Dial

from config import (
    TWILIO_ACCOUNT_SID,
    TWILIO_AUTH_TOKEN,
    TWILIO_PHONE,
    # SCANX_STAFF_NUMBER,
    BASE_URL,
    CALL_BUTTON_SECRET,
)

from models import (
    get_appointment_by_id,
    log_call,
    update_call_log,
)

router = APIRouter()

twilio_client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)


@router.get("/call-patient", response_class=HTMLResponse)
def call_patient(appointmentId: str, token: str | None = None):
    """
    Google Chat button will call this endpoint.

    Example:
    /call-patient?appointmentId=12345&token=SECRET
    """

    # Basic protection for Google Chat button URL
    if token != CALL_BUTTON_SECRET:
        raise HTTPException(status_code=403, detail="Invalid call token")

    appointment = get_appointment_by_id(appointmentId)

    if not appointment:
        raise HTTPException(
            status_code=404,
            detail=f"Appointment not found: {appointmentId}"
        )

    patient_phone = appointment.get("phone")

    if not patient_phone:
        raise HTTPException(
            status_code=404,
            detail=f"No phone found for appointment: {appointmentId}"
        )

    call = twilio_client.calls.create(
        to=SCANX_STAFF_NUMBER,
        from_=TWILIO_PHONE,
        url=f"{BASE_URL}/twilio/connect-patient?appointmentId={appointmentId}",
        method="POST",
        status_callback=f"{BASE_URL}/twilio/call-status",
        status_callback_method="POST",
        status_callback_event=["initiated", "ringing", "answered", "completed"],
    )

    try:
        log_call(
            appointment_id=appointmentId,
            staff_phone=SCANX_STAFF_NUMBER,
            patient_number=patient_phone,
            direction="outbound",
            call_sid=call.sid,
            status="initiated",
        )
    except Exception as e:
        print("Call log insert failed:", str(e))

    patient_name = f"{appointment.get('first_name', '')} {appointment.get('last_name', '')}".strip()

    return """
    <html>
      <head>
        <title>ScanX Call</title>
        <meta name="viewport" content="width=device-width, initial-scale=1" />
        <script>
          setTimeout(function () {
            window.close();
          }, 3000);
        </script>
      </head>
      <body style="font-family: Arial, sans-serif; padding: 32px;">
        <h2>Calling patient...</h2>
        <p>The call has been started from the ScanX clinic line.</p>
        <p>You may close this tab.</p>
      </body>
    </html>
    """


@router.post("/twilio/connect-patient")
def connect_patient(appointmentId: str):
    """
    Twilio calls this when staff answers.
    Then we tell Twilio to dial the patient.
    """

    appointment = get_appointment_by_id(appointmentId)

    response = VoiceResponse()

    if not appointment:
        response.say("Sorry, appointment details were not found.")
        response.hangup()
        return Response(content=str(response), media_type="application/xml")

    patient_phone = appointment.get("phone")

    if not patient_phone:
        response.say("Sorry, patient phone number was not found.")
        response.hangup()
        return Response(content=str(response), media_type="application/xml")

    response.say("Connecting you to the patient now.")

    dial = Dial(
        caller_id=TWILIO_PHONE,
        timeout=30,
        record="record-from-answer-dual"
    )

    dial.number(patient_phone)
    response.append(dial)

    return Response(content=str(response), media_type="application/xml")


@router.post("/twilio/call-status")
async def call_status(request: Request):
    """
    Twilio sends call status updates here.
    """

    form = await request.form()

    call_sid = form.get("CallSid")
    call_status = form.get("CallStatus")
    duration = form.get("CallDuration") or 0

    print({
        "call_sid": call_sid,
        "call_status": call_status,
        "duration": duration,
    })

    if call_sid:
        try:
            update_call_log(
                call_sid=call_sid,
                status=call_status or "unknown",
                duration=int(duration),
            )
        except Exception as e:
            print("Call log update failed:", str(e))

    return {"ok": True}