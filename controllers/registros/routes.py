# backend/tancho/registros/routes.py
import logging
from typing import List

from bson.objectid import ObjectId
from fastapi import APIRouter, Depends, HTTPException

from config.config import DB, CONF
from .models import RegistroBase, RegistroOnDB

registros_router = APIRouter()


def validate_object_id(id_: str):
    try:
        _id = ObjectId(id_)
    except Exception:
        if CONF["fastapi"].get("debug", False):
            logging.warning("Invalid Object ID")
        raise HTTPException(status_code=400)
    return _id


async def _get_or_404(id_: str):
    _id = validate_object_id(id_)
    resp = await DB.registros.find_one({"_id": _id})
    if resp:
        return fix_id(resp)
    else:
        raise HTTPException(status_code=404, detail="not found")


def fix_id(resp):
    resp["id_"] = str(resp["_id"])
    return resp


@registros_router.get("/count")
async def get_count():
    # print("qweqweqwe")
    conteo = await DB.registros.count_documents({})
    return conteo


@registros_router.get("/", response_model=List[RegistroOnDB])
async def get_all_registros(dni: int = None, limit: int = 10, skip: int = 0):
    """[summary]
    Gets all registros.

    [description]
    Endpoint to retrieve registros.
    """
    if dni is None:
        registro_cursor = DB.registros.find().skip(skip).limit(limit)
    else:
        registro_cursor = DB.registros.find({"responsable": dni}).skip(skip).limit(limit)
    registros = await registro_cursor.to_list(length=limit)
    return list(map(fix_id, registros))


#
#
# @registros_router.post("/", response_model=RegistroOnDB)
@registros_router.post("/")
async def add_registro(registro: RegistroBase):
    """[summary]
    Inserts a new user on the DB.

    [description]
    Endpoint to add a new user.
    """
    registro_op = await DB.registros.insert_one(registro.dict())
    # await DB.registros.update_one(registro.dict())
    # print(registro_op.inserted_id)
    return {"id": str(registro_op.inserted_id)}

    # if registro_op.inserted_id:
    #     registro = await _get_or_404(registro_op.inserted_id)
    #     registro["id_"] = str(registro['_id'])
    #     # print(registro)
    #     return registro
    # registro["id_"] = str(registro_op.inserted_id)
    # return registro
    # if registro_op.inserted_id:
    #     registro = await _get_or_404(registro_op.inserted_id)
    #     registro["id_"] = str(registro["_id"])
    #     return registro


#
@registros_router.get(
    "/{id_}",
    response_model=RegistroOnDB
)
async def get_registro_by_id(id_: ObjectId = Depends(validate_object_id)):
    """[summary]
    Get one registro by ID.

    [description]
    Endpoint to retrieve an specific registro.
    """
    registro = await DB.registros.find_one({"_id": id_})
    if registro:
        registro["id_"] = str(registro["_id"])
        return registro
    else:
        raise HTTPException(status_code=404, detail="not found")


#
#
@registros_router.delete(
    "/{id_}",
    dependencies=[Depends(_get_or_404)],
    response_model=dict
)
async def delete_registro_by_id(id_: str):
    """[summary]
    Get one registro by ID.

    [description]
    Endpoint to retrieve an specific registro.
    """
    registros_op = await DB.registros.delete_one({"_id": ObjectId(id_)})
    if registros_op.deleted_count:
        return {"status": f"se elimino la cuenta de: {registros_op.deleted_count}"}


#
#
@registros_router.put(
    "/{id_}",
    dependencies=[Depends(validate_object_id), Depends(_get_or_404)],
    response_model=RegistroOnDB
)
async def update_registro(id_: str, registro_data: dict):
    """[summary]
    Update a registro by ID.

    [description]
    Endpoint to update an specific registro with some or all fields.
    """
    registro_op = await DB.registros.update_one(
        {"_id": ObjectId(id_)}, {"$set": registro_data}
    )
    if registro_op.modified_count:
        return await _get_or_404(id_)
    else:
        raise HTTPException(status_code=304)
