# backend/tancho/registros/routes.py
import logging
from datetime import datetime, timedelta
from typing import List

from bson.objectid import ObjectId
from fastapi import APIRouter, Depends, HTTPException

from config.config import DB, CONF
from .models import MantenimientoBase, MantenimientoOnDB, MantenimientoFilter

mantenimiento_router = APIRouter()

async def nameMobil(val):
    resp = await DB.users.find_one({"dni": "{}".format(val)})
    print("###################")
    print(resp['name'])
    print("###################")
    return resp['name']

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
    resp = await DB.mantenimiento.find_one({"_id": _id})
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
    #resp["created_at"] = formatDate(resp["created_at"])
    #resp["last_modified"] = formatDate(resp["last_modified"])
    return resp

@mantenimiento_router.get("/proveedores", response_model=List[MantenimientoOnDB])
async def get_all_registros(limit: int = 1000, skip: int = 0):
    """[summary]
    Gets all registros.

    [description]
    Endpoint to retrieve registros.
    """
    registro_cursor = DB.mantenimiento.find().skip(skip).limit(limit)
    return list(map(fix_id, await registro_cursor.to_list(length=limit)))


# @mantenimiento_router.post("/", response_model=MantenimientoOnDB)
@mantenimiento_router.post("/proveedores")
async def add_registro(registro: MantenimientoBase):
    """[summary]
    Inserts a new user on the DB.

    [description]
    Endpoint to add a new user.
    """
    try:
        conteo = DB.mantenimiento.find({}, {'registro': 1}).sort('registro', -1).limit(1)
        conteo = await conteo.to_list(length=1)
        registro = registro.dict()
        registro['registro'] = conteo[0]['registro'] + 1
    except:
        registro['registro'] = 0
    registro_op = await DB.mantenimiento.insert_one(registro)
    return {
        "id": str(registro_op.inserted_id),
        "registro" : registro['registro']
    }


@mantenimiento_router.get(
    "/proveedores/{id_}",
    response_model=MantenimientoOnDB
)
async def get_registro_by_id(id_: ObjectId = Depends(validate_object_id)):
    """[summary]
    Get one registro by ID.

    [description]
    Endpoint to retrieve an specific registro.
    """
    print("#############################################")
    registro = await DB.mantenimiento.find_one({"_id": id_})
    if registro:
        registro["id_"] = str(registro["_id"])
        #registro["created_at"] = formatDate(registro["created_at"])
        #registro["last_modified"] = formatDate(registro["last_modified"])
        return registro
    else:
        raise HTTPException(status_code=404, detail="not found")

# buscar por registro y control
@mantenimiento_router.get(
    "/filtros/{tipo}/{id_}",
    response_model=MantenimientoFilter
)
async def get_registro_by_filter(id_: int, tipo: str = 1):
    """[summary]
    Get one registro by ID.

    [description]
    Endpoint to retrieve an specific registro.
    """
    print(id_)
    print(tipo)
    if tipo == "1":
        print("#############################################")
        registro = await DB.registros.find_one({"registro": id_})
        if registro:
            registro["id_"] = str(registro["_id"])
            #registro["created_at"] = formatDate(registro["created_at"])
            #registro["last_modified"] = formatDate(registro["last_modified"])
            if registro["responsable"]:
                registro["responsable_name"] = await nameMobil(registro["responsable"])
                registro["created_at"] = formatDate(registro["created_at"])
                registro["last_modified"] = formatDate(registro["last_modified"])
            return registro
    elif tipo == "2":
        print("#############################################")
        registro = await DB.registros.find_one({"control": "{}".format(id_)})
        if registro:
            registro["id_"] = str(registro["_id"])
            #registro["created_at"] = formatDate(registro["created_at"])
            #registro["last_modified"] = formatDate(registro["last_modified"])
            if registro["responsable"]:
                registro["responsable_name"] = await nameMobil(registro["responsable"])
                registro["created_at"] = formatDate(registro["created_at"])
                registro["responsable_name"] = await nameMobil(registro["responsable"])
            return registro
    else:
        raise HTTPException(status_code=404, detail="not found")


@mantenimiento_router.delete(
    "/proveedores/{id_}",
    dependencies=[Depends(_get_or_404)],
    response_model=dict
)
async def delete_registro_by_id(id_: str):
    """[summary]
    Get one registro by ID.

    [description]
    Endpoint to retrieve an specific registro.
    """
    registros_op = await DB.mantenimiento.delete_one({"_id": ObjectId(id_)})
    if registros_op.deleted_count:
        return {"status": f"se elimino la cuenta de: {registros_op.deleted_count}"}


@mantenimiento_router.put(
    "/proveedores/{id_}",
    dependencies=[Depends(validate_object_id), Depends(_get_or_404)],
    response_model=MantenimientoOnDB
)
async def update_registro(id_: str, registro_data: dict):
    """[summary]
    Update a registro by ID.

    [description]
    Endpoint to update an specific registro with some or all fields.
    """
    registro_op = await DB.mantenimiento.update_one(
        {"_id": ObjectId(id_)}, {"$set": registro_data}
    )
    if registro_op.modified_count:
        return await _get_or_404(id_)
    else:
        raise HTTPException(status_code=304)



