# backend/tancho/pets/models.py
from datetime import datetime
from enum import Enum
from pydantic import BaseModel, validator
from typing import List, Optional
from pytz import timezone

class MsgBase(BaseModel):
    msg = str

class UserRol(str, Enum):
    """[summary]
        Used to manage supported pets.

    [description]
        Simple enumeration to link the kind of a pet.
    """
    admin = "1"
    user = "2"


class UserBase(BaseModel):
    """[summary]
        Base pet abstraction model.

    [description]
        Used to abstract out basic pet fields.

    Arguments:
        BaseModel {[type]} -- [description]
    """
    rol: UserRol
    name: str
    phone: int
    email: str
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

