from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.db.models import CodigoPostal
from app.db.database import get_db
from pydantic import BaseModel
from typing import List

router = APIRouter()


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

class JSONAPIErrorDetail(BaseModel):
    status: str
    title: str
    detail: str

class JSONAPIErrorResponse(BaseModel):
    errors: List[JSONAPIErrorDetail]

@router.get("/api/v1/postalCode", response_model=CodigoPostalResponse)
def get_info_by_postal_code(cp: str, db: Session = Depends(get_db)):
    results = db.query(
        CodigoPostal.d_estado,
        CodigoPostal.D_mnpio,
        CodigoPostal.d_asenta
    ).filter(CodigoPostal.d_codigo == cp).all()

    if not results:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No se encontró información para el código postal proporcionado."
        )

    estado = results[0].d_estado
    ciudad = results[0].D_mnpio
    colonias = [r.d_asenta for r in results]

    response = CodigoPostalResponse(
        data=CodigoPostalData(
            type="postalCodeInfo",
            id=cp,
            attributes=CodigoPostalAttributes(
                estado=estado,
                ciudad=ciudad,
                colonias=colonias
            )
        )
    )

    return response
