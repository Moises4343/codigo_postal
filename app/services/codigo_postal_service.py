from sqlalchemy.orm import Session
from app.db.models import CodigoPostal
from fastapi import HTTPException, status

def get_info_by_postal_code(cp: str, db: Session):
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

    return {
        "estado": estado,
        "ciudad": ciudad,
        "colonias": colonias
    }
