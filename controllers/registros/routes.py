# backend/tancho/registros/routes.py
import logging
from datetime import datetime, timedelta
from pytz import timezone
from typing import List

from bson.objectid import ObjectId
from fastapi import APIRouter, Depends, HTTPException

from config.config import DB, CONF
from .models import RegistroBase, RegistroOnDB, RegistroOnDBQR

import pytz

registros_router = APIRouter()
import requests


async def nameMobil(resp):
    resp = await DB.users.find_one({"dni": "{}".format(resp)})
    return resp['name']


#
# async def nameMobil(val):
#     try:
#         resp = await DB.users.find_one({"dni": "{}".format(val)})
#         print("###################")
#         print(resp['name'])
#         print("###################")
#         val['responsable_name'] = resp['name']
#         val["id_"] = str(val["_id"])
#         return val
#     except:
#         print("Ya tenia")


def enviarSms(telf, registro):
    print("enviarSms", telf, registro)
    url = "https://api.labsmobile.com/get/send.php?username=administracion@texcargo.cl&password=t3xc4rg0cl2021&message=TexCargo le notifica que se le a realizado un envio con numero de orden {}, para mas informacion dirigete a https://tracking.texcargo.cl/tracking.php?id={}&msisdn=56{}&sender=34609033163".format(
        registro,
        registro, telf)
    print(url)
    response = requests.request("GET", url)

    print(response.text)


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
    lima = pytz.timezone('America/Lima')
    fehcaEvaluarTest = v
    # print("fehcaEvaluarTest", fehcaEvaluarTest)
    # tz = pytz.timezone('America/St_Johns')
    fehcaEvaluarTest = fehcaEvaluarTest.replace(tzinfo=pytz.UTC)
    # print("fehcaEvaluarTest 2", fehcaEvaluarTest)
    fehcaEvaluar = fehcaEvaluarTest.astimezone(lima)
    # print("fehcaEvaluarTest 3", fehcaEvaluar)
    # print("fehcaEvaluar")
    # print(fehcaEvaluar)
    # print(datetime.now(lima))
    # return v or datetime.now(lima)
    return fehcaEvaluar


def fix_id(resp):
    resp["id_"] = str(resp["_id"])
    # try:
    #    asd = resp["responsable_name"]
    #   print("ya tiene",asd)
    # except:
    #   print("responsable", resp["responsable"])
    #  resp["responsable_name"] = nameMobil(resp["responsable"])
    # resp["responsable_name"] = nameMobil(resp["responsable"])
    resp["created_at"] = formatDate(resp["created_at"])
    # print("resp", resp)
    resp["last_modified"] = formatDate(resp["last_modified"])
    return resp


@registros_router.get("/count")
async def get_count():
    # print("qweqweqwe")
    conteo = DB.registros.find({}, {'registro': 1}).sort('registro', -1).limit(1)
    conteo = await conteo.to_list(length=1)
    print(conteo[0]['registro'])
    return conteo[0]['registro']


@registros_router.get("/findMobil/{dnimobil}")
async def get_proveedor(dnimobil: int = None):
    """[summary]
    Obtener proveedors.

    [description]
    Reportes por fechas.
    """
    print("dnimobil", dnimobil)
    try:
        global total
        total = []

        # buscar = DB.historico.find({})
        # pd.DataFrame(MyList, columns=["x"]).groupby('x').size().to_dict()
        registro_cursor = DB.registros.find({'responsable': '{}'.format(dnimobil)})
        bodega = []
        asignados = []
        entregados = []

        for docs in await registro_cursor.to_list(None):
            print(docs['estado'])
            total.append(docs)
            if docs['estado'] == "0":
                bodega.append(docs['estado'])

            if docs['estado'] == "1":
                asignados.append(docs['estado'])

            if docs['estado'] == "2":
                entregados.append(docs['estado'])

            # print(users)
            # return list(map(fix_id_provee, users))
        return {
            "total_bodega": len(bodega),
            "total_asignados": len(asignados),
            "total_entregados": len(entregados),
            "total": len(total)
        }
        # print("registro_cursor",await registro_cursor)
        # registro_cursor = DB.registros.find()
        # return list(map(fix_id_provee, await registro_cursor.to_list(None)))
    except:
        # print(ValueError)
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


# asignar paquetes por QR
@registros_router.put("/addqr/{registro}")
async def add_asing_qr(registro: int, registro_data: dict):
    # print("qweqweqwe")
    print(registro_data)
    global message
    try:
        buscar_registro = DB.registros.find({'registro': registro})
        if buscar_registro:
            buscar_registro = await buscar_registro.to_list(length=1)
            estado = buscar_registro[0]['estado']
            telf = buscar_registro[0]['telf']
            print("estado", estado)
            if estado == "0":
                lima = pytz.timezone('America/Lima')
                registro_data["last_modified"] = datetime.now(lima)
                # registro_data["registro"] = int(registro_data["registro"])
                await DB.registros.update_one(
                    {"registro": registro}, {"$set": registro_data}
                )
                print("Paquete asigando correctamente")
                message = "Paquete asigando correctamente"
                if telf:
                    pass
                    # enviarSms(telf, registro)
            elif estado == "1":
                print("Ya fue asignado")
                message = "Ya fue asignado"
            else:
                print("Se encutra entregado o borrado")
                message = "Se encutra entregado o borrado"
        return {message}
    except:
        return {"No existe este paquete"}


@registros_router.get("/repair")
async def reparar():
    """[summary]
    Gets all registros.

    [description]
    Endpoint to retrieve registros.
    """

    # registro_cursor = DB.registros.find({'created_at' : {"$gte": from_date, "$lt": to_date}}).skip(skip).limit(limit)
    registro_cursor = DB.registros.find()
    for docs in await registro_cursor.to_list(None):
        if docs['responsable'] != None and docs['responsable'] != "":
            print(docs['responsable'])
            print(docs['_id'])
            print(docs['registro'])
            registro_op = await DB.registros.update_one(
                {"_id": ObjectId(docs['_id'])}, {"$set": {"responsable_name": await nameMobil(docs['responsable'])}}
            )
    return {"completado": "completado"}


@registros_router.get("/buscar", response_model=List[RegistroOnDB])
async def get_all_registros(ini_date: str = None, fin_date: str = None, provee: str = None,
                            limit: int = 0, skip: int = 0):
    """[summary]
    Gets all registros.

    [description]
    Endpoint to retrieve registros.
    """

    print("ini_date", ini_date)
    print("fin_date", fin_date)
    print("provee", provee)
    global registro_cursor
    if ini_date == "null":
        ini_date = None
    if fin_date == "null":
        fin_date = None

    print("Sin DNI")
    in_time_obj = datetime.strptime("{} 00:00:00".format(ini_date), '%d/%m/%Y %H:%M:%S')
    in_time_obj = formatDate(in_time_obj) + timedelta(hours=5)
    out_time_obj = datetime.strptime("{} 23:59:59".format(fin_date), '%d/%m/%Y %H:%M:%S')
    out_time_obj = formatDate(out_time_obj) + timedelta(hours=5)
    print("Traer datos de {} hasta {}".format(in_time_obj, out_time_obj))
    registro_cursor = DB.registros.find(
        {
            'created_at': {"$gte": in_time_obj, "$lt": out_time_obj},
            'proveedores' : "{}".format(provee)

        }
    ).skip(skip).limit(limit)
    return list(map(fix_id, await registro_cursor.to_list(length=limit)))


# sms
@registros_router.get("/sms/{telf}/{registro}")
async def send_sms(telf: str, registro: str):
    """[summary]
    Gets all registros.

    [description]
    Endpoint to retrieve registros.
    """
    # print(id)
    # registro = await DB.registros.find_one({"registro": id})
    # if registro:
    #     print(registro)
    # registro["id_"] = str(registro["_id"])
    # registro.pop('_id')
    # registro["created_at"] = formatDate(registro["created_at"])
    # registro["last_modified"] = formatDate(registro["last_modified"])
    enviarSms(telf, registro)
    return {
        "message": "mensaje enviado correctamente"
    }


# tracking
@registros_router.get("/tracking/{id}")
async def get_packet_tranking(id: int):
    """[summary]
    Gets all registros.

    [description]
    Endpoint to retrieve registros.
    """
    print(id)
    registro = await DB.registros.find_one({"registro": id})
    if registro:
        print(registro)
        # registro["id_"] = str(registro["_id"])
        registro.pop('_id')
        # registro["created_at"] = formatDate(registro["created_at"])
        # registro["last_modified"] = formatDate(registro["last_modified"])
        return registro
    else:
        raise HTTPException(status_code=404, detail="not found")


@registros_router.get("/", response_model=List[RegistroOnDB])
async def get_all_registros(dni: str = None, estado: str = None, ini_date: str = None, fin_date: str = None,
                            limit: int = 10000, skip: int = 0):
    """[summary]
    Gets all registros.

    [description]
    Endpoint to retrieve registros.
    """

    print("dni: ", dni)
    print("estado: ", estado)
    print("ini_date", ini_date)
    print("fin_date", fin_date)
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
        registro_cursor = DB.registros.find().skip(skip).limit(limit)

    # elif dni is None and estado:
    #     registro_cursor = DB.registros.find({"estado": estado}).skip(skip).limit(limit)

    # elif dni and estado is None:
    #     print("aqui")
    #     registro_cursor = DB.registros.find({"responsable": dni}).skip(skip).limit(limit)
    elif dni is None and estado and ini_date and fin_date:
        print("Sin DNI")
        in_time_obj = datetime.strptime("{} 00:00:00".format(ini_date), '%d/%m/%Y %H:%M:%S')
        in_time_obj = formatDate(in_time_obj) + timedelta(hours=5)
        out_time_obj = datetime.strptime("{} 23:59:59".format(fin_date), '%d/%m/%Y %H:%M:%S')
        out_time_obj = formatDate(out_time_obj) + timedelta(hours=5)
        print("Traer datos de {} hasta {}".format(in_time_obj, out_time_obj))
        # print("Verficiaar tiop", type(estado))
        if estado == "0":
            registro_cursor = DB.registros.find(
                {'estado': estado, 'created_at': {"$gte": in_time_obj, "$lt": out_time_obj}}).skip(skip).limit(limit)
        # print(await r:egistro_cursor.to_list(length=1000))
        if estado != "0":
            registro_cursor = DB.registros.find(
                {'estado': estado, 'last_modified': {"$gte": in_time_obj, "$lt": out_time_obj}}).skip(skip).limit(limit)

    elif dni and estado and ini_date and fin_date:
        print("Con DNI")
        in_time_obj = datetime.strptime("{} 00:00:00".format(ini_date), '%d/%m/%Y %H:%M:%S')
        in_time_obj = formatDate(in_time_obj) + timedelta(hours=5)
        out_time_obj = datetime.strptime("{} 23:59:59".format(fin_date), '%d/%m/%Y %H:%M:%S')
        out_time_obj = formatDate(out_time_obj) + timedelta(hours=5)
        if estado == "0":
            registro_cursor = DB.registros.find(
                {"responsable": dni, 'estado': estado,
                 'last_modified': {"$gte": in_time_obj, "$lt": out_time_obj}}).skip(
                skip).limit(limit)
        if estado != "0":
            registro_cursor = DB.registros.find(
                {"responsable": dni, 'estado': estado,
                 'last_modified': {"$gte": in_time_obj, "$lt": out_time_obj}}).skip(
                skip).limit(limit)

    elif dni and estado and ini_date is None and fin_date is None:
        print("Con DNI")
        registro_cursor = DB.registros.find({"responsable": dni, 'estado': estado}).skip(skip).limit(limit)

    # elif dni and estado:
    #     print({"responsable": dni, "estado": estado})
    #     registro_cursor = DB.registros.find({"responsable": dni, "estado": estado}).skip(skip).limit(limit)
    # asd = list(map(fix_id, await registro_cursor.to_list(length=limit)))
    # asd = await nameMobil(asd['responsable'])
    # for document in await registro_cursor.to_list(length=1000):
    # print("document", await nameMobil(document['responsable']))
    # document['responsable_name'] = await nameMobil(document['responsable'])
    # document = fix_id(document)
    return list(map(fix_id, await registro_cursor.to_list(length=limit)))


# @registros_router.post("/", response_model=RegistroOnDB)
@registros_router.post("/")
async def add_registro(registro: RegistroBase):
    """[summary]
    Inserts a new user on the DB.

    [description]
    Endpoint to add a new user.
    """
    try:
        conteo = DB.registros.find({}, {'registro': 1}).sort('registro', -1).limit(1)
        conteo = await conteo.to_list(length=1)
        # registro['registro'] = conteo[0]['registro']
        registro = registro.dict()
        registro['registro'] = conteo[0]['registro'] + 1
        registroID = registro['registro']
        Telf = registro['telf']
        enviarSms(Telf, registroID)
    except:
        registro['registro'] = 0
    print("registro", registro)
    registro_op = await DB.registros.insert_one(registro)
    # await DB.registros.update_one(registro.dict())
    # print(registro_op.inserted_id)
    print(registro.pop('_id'))
    return {
        "id": str(registro_op.inserted_id),
        "registro": registro
    }

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
        # registro["created_at"] = formatDate(registro["created_at"])
        # registro["last_modified"] = formatDate(registro["last_modified"])
        return registro
    else:
        raise HTTPException(status_code=404, detail="not found")


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
    lima = pytz.timezone('America/Lima')
    registro_data["last_modified"] = datetime.now(lima)
    registro_op = await DB.registros.update_one(
        {"_id": ObjectId(id_)}, {"$set": registro_data}
    )
    if registro_op.modified_count:
        return await _get_or_404(id_)
    else:
        raise HTTPException(status_code=304)
