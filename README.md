# EMotorad-Backend-Task
Assignment for Intern-Cloud &amp; Backend Development
This project is a web service designed to manage and consolidate contact information for users with multiple orders under different email addresses and phone numbers. Built using FastAPI and SQLAlchemy, the service is designed to link different purchases to the same user by tracking their contact details.

Features
Identify and Consolidate Contacts: Associates different contact details (emails, phone numbers) with a single primary contact.
Seamless Primary-Secondary Linkage: Automatically assigns primary or secondary status to contact records based on existing data.
API Response Structure: Returns a consolidated list of contact information, including emails, phone numbers, and associated secondary contacts.
Efficient Database Handling: Uses SQLAlchemy ORM for efficient database operations and management.
Technology Stack
FastAPI: For building a fast and efficient API.
SQLAlchemy: ORM for database management.
SQLite: Default database (can be replaced with PostgreSQL or others).
Requirements
Python 3.7+
FastAPI
SQLAlchemy
Pydantic
Uvicorn (for running the FastAPI server)
Install dependencies with:

bash
Copy code
pip install fastapi sqlalchemy pydantic uvicorn
Database Model
The database contains a Contact model with the following fields:

id: Unique identifier for each contact.
email: Email address of the contact.
phone_number: Phone number of the contact.
linked_id: ID of the primary contact to which a secondary contact is linked.
link_precedence: Defines whether a contact is "primary" or "secondary."
created_at: Timestamp of creation.
updated_at: Timestamp of the last update.
deleted_at: Soft delete timestamp (if the record is deleted).
API Endpoints
/identify
Method: POST
Description: Identifies or creates a consolidated contact record based on the provided email and/or phone number.

Request Body:

json
Copy code
{
  "email": "optional@example.com",
  "phone_number": "optional-phone-number"
}
Response:

primary_contact_id: ID of the primary contact.
emails: List of associated emails.
phone_numbers: List of associated phone numbers.
secondary_contact_ids: List of secondary contact IDs linked to the primary contact.
Sample Response:

json
Copy code
{
  "primary_contact_id": 1,
  "emails": ["user@example.com"],
  "phone_numbers": ["1234567890"],
  "secondary_contact_ids": [2, 3]
}
Running the Service
Start the server with:
bash
Copy code
uvicorn main:app --reload
Access the API documentation at http://127.0.0.1:8000/docs.
