from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from typing import List

from database import get_db
from models import Person
from schemas import PersonCreate, PersonResponse
from logging import Logger

logger = Logger(__name__)
router = APIRouter(prefix="/people", tags=["People"])


@router.post("", response_model=PersonResponse)
def create_person(person: PersonCreate, db: Session = Depends(get_db)):
    existing = db.query(Person).filter(
        Person.first_name == person.first_name,
        Person.last_name == person.last_name,
    ).first()
    if existing:
        logger.warning(
            "409 Person already exists",
            first_name=person.first_name,
            last_name=person.last_name,
        )
        raise HTTPException(status_code=409, detail="Person with this first and last name already exists")
    db_person = Person(first_name=person.first_name, last_name=person.last_name)
    db.add(db_person)
    try:
        db.commit()
        db.refresh(db_person)
    except IntegrityError:
        db.rollback()
        logger.warning(
            "409 Person already exists (integrity)",
            first_name=person.first_name,
            last_name=person.last_name,
        )
        raise HTTPException(status_code=409, detail="Person with this first and last name already exists")
    logger.info(
        "Person created",
        person_id=db_person.id,
        first_name=db_person.first_name,
        last_name=db_person.last_name,
    )
    return PersonResponse.model_validate(db_person)


@router.get("", response_model=List[PersonResponse])
def get_people(db: Session = Depends(get_db)):
    people = db.query(Person).all()
    return [PersonResponse.model_validate(p) for p in people]


@router.get("/{person_id}", response_model=PersonResponse)
def get_person(person_id: str, db: Session = Depends(get_db)):
    db_person = db.query(Person).filter(Person.id == person_id).first()
    if not db_person:
        logger.warning("404 Person not found", person_id=person_id)
        raise HTTPException(status_code=404, detail="Person not found")
    return PersonResponse.model_validate(db_person)


@router.delete("/{person_id}")
def delete_person(person_id: str, db: Session = Depends(get_db)):
    db_person = db.query(Person).filter(Person.id == person_id).first()
    if not db_person:
        logger.warning("404 Person not found", person_id=person_id)
        raise HTTPException(status_code=404, detail="Person not found")
    db.delete(db_person)
    db.commit()
    logger.info("Person deleted", person_id=person_id)
    return {"status": "success"}
