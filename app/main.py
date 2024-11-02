from fastapi import FastAPI, HTTPException, Request, status
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import List
from app.routes import codigo_postal, actualizar_codigo


app = FastAPI()

class JSONAPIErrorDetail(BaseModel):
    status: str
    title: str
    detail: str

class JSONAPIErrorResponse(BaseModel):
    errors: List[JSONAPIErrorDetail]

@app.exception_handler(HTTPException)
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

app.include_router(codigo_postal.router)
app.include_router(actualizar_codigo.router)

if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
