from fastapi import FastAPI, HTTPException
from app.routes import codigo_postal, actualizar_codigo
from app.exception_handlers import jsonapi_exception_handler

app = FastAPI()

app.add_exception_handler(HTTPException, jsonapi_exception_handler)

app.include_router(codigo_postal.router)
app.include_router(actualizar_codigo.router)

if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
