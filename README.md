#Crear la base de datos y tabla con los columnas
--> Revisar archivo cp.sql

#Crear archivo .env

--> DATABASE_URL=mysql+mysqlconnector://usuario:password@localhost/sepomex

#Ejecutar el código

Posicionados en "servicios-codigo-postal" abrir la terminal y ejecutar

--> uvicorn app.main:app --reload