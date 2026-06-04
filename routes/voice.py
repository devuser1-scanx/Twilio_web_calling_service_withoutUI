from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import HTMLResponse, Response
from twilio.jwt.access_token import AccessToken
from twilio.jwt.access_token.grants import VoiceGrant
from twilio.twiml.voice_response import VoiceResponse, Dial

from config import (
    TWILIO_ACCOUNT_SID,
    TWILIO_API_KEY_SID,
    TWILIO_API_KEY_SECRET,
    TWILIO_TWIML_APP_SID,
    TWILIO_PHONE,
    CALL_BUTTON_SECRET,
)

from models import get_appointment_by_id, log_call, update_call_log

router = APIRouter()


@router.get("/call-page", response_class=HTMLResponse)
def call_page(appointmentId: str, token: str):
    """
    Opens on clinic tablet/browser.
    Auto-starts the call.
    Does not expose patient phone or patient details.
    """

    if token != CALL_BUTTON_SECRET:
        raise HTTPException(status_code=403, detail="Invalid call token")

    appointment = get_appointment_by_id(appointmentId)

    if not appointment:
        raise HTTPException(status_code=404, detail="Appointment not found")

    html = f"""
    <!DOCTYPE html>
    <html>
      <head>
        <title>ScanX Call</title>
        <meta name="viewport" content="width=device-width, initial-scale=1" />

        <script src="https://cdn.jsdelivr.net/npm/@twilio/voice-sdk@2.18.3/dist/twilio.min.js"></script>

        <style>
          body {{
            font-family: Arial, sans-serif;
            padding: 24px;
            background: #f7f9fb;
            margin: 0;
          }}

          .card {{
            max-width: 520px;
            margin: 40px auto;
            background: white;
            padding: 32px;
            border-radius: 14px;
            box-shadow: 0 4px 18px rgba(0,0,0,0.08);
            text-align: center;
          }}

          h2 {{
            margin-top: 0;
            font-size: 30px;
          }}

          p {{
            font-size: 18px;
          }}

          #status {{
            margin-top: 22px;
            color: #333;
            font-size: 18px;
          }}

          #hangupBtn {{
            width: 100%;
            padding: 14px;
            margin-top: 20px;
            border: none;
            border-radius: 8px;
            font-size: 17px;
            cursor: pointer;
            background: #d93025;
            color: white;
            display: none;
          }}

          .loader {{
            margin: 24px auto 0;
            width: 36px;
            height: 36px;
            border: 4px solid #e5e5e5;
            border-top: 4px solid #0b7cff;
            border-radius: 50%;
            animation: spin 1s linear infinite;
          }}

          @keyframes spin {{
            0% {{ transform: rotate(0deg); }}
            100% {{ transform: rotate(360deg); }}
          }}
        </style>
      </head>

      <body>
        <div class="card">
          <h2>ScanX Patient Call</h2>
          <p>Calling patient from this clinic tablet...</p>

          <div class="loader" id="loader"></div>

          <button id="hangupBtn">End Call</button>

          <div id="status">Preparing call...</div>
        </div>

        <script>
          let device = null;
          let activeCall = null;
          let callAlreadyStarted = false;

          const appointmentId = "{appointmentId}";
          const callToken = "{token}";

          function setStatus(message) {{
            const statusEl = document.getElementById("status");
            if (statusEl) {{
              statusEl.innerText = message;
            }}
          }}

          function showHangupButton() {{
            const hangupBtn = document.getElementById("hangupBtn");
            if (hangupBtn) {{
              hangupBtn.style.display = "block";
            }}
          }}

          function hideHangupButton() {{
            const hangupBtn = document.getElementById("hangupBtn");
            if (hangupBtn) {{
              hangupBtn.style.display = "none";
            }}
          }}

          function hideLoader() {{
            const loader = document.getElementById("loader");
            if (loader) {{
              loader.style.display = "none";
            }}
          }}

          function closeWindowAfterDelay() {{
            hideHangupButton();
            hideLoader();
            setStatus("Call ended. Closing window...");

            setTimeout(function () {{
              window.close();

              // Fallback if browser blocks window.close()
              document.body.innerHTML = `
                <div style="font-family: Arial, sans-serif; padding: 32px; text-align: center;">
                  <h2>Call ended</h2>
                  <p>You may close this tab.</p>
                </div>
              `;
            }}, 1500);
          }}

          async function setupDeviceAndStartCall() {{
            try {{
              setStatus("Preparing secure voice connection...");

              if (!window.Twilio || !window.Twilio.Device) {{
                hideLoader();
                setStatus("Twilio Voice SDK failed to load. Please refresh and try again.");
                return;
              }}

              const res = await fetch(`/voice/token?identity=clinic-tablet`);

              if (!res.ok) {{
                hideLoader();
                setStatus("Failed to get voice token.");
                return;
              }}

              const data = await res.json();

              device = new Twilio.Device(data.token, {{
                logLevel: 1
              }});

              device.on("registered", async () => {{
                if (callAlreadyStarted) {{
                  return;
                }}

                callAlreadyStarted = true;
                await startCall();
              }});

              device.on("error", (error) => {{
                console.error("Device error:", error);
                hideLoader();
                setStatus("Voice error: " + error.message);
              }});

              await device.register();

            }} catch (err) {{
              console.error("Setup error:", err);
              hideLoader();
              setStatus("Failed to prepare call: " + err.message);
            }}
          }}

          async function startCall() {{
            try {{
              if (!device) {{
                hideLoader();
                setStatus("Voice device is not ready. Please refresh and try again.");
                return;
              }}

              setStatus("Requesting microphone permission and starting call...");

              activeCall = await device.connect({{
                params: {{
                  appointmentId: appointmentId,
                  token: callToken
                }}
              }});

              setStatus("Calling patient...");

              activeCall.on("accept", () => {{
                hideLoader();
                showHangupButton();
                setStatus("Call connected.");
              }});

              activeCall.on("disconnect", () => {{
                closeWindowAfterDelay();
              }});

              activeCall.on("cancel", () => {{
                closeWindowAfterDelay();
              }});

              activeCall.on("reject", () => {{
                closeWindowAfterDelay();
              }});

              activeCall.on("error", (error) => {{
                console.error("Call error:", error);
                hideLoader();
                setStatus("Call error: " + error.message);
              }});

            }} catch (err) {{
              console.error("Start call error:", err);
              hideLoader();
              setStatus("Failed to start call: " + err.message);
            }}
          }}

          function hangupCall() {{
            if (activeCall) {{
              activeCall.disconnect();
            }} else if (device) {{
              device.disconnectAll();
            }}

            closeWindowAfterDelay();
          }}

          const hangupBtn = document.getElementById("hangupBtn");
          if (hangupBtn) {{
            hangupBtn.addEventListener("click", hangupCall);
          }}

          window.addEventListener("load", setupDeviceAndStartCall);
        </script>
      </body>
    </html>
    """

    return html


@router.get("/voice/token")
def get_voice_token(identity: str = "clinic-tablet"):
    """
    Browser/tablet calls this to get temporary Twilio Voice token.
    """

    if not all([
        TWILIO_ACCOUNT_SID,
        TWILIO_API_KEY_SID,
        TWILIO_API_KEY_SECRET,
        TWILIO_TWIML_APP_SID,
    ]):
        raise HTTPException(status_code=500, detail="Missing Twilio Voice SDK config")

    access_token = AccessToken(
        TWILIO_ACCOUNT_SID,
        TWILIO_API_KEY_SID,
        TWILIO_API_KEY_SECRET,
        identity=identity,
    )

    voice_grant = VoiceGrant(
        outgoing_application_sid=TWILIO_TWIML_APP_SID,
        incoming_allow=False,
    )

    access_token.add_grant(voice_grant)

    return {
        "identity": identity,
        "token": access_token.to_jwt(),
    }


@router.post("/voice/outgoing")
async def voice_outgoing(request: Request):
    """
    Twilio hits this URL when browser/tablet starts outbound call.
    This returns TwiML telling Twilio which patient number to dial.
    """

    form = await request.form()

    appointment_id = form.get("appointmentId")
    token = form.get("token")
    call_sid = form.get("CallSid")

    response = VoiceResponse()

    if token != CALL_BUTTON_SECRET:
        response.say("Invalid call request.")
        response.hangup()
        return Response(content=str(response), media_type="application/xml")

    if not appointment_id:
        response.say("Appointment ID is missing.")
        response.hangup()
        return Response(content=str(response), media_type="application/xml")

    appointment = get_appointment_by_id(appointment_id)

    if not appointment:
        response.say("Appointment was not found.")
        response.hangup()
        return Response(content=str(response), media_type="application/xml")

    patient_phone = appointment.get("phone")

    if not patient_phone:
        response.say("Patient phone number was not found.")
        response.hangup()
        return Response(content=str(response), media_type="application/xml")

    try:
        log_call(
            appointment_id=appointment_id,
            staff_phone="clinic-tablet",
            patient_number=patient_phone,
            direction="outbound",
            call_sid=call_sid,
            status="initiated",
        )
    except Exception as e:
        print("Call log insert failed:", str(e))

    dial = Dial(
        caller_id=TWILIO_PHONE,
        timeout=30,
        record="record-from-answer-dual",
    )

    dial.number(patient_phone)
    response.append(dial)

    return Response(content=str(response), media_type="application/xml")


@router.post("/voice/status")
async def voice_status(request: Request):
    """
    Optional status callback endpoint.
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