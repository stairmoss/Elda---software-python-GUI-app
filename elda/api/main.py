from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
import os

from elda.api import auth, patient_api, caregiver_api, doctor_api

app = FastAPI(title="ELDA API", version="0.1.0")



app.include_router(auth.router, prefix="/auth", tags=["Auth"])
app.include_router(patient_api.router, prefix="/patient", tags=["Patient"])
app.include_router(caregiver_api.router, prefix="/caregiver", tags=["Caregiver"])
app.include_router(doctor_api.router, prefix="/doctor", tags=["Doctor"])

@app.get("/")
async def root():
    return {"message": "ELDA Backend is Running"}
