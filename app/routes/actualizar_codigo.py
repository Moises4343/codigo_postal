from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from app.db.config import VERSION
from app.db.models import CodigoPostal
from app.db.database import get_db
from app.services.backup_service import backup_to_excel
import pandas as pd
import numpy as np
from io import BytesIO
from sqlalchemy import text

router = APIRouter()

@router.post(f"/api/{VERSION}/actualizar")
async def actualizar_datos(archivo: UploadFile = File(None), db: Session = Depends(get_db)):
    if archivo is None:
        raise HTTPException(status_code=400, detail="Ningún archivo seleccionado.")

    if archivo.content_type not in [
        "application/vnd.ms-excel", 
        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    ]:
        raise HTTPException(status_code=400, detail="El archivo debe ser de tipo Excel (.xls o .xlsx)")

    contenido = await archivo.read()

    columnas_requeridas = [
        'd_codigo', 
        'd_asenta', 
        'd_tipo_asenta', 
        'D_mnpio', 
        'd_estado', 
        'd_ciudad', 
        'd_CP', 
        'c_estado', 
        'c_oficina', 
        'c_CP', 
        'c_tipo_asenta', 
        'c_mnpio', 
        'id_asenta_cpcons', 
        'd_zona', 
        'c_cve_ciudad'
    ]

    try:
        all_sheets = pd.read_excel(BytesIO(contenido), sheet_name=None, dtype=str)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error al leer el archivo: {str(e)}")

    dataframes = [df[columnas_requeridas] for sheet_name, df in all_sheets.items() if all(col in df.columns for col in columnas_requeridas)]
    
    if not dataframes:
        raise HTTPException(status_code=422, detail="Ninguna hoja contiene todas las columnas requeridas.")

    df = pd.concat(dataframes, ignore_index=True).replace({pd.NA: None, np.nan: None, 'nan': None})

    backup_file = backup_to_excel(db, CodigoPostal, VERSION)
    
    try:
        db.execute(text("TRUNCATE TABLE servicio_postal"))
        db.commit()
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error al eliminar datos existentes: {str(e)}")

    records = df.to_dict(orient='records')
    
    try:
        db.bulk_insert_mappings(CodigoPostal, records)
        db.commit()
        message = f"Datos agregados exitosamente en la versión {VERSION}."
        if backup_file:
            message += f" Respaldo guardado en {backup_file}."
        return {"message": message, "total_registros": len(records)}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error al insertar datos: {str(e)}")
