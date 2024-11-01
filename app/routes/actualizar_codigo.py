from fastapi import APIRouter, Depends, HTTPException, UploadFile, File  
from sqlalchemy.orm import Session
from app.db.models import CodigoPostal
from app.db.database import get_db
import pandas as pd
import numpy as np
from io import BytesIO

router = APIRouter()

@router.post("/api/v1/actualizar")
async def actualizar_datos(archivo: UploadFile = File(...), db: Session = Depends(get_db)):
    if archivo.content_type not in [
        "application/vnd.ms-excel", 
        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    ]:
        raise HTTPException(status_code=400, detail="El archivo debe ser de tipo Excel (.xls o .xlsx)")

    columnas_requeridas = {
        'd_codigo': ['d_codigo', 's'],
        'd_asenta': ['d_asenta'],
        'd_tipo_asenta': ['d_tipo_asenta'],
        'D_mnpio': ['D_mnpio'],
        'd_estado': ['d_estado'],
        'd_ciudad': ['d_ciudad'],
        'd_CP': ['d_CP'],
        'c_estado': ['c_estado'],
        'c_oficina': ['c_oficina'],
        'c_CP': ['c_CP'],
        'c_tipo_asenta': ['c_tipo_asenta'],
        'c_mnpio': ['c_mnpio'],
        'id_asenta_cpcons': ['id_asenta_cpcons'],
        'd_zona': ['d_zona'],
        'c_cve_ciudad': ['c_cve_ciudad']
    }

    try:
        contenido = await archivo.read()
        all_sheets = pd.read_excel(BytesIO(contenido), sheet_name=None, dtype=str)
        print("Hojas en el archivo:", all_sheets.keys())

        dataframes = []
        for sheet_name, df_sheet in all_sheets.items():
            if 'd_estado' in df_sheet.columns:
                print(f"La hoja '{sheet_name}' contiene 'd_estado' y será procesada.")

                column_rename = {}
                for std_col, possible_cols in columnas_requeridas.items():
                    for col in possible_cols:
                        if col in df_sheet.columns:
                            column_rename[col] = std_col
                            break  
                df_sheet = df_sheet.rename(columns=column_rename)

                for col in columnas_requeridas.keys():
                    if col not in df_sheet.columns:
                        df_sheet[col] = None

                dataframes.append(df_sheet)
            else:
                print(f"La hoja '{sheet_name}' no contiene la columna 'd_estado' y será omitida.")
        
        if not dataframes:
            raise HTTPException(status_code=400, detail="Ninguna hoja contiene la columna 'd_estado'.")

        df = pd.concat(dataframes, ignore_index=True)

        df = df.replace({pd.NA: None, np.nan: None, 'nan': None})

        if 'd_codigo' in df.columns:
            df['d_codigo'] = df['d_codigo'].astype(str).str.extract('(\d+)') 
            df['d_codigo'] = df['d_codigo'].apply(lambda x: x.lstrip('0') if isinstance(x, str) else x)

        integer_columns = [
            'd_CP', 'c_estado', 'c_oficina', 'c_CP', 
            'c_tipo_asenta', 'c_mnpio', 'id_asenta_cpcons', 'c_cve_ciudad'
        ]
        for col in integer_columns:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce').astype('Int64')

        string_columns = [
            'd_codigo', 'd_asenta', 'd_tipo_asenta', 
            'D_mnpio', 'd_estado', 'd_ciudad', 'd_zona'
        ]
        for col in string_columns:
            if col in df.columns:
                df[col] = df[col].astype(str).replace({'None': None})

        df = df.replace({pd.NA: None})

    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error al procesar el archivo: {str(e)}")

    try:
        db.query(CodigoPostal).delete()
        db.commit()
        print("Datos existentes eliminados de la tabla 'CodigoPostal'.")
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error al eliminar datos existentes: {str(e)}")

    records = df.to_dict(orient='records')

    codigos_postales_nuevos = []
    for record in records:
        record_filtered = {key: record.get(key, None) for key in columnas_requeridas.keys()}

        nuevo_codigo_postal = CodigoPostal(**record_filtered)
        codigos_postales_nuevos.append(nuevo_codigo_postal)
    
    try:
        db.bulk_save_objects(codigos_postales_nuevos)
        db.commit()
        total_nuevos = len(codigos_postales_nuevos)
        return {"message": f"Datos actualizados exitosamente. Se agregaron {total_nuevos} registros nuevos."}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error al insertar nuevos datos: {str(e)}")
