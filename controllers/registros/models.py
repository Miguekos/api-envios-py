# backend/tancho/pets/models.py
from datetime import datetime
from pytz import timezone
from enum import Enum
from pydantic import BaseModel, validator
from datetime import date
from typing import List, Optional

class RegistroBase(BaseModel):
    """[summary]
        Base pet abstraction model.

    [description]
        Used to abstract out basic pet fields.

    Arguments:
        BaseModel {[type]} -- [description]
    """
    name: str
    lastname: str
    comuna: str
    direccion: str
    telf: str
    tipodepago: str
    control: str
    valordeflete: str
    proveedores: str
    registro: int
    estado: str = "0"
    user_registrante: str = None
    responsable: str = None
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


class RegistroOnDB(RegistroBase):
    """[summary]
    Actual model used at DB level

    [description]
    Extends:
        PetBase
    Adds `_id` field.

    Variables:
        _id: str {[ObjectId]} -- [id at DB]
    """
    id_ : str