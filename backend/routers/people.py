from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from typing import List

from database import get_db
from models import Person
from schemas import PersonCreate, PersonResponse

router = APIRouter(prefix="/people", tags=["People"])


@router.post("", response_model=PersonResponse)
def create_person(person: PersonCreate, db: Session = Depends(get_db)):
    existing = db.query(Person).filter(
        Person.first_name == person.first_name,
        Person.last_name == person.last_name,
    ).first()
    if existing:
        raise HTTPException(status_code=409, detail="Person with this first and last name already exists")
    db_person = Person(first_name=person.first_name, last_name=person.last_name)
    db.add(db_person)
    try:
        db.commit()
        db.refresh(db_person)
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=409, detail="Person with this first and last name already exists")
    return PersonResponse.model_validate(db_person)


@router.get("", response_model=List[PersonResponse])
def get_people(db: Session = Depends(get_db)):
    people = db.query(Person).all()
    return [PersonResponse.model_validate(p) for p in people]


@router.get("/{person_id}", response_model=PersonResponse)
def get_person(person_id: str, db: Session = Depends(get_db)):
    db_person = db.query(Person).filter(Person.id == person_id).first()
    if not db_person:
        raise HTTPException(status_code=404, detail="Person not found")
    return PersonResponse.model_validate(db_person)


@router.delete("/{person_id}")
def delete_person(person_id: str, db: Session = Depends(get_db)):
    db_person = db.query(Person).filter(Person.id == person_id).first()
    if not db_person:
        raise HTTPException(status_code=404, detail="Person not found")
    db.delete(db_person)
    db.commit()
    return {"status": "success"}
