# backend/tancho/registros/routes.py
import logging
from collections import Counter
from datetime import datetime, timedelta
from typing import List

from bson.objectid import ObjectId
from fastapi import APIRouter, Depends, HTTPException

from config.config import DB, CONF
from .models import ReporteBase, ReporteOnDB, ReporteFilter, ReporteHistorico

reporte_router = APIRouter()


async def nameMobil(resp):
    resp = await DB.users.find_one({"dni": "{}".format(resp)})
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
    resp = await DB.reporte.find_one({"_id": _id})
    if resp:
        return fix_id(resp)
    else:
        raise HTTPException(status_code=404, detail="not found")


def formatDate(v):
    import pytz
    lima = pytz.timezone('America/Lima')
    v = v.replace(tzinfo=pytz.UTC)
    fehcaEvaluar = v.astimezone(lima)
    return fehcaEvaluar

def fix_id_historico(resp):
    resp["id_"] = str(resp["_id"])
    resp.pop('_id')
    return resp


def fix_id(resp):
    resp["id_"] = str(resp["_id"])
    resp["created_at"] = formatDate(resp["created_at"])
    resp["last_modified"] = formatDate(resp["last_modified"])
    return resp


@reporte_router.get("/dashboard")
async def get_reporte_tipodepagos(ini_date: str = None, fin_date: str = None):
    """[summary]
    Obtener reportes.

    [description]
    Reportes por fechas.
    """
    # pd.DataFrame(MyList, columns=["x"]).groupby('x').size().to_dict()
    global total_pagado, total_por_pagado, total_credito, comunas, proveedores, responsables, total
    total = []
    responsables = []
    proveedores = []
    comunas = []
    total_pagado = []
    total_por_pagado = []
    total_credito = []
    in_time_obj = datetime.strptime("{} 00:00:00".format(ini_date), '%d/%m/%Y %H:%M:%S')
    in_time_obj = formatDate(in_time_obj) + timedelta(hours=5)
    out_time_obj = datetime.strptime("{} 23:59:59".format(fin_date), '%d/%m/%Y %H:%M:%S')
    out_time_obj = formatDate(out_time_obj) + timedelta(hours=5)
    print("Traer datos de {} hasta {}".format(in_time_obj, out_time_obj))
    registro_cursor = DB.registros.find({'last_modified': {"$gte": in_time_obj, "$lt": out_time_obj}})
    # registro_cursor = DB.registros.find()
    for docs in await registro_cursor.to_list(None):
        total.append("docs")
        # print(nameMobil(docs['responsable']))
        # responsables.append(nameMobil(docs['responsable']))
        if docs['responsable'] != None and docs['responsable'] != "":
            # print("docs['responsable']", await nameMobil(docs['responsable']))
            # responsables.append(await nameMobil(docs['responsable']))
            responsables.append(docs['responsable_name'])
        else:
            print(docs['_id'])
            print(docs['responsable'])
        comunas.append(docs['comuna'])
        proveedores.append(docs['proveedores'])
        if docs['tipodepago'] == 'Pagado':
            total_pagado.append(docs['tipodepago'])
        if docs['tipodepago'] == 'Por pagar':
            total_por_pagado.append(docs['tipodepago'])
        if docs['tipodepago'] == 'Cuenta Corriente':
            total_credito.append(docs['tipodepago'])
    # return list(map(fix_id, await registro_cursor.to_list(length=10)))
    # try:
    global keys_comunas, keys_proveedores, keys_responsables, values_comunas, values_proveedores, values_responsables
    keys_comunas = []
    keys_proveedores = []
    keys_responsables = []
    values_comunas = []
    values_proveedores = []
    values_responsables = []
    if len(comunas) > 0:
        comunas = dict(Counter(comunas))
        keys_comunas, values_comunas = zip(*comunas.items())

    if len(proveedores) > 0:
        proveedores = dict(Counter(proveedores))
        keys_proveedores, values_proveedores = zip(*proveedores.items())

    if len(responsables) > 0:
        responsables = dict(Counter(responsables))
        keys_responsables, values_responsables = zip(*responsables.items())
    # printing keys and values separately
    return {
        "total_registro": len(total),
        "total_pagado": len(total_pagado),
        "total_por_pagado": len(total_por_pagado),
        "total_credito": len(total_credito),
        "comunasKeys": keys_comunas,
        "comunasValue": values_comunas,
        "proveedoresKeys": keys_proveedores,
        "proveedoresValue": values_proveedores,
        "responsablesKeys": keys_responsables,
        "responsablesValue": values_responsables
    }
    # except:
    #     return {
    #         "total_registro": len(total),
    #         "total_pagado": len(total_pagado),
    #         "total_por_pagado": len(total_por_pagado),
    #         "total_credito": len(total_credito),
    #         "comunasKeys": keys_comunas,
    #         "comunasValue": values_comunas,
    #         "proveedoresKeys": keys_proveedores,
    #         "proveedoresValue": values_proveedores,
    #         "responsablesKeys": keys_responsables,
    #         "responsablesValue": values_responsables
    #     }


@reporte_router.get("/historico")
async def get_reporte_tipodepagos(ini_date: str = None):
    """[summary]
    Obtener reportes.

    [description]
    Reportes por fechas.
    """
    # pd.DataFrame(MyList, columns=["x"]).groupby('x').size().to_dict()
    if ini_date is None:
        buscar = DB.historico.find({})
        # buscar = DB.historico.find({}, {'_id': 0})
        # return await buscar.to_list(None)
        # users = await buscar.to_list(None)
        # global total_pagado, total_por_pagado, total_credito, total, fecha
        total_pagado_h = []
        total_por_pagado_h = []
        total_registro_h = []
        fecha_h = []
        for docs in await buscar.to_list(None):
            total_pagado_h.append(docs['total_pagado'])
            total_por_pagado_h.append(docs['total_por_pagado'])
            total_registro_h.append(docs['total_registro'])
            fecha_h.append(docs['created_format'])

            # print(users)
            # return list(map(fix_id_historico, users))
        return {
            "total_pagado": total_pagado_h,
            "total_por_pagado": total_por_pagado_h,
            "total_registro": total_registro_h,
            "fecha": fecha_h
        }
    else:
        global total_pagado, total_por_pagado, total_credito, comunas, proveedores, responsables, total
        total = []
        responsables = []
        proveedores = []
        comunas = []
        total_pagado = []
        total_por_pagado = []
        total_credito = []
        in_time_obj = datetime.strptime("{} 00:00:00".format(ini_date), '%d/%m/%Y %H:%M:%S')
        in_time_obj = formatDate(in_time_obj) + timedelta(hours=5)
        out_time_obj = datetime.strptime("{} 23:59:59".format(ini_date), '%d/%m/%Y %H:%M:%S')
        out_time_obj = formatDate(out_time_obj) + timedelta(hours=5)
        print("Traer datos de {} hasta {}".format(in_time_obj, out_time_obj))
        registro_cursor = DB.registros.find({'last_modified': {"$gte": in_time_obj, "$lt": out_time_obj}})
        # registro_cursor = DB.registros.find()
        for docs in await registro_cursor.to_list(None):
            total.append("docs")
            if docs['tipodepago'] == 'Pagado':
                total_pagado.append(docs['tipodepago'])
            if docs['tipodepago'] == 'Por pagar':
                total_por_pagado.append(docs['tipodepago'])
            if docs['tipodepago'] == 'Cuenta Corriente':
                total_credito.append(docs['tipodepago'])
        jsonEnviar = {
            "total_registro": len(total),
            "total_pagado": len(total_pagado),
            "total_por_pagado": len(total_por_pagado),
            "total_credito": len(total_credito),
            "fecha": str(ini_date),
            "created_at": in_time_obj,
            "created_format": in_time_obj.strftime("%b %d")
        }
        # print(type(jsonEnviar))
        # print(jsonEnviar)
        buscar = await DB.historico.find_one({"fecha": ini_date})
        if buscar is None:
            guardar = await DB.historico.insert_one(jsonEnviar)
            return {
                "result": "Se inserto"
            }
        else:
            registro_op = await DB.reporte.update_one(
                {"fecha": ini_date}, {"$set": jsonEnviar}
            )
            return {
                "result": "Se actualizo"
            }


# @reporte_router.post("/", response_model=ReporteOnDB)
@reporte_router.post("/proveedores")
async def add_registro(registro: ReporteBase):
    """[summary]
    Inserts a new user on the DB.

    [description]
    Endpoint to add a new user.
    """
    try:
        conteo = DB.reporte.find({}, {'registro': 1}).sort('registro', -1).limit(1)
        conteo = await conteo.to_list(length=1)
        registro = registro.dict()
        registro['registro'] = conteo[0]['registro'] + 1
    except:
        registro['registro'] = 0
    registro_op = await DB.reporte.insert_one(registro)
    return {
        "id": str(registro_op.inserted_id),
        "registro": registro['registro']
    }


@reporte_router.get(
    "/proveedores/{id_}",
    response_model=ReporteOnDB
)
async def get_registro_by_id(id_: ObjectId = Depends(validate_object_id)):
    """[summary]
    Get one registro by ID.

    [description]
    Endpoint to retrieve an specific registro.
    """
    print("#############################################")
    registro = await DB.reporte.find_one({"_id": id_})
    if registro:
        registro["id_"] = str(registro["_id"])
        # registro["created_at"] = formatDate(registro["created_at"])
        # registro["last_modified"] = formatDate(registro["last_modified"])
        return registro
    else:
        raise HTTPException(status_code=404, detail="not found")


# buscar por registro y control
@reporte_router.get(
    "/filtros/{tipo}/{id_}",
    response_model=ReporteFilter
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
            # registro["created_at"] = formatDate(registro["created_at"])
            # registro["last_modified"] = formatDate(registro["last_modified"])
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
            # registro["created_at"] = formatDate(registro["created_at"])
            # registro["last_modified"] = formatDate(registro["last_modified"])
            if registro["responsable"]:
                registro["responsable_name"] = await nameMobil(registro["responsable"])
                registro["created_at"] = formatDate(registro["created_at"])
                registro["responsable_name"] = await nameMobil(registro["responsable"])
            return registro
    else:
        raise HTTPException(status_code=404, detail="not found")


@reporte_router.delete(
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
    registros_op = await DB.reporte.delete_one({"_id": ObjectId(id_)})
    if registros_op.deleted_count:
        return {"status": f"se elimino la cuenta de: {registros_op.deleted_count}"}


@reporte_router.put(
    "/proveedores/{id_}",
    dependencies=[Depends(validate_object_id), Depends(_get_or_404)],
    response_model=ReporteOnDB
)
async def update_registro(id_: str, registro_data: dict):
    """[summary]
    Update a registro by ID.

    [description]
    Endpoint to update an specific registro with some or all fields.
    """
    registro_op = await DB.reporte.update_one(
        {"_id": ObjectId(id_)}, {"$set": registro_data}
    )
    if registro_op.modified_count:
        return await _get_or_404(id_)
    else:
        raise HTTPException(status_code=304)
