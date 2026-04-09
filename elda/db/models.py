from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime, Text
from sqlalchemy.orm import relationship, declarative_base
from datetime import datetime

Base = declarative_base()


class Patient(Base):
    __tablename__ = "patients"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, default="Patient")
    age = Column(Integer, default=72)
    condition = Column(String, default="Moderate Alzheimer's")
    medical_history = Column(Text, default="Hypertension, early-stage dementia.")
    caregiver_contact = Column(String, default="caregiver@elda.ai")
    notes = Column(Text, default="Tends to get confused in the evenings.")


class Interaction(Base):
    __tablename__ = "interactions"

    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(Integer, nullable=True)
    sender = Column(String, default="Patient")           # "Patient" | "ELDA"
    content = Column(Text)                               # Patient's message / input
    response_content = Column(Text, nullable=True)       # ELDA's response
    emotion = Column(String, default="Neutral")          # detected emotion
    interaction_type = Column(String, nullable=True)     # e.g. "voice", "text"
    timestamp = Column(DateTime, default=datetime.utcnow)


class VitalsLog(Base):
    __tablename__ = "vitals_log"

    id = Column(Integer, primary_key=True, index=True)
    heart_rate = Column(Integer, nullable=True)
    oxygen = Column(Float, nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow)
