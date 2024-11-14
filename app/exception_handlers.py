from fastapi import HTTPException, Request, status
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import List

class JSONAPIErrorDetail(BaseModel):
    status: str
    title: str
    detail: str

class JSONAPIErrorResponse(BaseModel):
    errors: List[JSONAPIErrorDetail]

async def jsonapi_exception_handler(request: Request, exc: HTTPException):
    if exc.status_code == status.HTTP_404_NOT_FOUND:
        title = "Recurso no encontrado"
    elif exc.status_code == status.HTTP_400_BAD_REQUEST:
        title = "Solicitud incorrecta"
    elif exc.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR:
        title = "Error interno del servidor"
    else:
        title = "Error"

    error_response = JSONAPIErrorResponse(
        errors=[
            JSONAPIErrorDetail(
                status=str(exc.status_code),
                title=title,
                detail=exc.detail
            )
        ]
    )
    return JSONResponse(
        status_code=exc.status_code,
        content=error_response.dict()
    )
