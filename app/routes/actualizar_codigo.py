from fastapi import APIRouter, Depends, HTTPException, UploadFile, File  
from sqlalchemy.orm import Session
from app.db.models import CodigoPostal
from app.db.database import get_db
import pandas as pd
import numpy as np
from io import BytesIO
from sqlalchemy import text
import os
from datetime import datetime

router = APIRouter()

def backup_to_excel(db: Session, table_model, backup_folder="backups"):
    os.makedirs(backup_folder, exist_ok=True)
    backup_filename = f"{backup_folder}/{table_model.__tablename__}_backup_Fecha_hora_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.xlsx"
    
    records = db.query(table_model).all()
    if not records:
        print("No hay datos en la tabla para respaldar.")
        return None
    
    df_backup = pd.DataFrame([record.__dict__ for record in records])
    df_backup = df_backup.drop(columns=["_sa_instance_state"], errors="ignore")  
    
    columnas_ordenadas = [
        'id', 
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
    
    df_backup = df_backup[columnas_ordenadas]
    
    with pd.ExcelWriter(backup_filename, engine='openpyxl') as writer:
        df_backup.to_excel(writer, index=False, sheet_name="Backup")
    
    print(f"Respaldo realizado exitosamente en {backup_filename}")
    return backup_filename

@router.post("/api/v1/actualizar")
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

    print("Hojas en el archivo:", all_sheets.keys())

    dataframes = []
    for sheet_name, df_sheet in all_sheets.items():
        if all(col in df_sheet.columns for col in columnas_requeridas):
            print(f"La hoja '{sheet_name}' contiene todas las columnas requeridas y será procesada.")
            df_sheet = df_sheet[columnas_requeridas]
            dataframes.append(df_sheet)
        else:
            print(f"La hoja '{sheet_name}' no contiene todas las columnas requeridas y será omitida.")
    
    if not dataframes:
        raise HTTPException(status_code=422, detail="Ninguna hoja contiene todas las columnas requeridas.")

    try:
        df = pd.concat(dataframes, ignore_index=True)
        df = df.replace({pd.NA: None, np.nan: None, 'nan': None})
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error al procesar el archivo: {str(e)}")

    backup_file = backup_to_excel(db, CodigoPostal)
    
    try:
        db.execute(text("TRUNCATE TABLE servicio_postal"))
        db.commit()
        print("Tabla actualizada.")
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error al eliminar datos existentes o reiniciar el ID: {str(e)}")

    records = df.to_dict(orient='records')
    
    try:
        db.bulk_insert_mappings(CodigoPostal, records)
        db.commit()
        total_nuevos = len(records)
        message = "Datos agregados exitosamente."
        if backup_file:
            message += f" Respaldo guardado en {backup_file}."
        else:
            message += " No se realizó respaldo, no había datos existentes."
        return {"message": message, "total_registros": total_nuevos}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error al insertar datos: {str(e)}")
