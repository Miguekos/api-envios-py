# backend/tancho/pets/models.py
from datetime import datetime
from passlib.context import CryptContext
from enum import Enum
from pydantic import BaseModel, validator
from pytz import timezone
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class UserRol(str, Enum):
    """[summary]
        Used to manage supported pets.

    [description]
        Simple enumeration to link the kind of a pet.
    """
    admin = "1"
    user = "2"

class UserLogin(BaseModel):
    email : str
    password : str

class UserIn(BaseModel):
    username: str
    name: str
    phone: str
    dni: str
    password: str
    email: str
    rol: UserRol = "1"
    codRes: str = "00"
    created_at: datetime = None
    last_modified: datetime = None

    @validator('created_at', pre=True, always=True)
    def default_ts_created(cls, v):
        lima = timezone('America/Lima')
        print(datetime.now(lima))
        return v or datetime.now(lima)

    @validator('last_modified', pre=True, always=True)
    def default_ts_modified(cls, v, *, values, **kwargs):
        return v or values['created_at']

    @validator('password', pre=True, always=True)
    def get_password_hash(cls, v):
        contr = pwd_context.hash(v)
        return contr

class UserOut(BaseModel):
    username: str
    name: str
    phone: str
    dni: str
    email: str
    rol: UserRol = "1"
    created_at: datetime = None
    last_modified: datetime = None
    codRes: str

    # @validator('status', pre=True, always=True)
    # def get_password_hash(cls, v):
    #     print(v)
    #     return v


class UserBase(BaseModel):
    """[summary]
        Base pet abstraction model.

    [description]
        Used to abstract out basic pet fields.

    Arguments:
        BaseModel {[type]} -- [description]
    """
    name: str
    phone: int
    dni: str
    email: str
    rol: UserRol = 2
    created_at: datetime = None
    last_modified: datetime = None

    @validator('created_at', pre=True, always=True)
    def default_ts_created(cls, v):
        lima = timezone('America/Lima')
        # print(datetime.now(lima))
        return v or datetime.now(lima)

    @validator('last_modified', pre=True, always=True)
    def default_ts_modified(cls, v, *, values, **kwargs):
        return v or values['created_at']


class UserOnDB(UserBase):
    """[summary]
    Actual model used at DB level

    [description]
    Extends:
        PetBase
    Adds `_id` field.

    Variables:
        _id: str {[ObjectId]} -- [id at DB]
    """
    id_: str
