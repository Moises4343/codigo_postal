from fastapi import APIRouter, HTTPException
from app.db.config import VERSION
import os
import json

router = APIRouter()

@router.get(f"/api/{VERSION}/backup-dates")
def get_backup_dates():
    backup_folder = "backups"
    log_file = os.path.join(backup_folder, "backup_logs.json")
    
    if not os.path.exists(log_file):
        raise HTTPException(status_code=404, detail="No se encontraron registros de backups.")
    
    with open(log_file, "r") as file:
        logs = json.load(file)
    
    return {"backups": logs}
