import os
from dotenv import load_dotenv
from src import create_app, db
from src.api_users.models import UserTypes, Levels, Sections, Strands

load_dotenv()


def seed_attrib():
    """Seeds the users table with initial data."""
    app = create_app(os.getenv("CONFIG_MODE"))
    with app.app_context():
        print("Seeding database...")

        try:
            user_types = [
                UserTypes(type_name="Student"),
                UserTypes(type_name="Faculty"),
                UserTypes(type_name="Administrator"),
                UserTypes(type_name="Staff"),
            ]
            student_levels = [
                Levels(level_name="11"),
                Levels(level_name="12"),
            ]

            student_sections = [
                Sections(section_name="OBEDIENCE"),
                Sections(section_name="COMPASSION"),
                Sections(section_name="HUMILITY"),
                Sections(section_name="BENEVOLENCE"),
                Sections(section_name="DILIGENCE"),
                Sections(section_name="INTEGRITY"),
            ]

            student_strands = [
                Strands(strand_name="STEM"),
                Strands(strand_name="HUMMS"),
                Strands(strand_name="ABM"),
            ]

            db.session.add_all(user_types)
            db.session.add_all(student_levels)
            db.session.add_all(student_sections)
            db.session.add_all(student_strands)
            db.session.commit()
            print("UserTypes table seeded successfully!")
        except Exception as e:
            db.session.rollback()
            print(f"Error while seeding UserTypes: {e}")


def run_attrib():
    """Runs all seeding functions."""
    print("🔄 Seeding database...")
    seed_attrib()
    print("✅ Database seeding complete!")


if __name__ == "__main__":
    run_attrib()
