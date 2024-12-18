import os
from datetime import datetime
import pandas as pd
from sqlalchemy.orm import Session
import json

def backup_to_excel(db: Session, table_model, version, backup_folder="backups"):
    os.makedirs(backup_folder, exist_ok=True)
    backup_filename = f"{backup_folder}/{table_model.__tablename__}_backup_{version}_{datetime.now().strftime('%Y-%m-%d_%H.%M.%S')}.xlsx"
    
    records = db.query(table_model).all()
    if not records:
        print("No hay datos en la tabla para respaldar.")
        return None
    
    df_backup = pd.DataFrame([record.__dict__ for record in records]).drop(columns=["_sa_instance_state"], errors="ignore")
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
    
    log_entry = {
        "backup_file": backup_filename,
        "version": version,
        "date": datetime.now().strftime('%Y-%m-%d')
    }
    log_file = os.path.join(backup_folder, "backup_logs.json")
    
    if os.path.exists(log_file):
        with open(log_file, "r") as file:
            logs = json.load(file)
    else:
        logs = []
    
    logs.append(log_entry)
    with open(log_file, "w") as file:
        json.dump(logs, file, indent=4)
    
    print(f"Respaldo realizado exitosamente en {backup_filename}")
    return backup_filename
