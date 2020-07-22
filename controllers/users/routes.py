# backend/tancho/users/routes.py
import logging
from typing import List

from bson.objectid import ObjectId
from fastapi import APIRouter, Depends, HTTPException
from passlib.context import CryptContext

from config.config import DB, CONF
from .models import UserOnDB, UserRol, UserIn, UserOut, UserLogin, UserBase

user_router = APIRouter()

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password):
    contr = pwd_context.hash(password)
    return contr


# def get_user(db, username: str):
#     if username in db:
#         user_dict = db[username]
#         return UserInDB(**user_dict)
#
#
# def authenticate_user(fake_db, username: str, password: str):
#     user = get_user(fake_db, username)
#     if not user:
#         return False
#     if not verify_password(password, user.hashed_password):
#         return False
#     return user

async def validar_duplicados(dni: str):
    get_user = await DB.users.find_one({"dni": dni})
    get_user = get_user.inserted_id
    print("get_user")
    print(get_user)
    print("get_user")
    if get_user:
        return "Ya existe el dni"
    else:
        return "Puede registrarse"


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
    user = await DB.users.find_one({"_id": _id})
    if user:
        return fix_user_id(user)
    else:
        raise HTTPException(status_code=404, detail="Pet not found")


def fix_user_id(user):
    user["id_"] = str(user["_id"])
    return user

@user_router.get("/count")
async def get_count_user():
    # print("qweqweqwe")
    conteo = await DB.users.count_documents({})
    return conteo

@user_router.get("/", response_model=List[UserOnDB])
async def get_all_users(rol: UserRol = None, limit: int = 1000, skip: int = 0):
    """[summary]
    Gets all users.

    [description]
    Endpoint to retrieve users.
    """
    if rol is None:
        users_cursor = DB.users.find().skip(skip).limit(limit)
    else:
        users_cursor = DB.users.find({"rol": rol.value}).skip(skip).limit(limit)
    users = await users_cursor.to_list(length=limit)
    return list(map(fix_user_id, users))


@user_router.post("/login", response_model=UserOnDB)
async def user_login(user: UserLogin):
    """[summary]
    Gets all users.

    [description]
    Endpoint to retrieve users.
    """
    get_user = await DB.users.find_one({"email": user.email})
    if get_user:
        verificar = verify_password(user.password, get_user['password'])
        if verificar:
            print("verificar", verificar)
            get_user["id_"] = str(get_user["_id"])
            return get_user
        else:
            raise HTTPException(status_code=200, detail="Password incorrecto")
    else:
        raise HTTPException(status_code=200, detail="Correo incorrecto")


# @user_router.post("/")
@user_router.post("/", response_model=UserOut)
async def add_user(*, user: UserIn):
    """[summary]
    Inserts a new user on the DB.users
    [description]
    Endpoint to add a new user.
    """
    # print(user)
    get_user = await DB.users.find_one({"dni": user.dni})
    if get_user:
        raise HTTPException(
            status_code=400,
            detail="El usuario con este dni ya existe",
        )
    user_op = await DB.users.insert_one(user.dict())
    return user
    # try:
    #     # return { "user" : UserOut , "codRes" : "00"  }
    #     # print("qwe")
    #     return user
    # except:
    # #     print("asd")
    # #     return { "user" : user , "codRes" : "01"  }
    #     return user


@user_router.get(
    "/{id_}",
    response_model=UserOnDB
)
async def get_user_by_id(id_: ObjectId = Depends(validate_object_id)):
    """[summary]
    Get one user by ID.

    [UserOnDBn]
    Endpoint to retrieve an specific user.
    """
    user = await DB.users.find_one({"_id": id_})
    if user:
        user["id_"] = str(user["_id"])
        return user
    else:
        raise HTTPException(status_code=404, detail="Pet not found")
#
#
@user_router.delete(
    "/{id_}",
    dependencies=[Depends(_get_or_404)],
    response_model=dict
)
async def delete_user_by_id(id_: str):
    """[summary]
    Get one user by ID.

    [description]
    Endpoint to retrieve an specific user.
    """
    user_op = await DB.users.delete_one({"_id": ObjectId(id_)})
    if user_op.deleted_count:
        return {"status": f"deleted count: {user_op.deleted_count}"}

@user_router.put(
    "/{id_}",
    dependencies=[Depends(validate_object_id), Depends(_get_or_404)],
    response_model=UserOnDB
)
async def update_user(id_: str, user_data: dict):
    """[summary]
    Update a user by ID.

    [description]
    Endpoint to update an specific user with some or all fields.
    """
    print(user_data)
    user_op = await DB.users.update_one(
        {"_id": ObjectId(id_)}, {"$set": user_data}
    )
    if user_op.modified_count:
        return await _get_or_404(id_)
    else:
        raise HTTPException(status_code=304)