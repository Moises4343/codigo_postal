from pydantic import BaseModel
from typing import List

class CodigoPostalAttributes(BaseModel):
    estado: str
    ciudad: str
    colonias: List[str]

class CodigoPostalData(BaseModel):
    type: str
    id: str
    attributes: CodigoPostalAttributes

class CodigoPostalResponse(BaseModel):
    data: CodigoPostalData