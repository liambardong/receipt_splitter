"""
Seed the SQLite database with sample data for testing endpoints.
Run from the backend directory (use venv): ./venv/bin/python seed_db.py
"""
import os
from datetime import date

# Ensure we use the same DB as the app (run from backend dir)
os.chdir(os.path.dirname(os.path.abspath(__file__)))

from database import engine, Base, SessionLocal
from models import Person, User, Receipt, Item, ReceiptParticipants, ItemAssignment


def seed():
    # Drop and recreate all tables so schema is current
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

    db = SessionLocal()

    # People (standalone + "Me" for users)
    me1 = Person(first_name="Me", last_name=None)
    db.add(me1)
    db.flush()

    me2 = Person(first_name="Me", last_name=None)
    db.add(me2)
    db.flush()

    alice = Person(first_name="Alice", last_name="Smith")
    db.add(alice)
    db.flush()

    bob = Person(first_name="Bob", last_name="Jones")
    db.add(bob)
    db.flush()

    # Users (each linked to a "Me" person)
    user1 = User(email="test@example.com", person_id=me1.id)
    user2 = User(email="demo@example.com", person_id=me2.id)
    db.add_all([user1, user2])
    db.flush()

    # Receipts
    dinner = Receipt(
        name="Dinner at Mario's",
        date=date(2025, 2, 10),
        tax_amount=8.50,
        tip_amount=15.00,
        tax_split_method="proportional",
    )
    db.add(dinner)
    db.flush()

    groceries = Receipt(
        name="Weekly groceries",
        date=date(2025, 2, 9),
        tax_amount=3.20,
        tip_amount=0,
        tax_split_method="proportional",
    )
    db.add(groceries)
    db.flush()

    # Items on dinner receipt
    item1 = Item(receipt_id=dinner.id, name="Margherita Pizza", unit_price=14.99, quantity=1, notes=None)
    item2 = Item(receipt_id=dinner.id, name="Caesar Salad", unit_price=9.50, quantity=2, notes="split")
    item3 = Item(receipt_id=dinner.id, name="Soda", unit_price=2.50, quantity=3, notes=None)
    db.add_all([item1, item2, item3])
    db.flush()

    # Items on groceries receipt
    item4 = Item(receipt_id=groceries.id, name="Milk", unit_price=4.99, quantity=1, notes=None)
    item5 = Item(receipt_id=groceries.id, name="Bread", unit_price=3.49, quantity=2, notes=None)
    db.add_all([item4, item5])
    db.flush()

    # Participants on dinner receipt (Me1, Alice, Bob)
    db.add_all([
        ReceiptParticipants(receipt_id=dinner.id, person_id=me1.id),
        ReceiptParticipants(receipt_id=dinner.id, person_id=alice.id),
        ReceiptParticipants(receipt_id=dinner.id, person_id=bob.id),
    ])
    db.flush()

    # Participants on groceries (Me1, Alice)
    db.add_all([
        ReceiptParticipants(receipt_id=groceries.id, person_id=me1.id),
        ReceiptParticipants(receipt_id=groceries.id, person_id=alice.id),
    ])
    db.flush()

    # Sample item assignments (who owes what for dinner)
    db.add_all([
        ItemAssignment(item_id=item1.id, person_id=me1.id),
        ItemAssignment(item_id=item2.id, person_id=me1.id),
        ItemAssignment(item_id=item2.id, person_id=alice.id),
        ItemAssignment(item_id=item3.id, person_id=me1.id),
        ItemAssignment(item_id=item3.id, person_id=alice.id),
        ItemAssignment(item_id=item3.id, person_id=bob.id),
    ])

    db.commit()
    db.close()

    print("Database seeded successfully.")
    print("  People: 4 (2 'Me', Alice Smith, Bob Jones)")
    print("  Users: 2 (test@example.com, demo@example.com)")
    print("  Receipts: 2 (Dinner at Mario's, Weekly groceries)")
    print("  Items: 5 (3 on dinner, 2 on groceries)")
    print("  Participants and item assignments added.")
    print(f"  DB file: {os.path.abspath('receipt_splitter.db')}")


if __name__ == "__main__":
    seed()
