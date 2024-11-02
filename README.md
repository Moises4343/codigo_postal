#Crear archivo .env

DATABASE_URL=mysql+mysqlconnector://usuario:password@localhost/nombre_DB

#Ejecutar el código

Posicionados en "servicios-codigo-postal" abrir la terminal y ejecutar

--> uvicorn app.main:app --reload