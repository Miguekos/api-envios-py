# backend/tancho/registros/routes.py
import logging
from datetime import datetime
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


def formatDate(v):
    import pytz
    lima = pytz.timezone('America/Lima')
    fehcaEvaluarTest = v
    # tz = pytz.timezone('America/St_Johns')
    fehcaEvaluarTest = fehcaEvaluarTest.replace(tzinfo=pytz.UTC)
    fehcaEvaluar = fehcaEvaluarTest.astimezone(lima)
    # print("fehcaEvaluar")
    # print(fehcaEvaluar)
    # print(datetime.now(lima))
    # return v or datetime.now(lima)
    return fehcaEvaluar


def fix_id(resp):
    # print(resp)
    resp["id_"] = str(resp["_id"])
    resp["created_at"] = formatDate(resp["created_at"])
    resp["last_modified"] = formatDate(resp["last_modified"])
    return resp


@registros_router.get("/count")
async def get_count():
    # print("qweqweqwe")
    conteo = await DB.registros.count_documents({})
    return conteo


@registros_router.get("/", response_model=List[RegistroOnDB])
async def get_all_registros(dni: str = None, estado: str = None, ini_date: str = None, fin_date: str = None,
                            limit: int = 10, skip: int = 0):
    """[summary]
    Gets all registros.

    [description]
    Endpoint to retrieve registros.
    """

    print("dni: ", dni)
    print("estado: ", estado)
    print("ini_date", ini_date)
    print("fin_date", fin_date)
    in_time_obj = datetime.strptime("{} 00:00:00".format(ini_date), '%Y-%m-%d %H:%M:%S')
    out_time_obj = datetime.strptime("{} 00:00:00".format(fin_date), '%Y-%m-%d %H:%M:%S')
    global registro_cursor
    if dni == "null":
        dni = None
    if estado == "null":
        estado = None
    if ini_date == "null":
        ini_date = None
    if fin_date == "null":
        fin_date = None
    if dni is None and estado is None:
        # registro_cursor = DB.registros.find({'created_at' : {"$gte": from_date, "$lt": to_date}}).skip(skip).limit(limit)
        registro_cursor = DB.registros.find({'created_at': {"$gte": in_time_obj, "$lt": out_time_obj}}).skip(skip).limit(limit)

    elif dni is None and estado:
        registro_cursor = DB.registros.find({"estado": estado}).skip(skip).limit(limit)

    elif dni and estado is None:
        print("aqui")
        registro_cursor = DB.registros.find({"responsable": dni}).skip(skip).limit(limit)

    elif dni and estado and ini_date and fin_date:
        print("Por fecha")
        registro_cursor = DB.registros.find({'created_at': {"$gte": in_time_obj, "$lt": out_time_obj}}).skip(skip).limit(limit)

    elif dni and estado:
        print({"responsable": dni, "estado": estado})
        registro_cursor = DB.registros.find({"responsable": dni, "estado": estado}).skip(skip).limit(limit)

    return list(map(fix_id, await registro_cursor.to_list(length=limit)))


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
    print("#############################################")
    registro = await DB.registros.find_one({"_id": id_})
    if registro:
        registro["id_"] = str(registro["_id"])
        registro["created_at"] = formatDate(registro["created_at"])
        registro["last_modified"] = formatDate(registro["last_modified"])
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
