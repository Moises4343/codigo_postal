from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.db.config import VERSION
from app.db.database import get_db
from app.schemas.codigo_postal_schema import CodigoPostalResponse, CodigoPostalData, CodigoPostalAttributes
from app.services.codigo_postal_service import get_info_by_postal_code

router = APIRouter()

@router.get(f"/api/{VERSION}/postalCode", response_model=CodigoPostalResponse)
def get_postal_code_info(cp: str, db: Session = Depends(get_db)):
    info = get_info_by_postal_code(cp, db)

    response = CodigoPostalResponse(
        data=CodigoPostalData(
            type="postalCodeInfo",
            cp=cp,
            attributes=CodigoPostalAttributes(
                estado=info["estado"],
                ciudad=info["ciudad"],
                colonias=info["colonias"]
            )
        )
    )

    return response
