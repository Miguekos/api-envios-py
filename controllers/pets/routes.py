# backend/tancho/pets/routes.py

from bson.objectid import ObjectId
from config.config import DB, CONF
from fastapi import APIRouter, Depends, HTTPException
from typing import List
import logging

from .models import PetBase, PetOnDB, PetKind


pets_router = APIRouter()


def validate_object_id(id_: str):
    try:
        _id = ObjectId(id_)
    except Exception:
        if CONF["fastapi"].get("debug", False):
            logging.warning("Invalid Object ID")
        raise HTTPException(status_code=400)
    return _id


async def _get_pet_or_404(id_: str):
    _id = validate_object_id(id_)
    pet = await DB.pet.find_one({"_id": _id})
    if pet:
        return fix_pet_id(pet)
    else:
        raise HTTPException(status_code=404, detail="Pet not found")


def fix_pet_id(pet):
    pet["id_"] = str(pet["_id"])
    return pet


@pets_router.get("/", response_model=List[PetOnDB])
async def get_all_pets(kind: PetKind = None, limit: int = 10, skip: int = 0):
    """[summary]
    Gets all pets.

    [description]
    Endpoint to retrieve pets.
    """
    if kind is None:
        pets_cursor = DB.pet.find().skip(skip).limit(limit)
    else:
        pets_cursor = DB.pet.find({"kind": kind.value}).skip(skip).limit(limit)
    pets = await pets_cursor.to_list(length=limit)
    return list(map(fix_pet_id, pets))


@pets_router.post("/", response_model=PetOnDB)
async def add_pet(pet: PetBase):
    """[summary]
    Inserts a new pet on the DB.

    [description]
    Endpoint to add a new pet.
    """
    pet_op = await DB.pet.insert_one(pet.dict())
    if pet_op.inserted_id:
        pet = await _get_pet_or_404(pet_op.inserted_id)
        pet["id_"] = str(pet["_id"])
        pet["codRes"] = "00"
        return pet


@pets_router.get(
    "/{id_}",
    response_model=PetOnDB
)
async def get_pet_by_id(id_: ObjectId = Depends(validate_object_id)):
    """[summary]
    Get one pet by ID.

    [description]
    Endpoint to retrieve an specific pet.
    """
    pet = await DB.pet.find_one({"_id": id_})
    if pet:
        pet["id_"] = str(pet["_id"])
        return pet
    else:
        raise HTTPException(status_code=404, detail="Pet not found")


@pets_router.delete(
    "/{id_}",
    dependencies=[Depends(_get_pet_or_404)],
    response_model=dict
)
async def delete_pet_by_id(id_: str):
    """[summary]
    Get one pet by ID.

    [description]
    Endpoint to retrieve an specific pet.
    """
    pet_op = await DB.pet.delete_one({"_id": ObjectId(id_)})
    if pet_op.deleted_count:
        return {"status": f"deleted count: {pet_op.deleted_count}"}


@pets_router.put(
    "/{id_}",
    dependencies=[Depends(validate_object_id), Depends(_get_pet_or_404)],
    response_model=PetOnDB
)
async def update_pet(id_: str, pet_data: PetBase):
    """[summary]
    Update a pet by ID.

    [description]
    Endpoint to update an specific pet with some or all fields.
    """
    pet_op = await DB.pet.update_one(
        {"_id": ObjectId(id_)}, {"$set": pet_data.dict()}
    )
    if pet_op.modified_count:
        return await _get_pet_or_404(id_)
    else:
        raise HTTPException(status_code=304)
