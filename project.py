from datetime import datetime
from enum import Enum as PyEnum
from typing import List, Optional

from fastapi import Depends, FastAPI, HTTPException
from pydantic import BaseModel
from sqlalchemy import (Column, DateTime, Enum, ForeignKey, Integer, String,
                        create_engine)
from sqlalchemy.orm import (Session, declarative_base, relationship,
                            sessionmaker)

# Database setup
DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# LinkPrecedence Enum
class LinkPrecedence(PyEnum):
    PRIMARY = "primary"
    SECONDARY = "secondary"

# Contact Model
class Contact(Base):
    __tablename__ = "contacts"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, nullable=True)
    phone_number = Column(String, nullable=True)
    linked_id = Column(Integer, ForeignKey("contacts.id"), nullable=True)
    link_precedence = Column(Enum(LinkPrecedence), default=LinkPrecedence.PRIMARY)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    deleted_at = Column(DateTime, nullable=True)

# Initialize database
Base.metadata.create_all(bind=engine)

# FastAPI App Initialization
app = FastAPI()

# Contact payload for request
class ContactPayload(BaseModel):
    email: Optional[str] = None
    phone_number: Optional[str] = None

# Response Model
class ContactResponse(BaseModel):
    primary_contact_id: int
    emails: List[str]
    phone_numbers: List[str]
    secondary_contact_ids: List[int]

# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Utility function to find existing contacts
def get_contact_by_email_or_phone(db: Session, email: str, phone_number: str):
    return db.query(Contact).filter(
        (Contact.email == email) | (Contact.phone_number == phone_number),
        Contact.deleted_at == None
    ).all()

@app.post("/identify", response_model=ContactResponse)
def identify_contact(payload: ContactPayload, db: Session = Depends(get_db)):
    # Step 1: Find existing contact(s) based on email or phone number
    existing_contacts = get_contact_by_email_or_phone(db, payload.email, payload.phone_number)

    if not existing_contacts:
        # Step 2: No match found; create a new primary contact
        new_contact = Contact(
            email=payload.email,
            phone_number=payload.phone_number,
            link_precedence=LinkPrecedence.PRIMARY
        )
        db.add(new_contact)
        db.commit()
        db.refresh(new_contact)

        return ContactResponse(
            primary_contact_id=new_contact.id,
            emails=[payload.email] if payload.email else [],
            phone_numbers=[payload.phone_number] if payload.phone_number else [],
            secondary_contact_ids=[]
        )

    # Step 3: Match found; consolidate contacts
    primary_contact = min(existing_contacts, key=lambda c: c.created_at)
    secondary_ids = []
    emails, phone_numbers = set(), set()

    for contact in existing_contacts:
        if contact.link_precedence == LinkPrecedence.SECONDARY or contact.id != primary_contact.id:
            contact.linked_id = primary_contact.id
            contact.link_precedence = LinkPrecedence.SECONDARY
            secondary_ids.append(contact.id)
        
        if contact.email:
            emails.add(contact.email)
        if contact.phone_number:
            phone_numbers.add(contact.phone_number)
        
    db.commit()

    # Ensure new info is linked as secondary contact if new
    if payload.email and payload.email not in emails:
        new_secondary_contact = Contact(
            email=payload.email,
            linked_id=primary_contact.id,
            link_precedence=LinkPrecedence.SECONDARY
        )
        db.add(new_secondary_contact)
        db.commit()
        db.refresh(new_secondary_contact)
        secondary_ids.append(new_secondary_contact.id)
        emails.add(payload.email)

    if payload.phone_number and payload.phone_number not in phone_numbers:
        new_secondary_contact = Contact(
            phone_number=payload.phone_number,
            linked_id=primary_contact.id,
            link_precedence=LinkPrecedence.SECONDARY
        )
        db.add(new_secondary_contact)
        db.commit()
        db.refresh(new_secondary_contact)
        secondary_ids.append(new_secondary_contact.id)
        phone_numbers.add(payload.phone_number)

    return ContactResponse(
        primary_contact_id=primary_contact.id,
        emails=list(emails),
        phone_numbers=list(phone_numbers),
        secondary_contact_ids=secondary_ids
    )
