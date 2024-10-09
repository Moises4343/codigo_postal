from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.models import CodigoPostal
from app.db.database import get_db

router = APIRouter()

@router.get("/api/v1/cp")
def get_info_by_postal_code(cp: str, db: Session = Depends(get_db)):
    result = db.query(CodigoPostal).filter(CodigoPostal.d_codigo == cp).all()

    if not result:
        raise HTTPException(status_code=404, detail="No se encontró información para el código postal proporcionado.")

    return result
