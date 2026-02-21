import os
import time

import pyotp
from fastapi import FastAPI, HTTPException
import io
import base64
import qrcode

from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

app = FastAPI()

origins = [
    "*"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

SECRET_KEY = pyotp.random_base32()


@app.get("/generate-qr")
def get_qr():
    totp = pyotp.TOTP(SECRET_KEY, interval=120)

    current_token = totp.now()

    url_env = os.environ.get("FRONTEND_URL")
    if not url_env:
        url_env = "http://127.0.0.1:8000"

    frontend_url = f"{url_env}/verify"
    contenido_qr = f"{frontend_url}?token={current_token}"

    img = qrcode.make(contenido_qr)

    buf = io.BytesIO()
    img.save(buf, format="PNG")
    img_str = base64.b64encode(buf.getvalue()).decode()

    return {
        "qr_image": img_str,
        "token": current_token,
        "seconds_remaining": totp.interval - (time.time() % totp.interval)
    }


class AttendanceRequest(BaseModel):
    student_id: str
    token: str


@app.post("/verify-attendance")
def verify_attendance(data: AttendanceRequest):
    totp = pyotp.TOTP(SECRET_KEY, interval=120)

    is_valid = totp.verify(data.token, valid_window=1)

    if is_valid:
        print(f"Attendance recorded for: {data.student_id}")
        return {"status": "success", "message": f"Welcome, {data.student_id}"}
    else:
        raise HTTPException(status_code=400, detail="Invalid or expired code")
