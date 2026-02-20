from datetime import datetime
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session, joinedload
from typing import List

from database import get_db
from models import Receipt, Item, Person, ReceiptParticipants, ItemAssignment
from schemas import (
    ReceiptCreate,
    ReceiptResponse,
    ParticipantAdd,
    ParticipantUpdate,
    ParticipantResponse,
    PersonResponse,
    ItemCreate,
    ItemResponse,
    AssignmentAdd,
    AssignmentResponse,
)

from logging import Logger

logger = Logger(__name__)

router = APIRouter(prefix="/receipts", tags=["Receipts"])


# ---- Receipt CRUD ----
@router.post("", response_model=ReceiptResponse)
def create_receipt(receipt: ReceiptCreate, db: Session = Depends(get_db)):
    db_receipt = Receipt(
        name=receipt.name,
        date=receipt.date,
        tax_amount=receipt.tax_amount,
        tip_amount=receipt.tip_amount,
        tax_split_method=receipt.tax_split_method,
    )
    db.add(db_receipt)
    db.commit()
    db.refresh(db_receipt)
    logger.info("Receipt Created", receipt_id=db_receipt.id)
    return ReceiptResponse.model_validate(db_receipt)


@router.get("", response_model=List[ReceiptResponse])
def get_receipts(db: Session = Depends(get_db)):
    receipts = db.query(Receipt).all()
    return [ReceiptResponse.model_validate(r) for r in receipts]


@router.get("/{receipt_id}", response_model=ReceiptResponse)
def get_receipt(receipt_id: str, db: Session = Depends(get_db)):
    db_receipt = db.query(Receipt).filter(Receipt.id == receipt_id).first()
    if not db_receipt:
        logger.warning("404 Receipt not found", receipt_id=receipt_id)
        raise HTTPException(status_code=404, detail="Receipt not found")
    return ReceiptResponse.model_validate(db_receipt)


@router.delete("/{receipt_id}")
def delete_receipt(receipt_id: str, db: Session = Depends(get_db)):
    db_receipt = db.query(Receipt).filter(Receipt.id == receipt_id).first()
    if not db_receipt:
        logger.warning("404 Receipt not found", receipt_id=receipt_id)
        raise HTTPException(status_code=404, detail="Receipt not found")
    db.delete(db_receipt)
    db.commit()
    logger.info("Receipt deleted", receipt_id=receipt_id)
    return {"status": "success"}


# ---- Participants ----
@router.post("/{receipt_id}/participants", response_model=ParticipantResponse)
def add_participant(receipt_id: str, body: ParticipantAdd, db: Session = Depends(get_db)):
    receipt = db.query(Receipt).filter(Receipt.id == receipt_id).first()
    if not receipt:
        error_message="Receipt not found"
        logger.error("404 Error", details=error_message)
        raise HTTPException(status_code=404, detail=error_message)
    person = db.query(Person).filter(Person.id == body.person_id).first()
    if not person:
        error_message = "Person not found"
        logger.error("404 Error", detail=error_message)
        raise HTTPException(status_code=404, detail=error_message)
    existing = db.query(ReceiptParticipants).filter(
        ReceiptParticipants.receipt_id == receipt_id,
        ReceiptParticipants.person_id == body.person_id,
    ).first()
    if existing:
        error_message = "Person already on this receipt"
        logger.error("400 Error", detail=error_message)
        raise HTTPException(status_code=400, detail=error_message)
    rp = ReceiptParticipants(receipt_id=receipt_id, person_id=body.person_id)
    db.add(rp)
    db.commit()
    logger.info("Added Participant to Receipt", receipt_id=receipt.id, person_id=body.person_id)
    return ParticipantResponse(person=PersonResponse.model_validate(person), paid=rp.paid, paid_at=rp.paid_at)


@router.get("/{receipt_id}/participants", response_model=List[ParticipantResponse])
def get_participants(receipt_id: str, db: Session = Depends(get_db)):
    receipt = (
        db.query(Receipt)
        .options(joinedload(Receipt.participants).joinedload(ReceiptParticipants.person))
        .filter(Receipt.id == receipt_id)
        .first()
    )
    if not receipt:
        logger.warning("404 Receipt not found", receipt_id=receipt_id)
        raise HTTPException(status_code=404, detail="Receipt not found")
    return [
        ParticipantResponse(
            person=PersonResponse.model_validate(rp.person),
            paid=rp.paid,
            paid_at=rp.paid_at,
        )
        for rp in receipt.participants
    ]


@router.patch("/{receipt_id}/participants/{person_id}", response_model=ParticipantResponse)
def update_participant(
    receipt_id: str, person_id: str, body: ParticipantUpdate, db: Session = Depends(get_db)
):
    rp = (
        db.query(ReceiptParticipants)
        .options(joinedload(ReceiptParticipants.person))
        .filter(
            ReceiptParticipants.receipt_id == receipt_id,
            ReceiptParticipants.person_id == person_id,
        )
        .first()
    )
    if not rp:
        logger.warning("404 Participant not found", receipt_id=receipt_id, person_id=person_id)
        raise HTTPException(status_code=404, detail="Participant not found on this receipt")
    rp.paid = body.paid
    rp.paid_at = datetime.utcnow() if body.paid else None
    db.commit()
    db.refresh(rp)
    logger.info("Participant updated", receipt_id=receipt_id, person_id=person_id, paid=body.paid)
    return ParticipantResponse(
        person=PersonResponse.model_validate(rp.person),
        paid=rp.paid,
        paid_at=rp.paid_at,
    )


@router.delete("/{receipt_id}/participants/{person_id}")
def remove_participant(receipt_id: str, person_id: str, db: Session = Depends(get_db)):
    rp = db.query(ReceiptParticipants).filter(
        ReceiptParticipants.receipt_id == receipt_id,
        ReceiptParticipants.person_id == person_id,
    ).first()
    if not rp:
        logger.warning("404 Participant not found", receipt_id=receipt_id, person_id=person_id)
        raise HTTPException(status_code=404, detail="Participant not found on this receipt")
    db.delete(rp)
    db.commit()
    logger.info("Participant removed", receipt_id=receipt_id, person_id=person_id)
    return {"status": "removed"}


# ---- Items ----
@router.post("/{receipt_id}/items", response_model=ItemResponse)
def create_item(receipt_id: str, item: ItemCreate, db: Session = Depends(get_db)):
    receipt = db.query(Receipt).filter(Receipt.id == receipt_id).first()
    if not receipt:
        logger.warning("404 Receipt not found", receipt_id=receipt_id)
        raise HTTPException(status_code=404, detail="Receipt not found")
    db_item = Item(
        name=item.name,
        receipt_id=receipt_id,
        unit_price=item.unit_price,
        quantity=item.quantity,
        notes=item.notes,
    )
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    logger.info("Item created", receipt_id=receipt_id, item_id=db_item.id)
    return ItemResponse.model_validate(db_item)


@router.get("/{receipt_id}/items", response_model=List[ItemResponse])
def get_items(receipt_id: str, db: Session = Depends(get_db)):
    db_items = db.query(Item).filter(Item.receipt_id == receipt_id).all()
    return [ItemResponse.model_validate(i) for i in db_items]


@router.get("/{receipt_id}/items/{item_id}", response_model=ItemResponse)
def get_item(receipt_id: str, item_id: str, db: Session = Depends(get_db)):
    db_item = db.query(Item).filter(Item.id == item_id, Item.receipt_id == receipt_id).first()
    if not db_item:
        logger.warning("404 Item not found", receipt_id=receipt_id, item_id=item_id)
        raise HTTPException(status_code=404, detail="Item not found")
    return ItemResponse.model_validate(db_item)


# ---- Item assignments ----
@router.post("/{receipt_id}/items/{item_id}/assignments", response_model=AssignmentResponse)
def add_item_assignment(
    receipt_id: str, item_id: str, body: AssignmentAdd, db: Session = Depends(get_db)
):
    item = db.query(Item).filter(Item.id == item_id, Item.receipt_id == receipt_id).first()
    if not item:
        logger.warning("404 Item not found", receipt_id=receipt_id, item_id=item_id)
        raise HTTPException(status_code=404, detail="Item not found")
    person = db.query(Person).filter(Person.id == body.person_id).first()
    if not person:
        logger.warning("404 Person not found", person_id=body.person_id)
        raise HTTPException(status_code=404, detail="Person not found")
    participant = db.query(ReceiptParticipants).filter(
        ReceiptParticipants.receipt_id == receipt_id,
        ReceiptParticipants.person_id == body.person_id,
    ).first()
    if not participant:
        logger.error(
            "400 Person must be participant before assignment",
            receipt_id=receipt_id,
            person_id=body.person_id,
        )
        raise HTTPException(
            status_code=400,
            detail="Person must be a participant on this receipt before being assigned to an item",
        )
    existing = db.query(ItemAssignment).filter(
        ItemAssignment.item_id == item_id,
        ItemAssignment.person_id == body.person_id,
    ).first()
    if existing:
        logger.error(
            "400 Person already assigned to item",
            item_id=item_id,
            person_id=body.person_id,
        )
        raise HTTPException(status_code=400, detail="Person already assigned to this item")
    assignment = ItemAssignment(item_id=item_id, person_id=body.person_id)
    db.add(assignment)
    db.commit()
    db.refresh(assignment)
    assignment.person = person
    logger.info(
        "Item assignment added",
        receipt_id=receipt_id,
        item_id=item_id,
        person_id=body.person_id,
    )
    return AssignmentResponse.model_validate(assignment)


@router.get("/{receipt_id}/items/{item_id}/assignments", response_model=List[AssignmentResponse])
def get_item_assignments(receipt_id: str, item_id: str, db: Session = Depends(get_db)):
    item = db.query(Item).filter(Item.id == item_id, Item.receipt_id == receipt_id).first()
    if not item:
        logger.warning("404 Item not found", receipt_id=receipt_id, item_id=item_id)
        raise HTTPException(status_code=404, detail="Item not found")
    assignments = (
        db.query(ItemAssignment)
        .options(joinedload(ItemAssignment.person))
        .filter(ItemAssignment.item_id == item_id)
        .all()
    )
    return [AssignmentResponse.model_validate(a) for a in assignments]


@router.delete("/{receipt_id}/items/{item_id}/assignments/{person_id}")
def remove_item_assignment(
    receipt_id: str, item_id: str, person_id: str, db: Session = Depends(get_db)
):
    item = db.query(Item).filter(Item.id == item_id, Item.receipt_id == receipt_id).first()
    if not item:
        logger.warning("404 Item not found", receipt_id=receipt_id, item_id=item_id)
        raise HTTPException(status_code=404, detail="Item not found")
    assignment = db.query(ItemAssignment).filter(
        ItemAssignment.item_id == item_id,
        ItemAssignment.person_id == person_id,
    ).first()
    if not assignment:
        logger.warning(
            "404 Assignment not found",
            receipt_id=receipt_id,
            item_id=item_id,
            person_id=person_id,
        )
        raise HTTPException(status_code=404, detail="Assignment not found")
    db.delete(assignment)
    db.commit()
    logger.info(
        "Item assignment removed",
        receipt_id=receipt_id,
        item_id=item_id,
        person_id=person_id,
    )
    return {"status": "removed"}


@router.get("/{receipt_id}/assignments", response_model=List[AssignmentResponse])
def get_receipt_assignments(receipt_id: str, db: Session = Depends(get_db)):
    receipt = db.query(Receipt).filter(Receipt.id == receipt_id).first()
    if not receipt:
        logger.warning("404 Receipt not found", receipt_id=receipt_id)
        raise HTTPException(status_code=404, detail="Receipt not found")
    assignments = (
        db.query(ItemAssignment)
        .join(Item, ItemAssignment.item_id == Item.id)
        .options(joinedload(ItemAssignment.person))
        .filter(Item.receipt_id == receipt_id)
        .all()
    )
    return [AssignmentResponse.model_validate(a) for a in assignments]
