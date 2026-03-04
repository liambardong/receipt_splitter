from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from typing import List

from database import get_db
from models import Person, User, Receipt, ReceiptParticipants
from schemas import UserCreate, UserResponse, ReceiptResponse
from logging import Logger

logger = Logger(__name__)
router = APIRouter(prefix="/users", tags=["Users"])


@router.post("", response_model=UserResponse)
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    existing = db.query(User).filter(User.email == user.email).first()
    if existing:
        logger.warning("409 User already exists", email=user.email)
        raise HTTPException(status_code=409, detail="User with this email already exists")
    db_person = Person(first_name="Me", last_name=None)
    db.add(db_person)
    db.flush()
    db_user = User(email=user.email, person_id=db_person.id)
    db.add(db_user)
    try:
        db.commit()
        db.refresh(db_user)
    except IntegrityError:
        db.rollback()
        logger.warning("409 User already exists (integrity)", email=user.email)
        raise HTTPException(status_code=409, detail="User with this email already exists")
    logger.info("User created", user_id=db_user.id, email=db_user.email)
    return UserResponse.model_validate(db_user)


@router.get("", response_model=List[UserResponse])
def get_users(db: Session = Depends(get_db)):
    users = db.query(User).all()
    return [UserResponse.model_validate(u) for u in users]


@router.get("/{user_id}", response_model=UserResponse)
def get_user(user_id: str, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.id == user_id).first()
    if not db_user:
        logger.warning("404 User not found", user_id=user_id)
        raise HTTPException(status_code=404, detail="User not found")
    return UserResponse.model_validate(db_user)


@router.delete("/{user_id}")
def delete_user(user_id: str, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.id == user_id).first()
    if not db_user:
        logger.warning("404 User not found", user_id=user_id)
        raise HTTPException(status_code=404, detail="User not found")
    db.delete(db_user)
    db.commit()
    logger.info("User deleted", user_id=user_id)
    return {"status": "success"}


@router.get("/{user_id}/receipts", response_model=List[ReceiptResponse])
def get_user_receipts(user_id: str, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.id == user_id).first()
    if not db_user:
        logger.warning("404 User not found", user_id=user_id)
        raise HTTPException(status_code=404, detail="User not found")
    if not db_user.person_id:
        return []
    receipts = (
        db.query(Receipt)
        .join(ReceiptParticipants, Receipt.id == ReceiptParticipants.receipt_id)
        .filter(ReceiptParticipants.person_id == db_user.person_id)
        .distinct()
        .all()
    )
    result = [ReceiptResponse.model_validate(r) for r in receipts]
    logger.info("User receipts listed", user_id=user_id, count=len(result))
    return result
