import os
from flask import Flask
from dotenv import load_dotenv
from werkzeug.security import generate_password_hash

from src import create_app, db
from src.api_users.models import Users

load_dotenv()

def seed_users():
    """Seeds the users table with initial data."""
    app = create_app(os.getenv("CONFIG_MODE"))
    with app.app_context():
        print("Seeding database...")
        
        
        try:
            users = [
                Users(
                    rfid_tag= "mock_rfid_12345",
                    first_name="Isaac1",
                    middle_name="Isaac",
                    last_name="Isaac",
                    contact_num="09123456789",
                    address="St. Michael",
                    email="Isaacbulugan1@example.com",
                    password=generate_password_hash("admin123"),
                    type_id=1,
                    level_id=1,
                    section_id=1,
                    strand_id=1,
                ),
                Users(
                    rfid_tag= "mock_rfid_22345",
                    first_name="Isaac2",
                    middle_name="Isaac",
                    last_name="Isaac",
                    contact_num="09223456789",
                    address="St. Michael",
                    email="Isaacbulugan2@example.com",
                    password=generate_password_hash("admin123"),
                    type_id=1,
                    level_id=1,
                    section_id=2,
                    strand_id=2,
                ),
                Users(
                    rfid_tag= "mock_rfid_32345",
                    first_name="Isaac3",
                    middle_name="Isaac",
                    last_name="Isaac",
                    contact_num="09323456789",
                    address="St. Michael",
                    email="Isaacbulugan3@example.com",
                    password=generate_password_hash("admin123"),
                    type_id=1,
                    level_id=1,
                    section_id=3,
                    strand_id=3,
                ),
                Users(
                    rfid_tag= "mock_rfid_42345",
                    first_name="Isaac4",
                    middle_name="Isaac",
                    last_name="Isaac",
                    contact_num="09423456789",
                    address="St. Michael",
                    email="Isaacbulugan4@example.com",
                    password=generate_password_hash("admin123"),
                    type_id=1,
                    level_id=2,
                    section_id=4,
                    strand_id=1,
                ),
                Users(
                    rfid_tag= "mock_rfid_52345",
                    first_name="Isaac5",
                    middle_name="Isaac",
                    last_name="Isaac",
                    contact_num="09523456789",
                    address="St. Michael",
                    email="Isaacbulugan5@example.com",
                    password=generate_password_hash("admin123"),
                    type_id=1,
                    level_id=2,
                    section_id=5,
                    strand_id=2,
                ),
                Users(
                    rfid_tag= "mock_rfid_62345",
                    first_name="Isaac6",
                    middle_name="Isaac",
                    last_name="Isaac",
                    contact_num="09623456789",
                    address="St. Michael",
                    email="Isaacbulugan6@example.com",
                    password=generate_password_hash("admin123"),
                    type_id=1,
                    level_id=2,
                    section_id=6,
                    strand_id=3,
                ),
                Users(
                    rfid_tag= "mock_rfid_72345",
                    first_name="Isaac7",
                    middle_name="Isaac",
                    last_name="Isaac",
                    contact_num="09723456789",
                    address="St. Michael",
                    email="Isaacbulugan7@example.com",
                    password=generate_password_hash("admin123"),
                    type_id=2,
                    level_id=None,
                    section_id=None,
                    strand_id=None,
                ),
                Users(
                    rfid_tag= "mock_rfid_82345",
                    first_name="Isaac8",
                    middle_name="Isaac",
                    last_name="Isaac",
                    contact_num="09823456789",
                    address="St. Michael",
                    email="Isaacbulugan8@example.com",
                    password=generate_password_hash("admin123"),
                    type_id=3,
                    level_id=None,
                    section_id=None,
                    strand_id=None,
                ),
                Users(
                    rfid_tag= "mock_rfid_92345",
                    first_name="Isaac9",
                    middle_name="Isaac",
                    last_name="Isaac",
                    contact_num="09923456789",
                    address="St. Michael",
                    email="Isaacbulugan9@example.com",
                    password=generate_password_hash("admin123"),
                    type_id=4,
                    level_id=None,
                    section_id=None,
                    strand_id=None,
                ),
            ]


            db.session.add_all(users)
            db.session.commit()
            print("Users table seeded successfully!")
        except Exception as e:
            db.session.rollback()
            print(f"Error while seeding users: {e}")


def run_users():
    """Runs all seeding functions."""
    print("🔄 Seeding database...")
    seed_users()
    print("Database seeding complete!")


if __name__ == "__main__":
    seed_users()
    print("Database seeding complete!")
