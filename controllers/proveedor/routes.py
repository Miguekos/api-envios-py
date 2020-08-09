# backend/tancho/registros/routes.py
import logging
from collections import Counter
from datetime import datetime, timedelta
from typing import List

import pytz

from bson.objectid import ObjectId
from fastapi import APIRouter, Depends, HTTPException

from config.config import DB, CONF
from .models import ReporteBase, ReporteOnDB, ReporteFilter, ReporteHistorico

proveedor_router = APIRouter()


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
    resp = await DB.proveedor.find_one({"_id": _id})
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


def fix_id_provee(resp):
    resp["id_"] = str(resp["_id"])
    resp.pop('_id')
    return resp


def fix_id(resp):
    resp["id_"] = str(resp["_id"])
    resp["created_at"] = formatDate(resp["created_at"])
    resp["last_modified"] = formatDate(resp["last_modified"])
    return resp

@proveedor_router.get("/")
async def get_proveedor(ini_date: str = None, fin_date: str = None, provee: int = None, estado : str = None):
    """[summary]
    Obtener proveedors.

    [description]
    Reportes por fechas.
    """
    try:
        findProvee = await DB.mantenimiento.find_one({'registro' : provee})
        # print(findProvee['name'])
        global total
        total = []
        # pd.DataFrame(MyList, columns=["x"]).groupby('x').size().to_dict()
        in_time_obj = datetime.strptime("{} 00:00:00".format(ini_date), '%d/%m/%Y %H:%M:%S')
        in_time_obj = formatDate(in_time_obj) + timedelta(hours=5)
        out_time_obj = datetime.strptime("{} 23:59:59".format(fin_date), '%d/%m/%Y %H:%M:%S')
        out_time_obj = formatDate(out_time_obj) + timedelta(hours=5)
        print("Traer datos de {} hasta {}".format(in_time_obj, out_time_obj))
        registro_cursor = DB.registros.find({'proveedores' : '{}'.format(findProvee['name']), 'estado' : estado , 'last_modified': {"$gte": in_time_obj, "$lt": out_time_obj}})
        # registro_cursor = DB.registros.find()
        return list(map(fix_id_provee, await registro_cursor.to_list(None)))
    except:
        raise HTTPException(status_code=500, detail="Error controlado")
    # for docs in await registro_cursor.to_list(None):
    #     total.append(fix_id_provee(docs))
    #     # print(nameMobil(docs['responsable']))
    #     # responsables.append(nameMobil(docs['responsable']))
    # print(total)
    # return { list(total) }
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


@proveedor_router.get("/historico")
async def get_proveedor_tipodepagos(ini_date: str = None):
    """[summary]
    Obtener proveedors.

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
            # return list(map(fix_id_provee, users))
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
            print(docs)
            if docs['tipodepago'] == 'Pagado':
                total_pagado.append(docs['tipodepago'])
            if docs['tipodepago'] == 'Por pagar':
                total_por_pagado.append(docs['tipodepago'])
            if docs['tipodepago'] == 'Cuenta Corriente':
                total_credito.append(docs['tipodepago'])
        print(total_pagado)
        print(total_por_pagado)
        print(total_credito)
        lima = pytz.timezone('America/Lima')
        jsonEnviar = {
            "total_registro": len(total),
            "total_pagado": len(total_pagado),
            "total_por_pagado": len(total_por_pagado),
            "total_credito": len(total_credito),
            "fecha": str(ini_date),
            "created_at": datetime.now(lima),
            "created_format": in_time_obj.strftime("%b %d")
        }
        # print(type(jsonEnviar))
        print(jsonEnviar)
        buscar = await DB.historico.find_one({"fecha": ini_date})
        if buscar is None:
            guardar = await DB.historico.insert_one(jsonEnviar)
            print("Se inserto")
            return {
                "result": "Se inserto"
            }
        else:
            registro_op = await DB.historico.update_one(
                {"fecha": ini_date}, {"$set": jsonEnviar}
            )
            print(registro_op.modified_count)
            print("Se actualizo")
            return {
                "result": "Se actualizo"
            }


# @proveedor_router.post("/", response_model=ReporteOnDB)
@proveedor_router.post("/proveedores")
async def add_registro(registro: ReporteBase):
    """[summary]
    Inserts a new user on the DB.

    [description]
    Endpoint to add a new user.
    """
    try:
        conteo = DB.proveedor.find({}, {'registro': 1}).sort('registro', -1).limit(1)
        conteo = await conteo.to_list(length=1)
        registro = registro.dict()
        registro['registro'] = conteo[0]['registro'] + 1
    except:
        registro['registro'] = 0
    registro_op = await DB.proveedor.insert_one(registro)
    return {
        "id": str(registro_op.inserted_id),
        "registro": registro['registro']
    }


@proveedor_router.get(
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
    registro = await DB.proveedor.find_one({"_id": id_})
    if registro:
        registro["id_"] = str(registro["_id"])
        # registro["created_at"] = formatDate(registro["created_at"])
        # registro["last_modified"] = formatDate(registro["last_modified"])
        return registro
    else:
        raise HTTPException(status_code=404, detail="not found")


# buscar por registro y control
@proveedor_router.get(
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


@proveedor_router.delete(
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
    registros_op = await DB.proveedor.delete_one({"_id": ObjectId(id_)})
    if registros_op.deleted_count:
        return {"status": f"se elimino la cuenta de: {registros_op.deleted_count}"}


@proveedor_router.put(
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
    registro_op = await DB.proveedor.update_one(
        {"_id": ObjectId(id_)}, {"$set": registro_data}
    )
    if registro_op.modified_count:
        return await _get_or_404(id_)
    else:
        raise HTTPException(status_code=304)
