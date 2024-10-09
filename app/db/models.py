from sqlalchemy import Column, Integer, String
from app.db.database import Base

class CodigoPostal(Base):
    __tablename__ = 'servicio_postal'
    
    id = Column(Integer, primary_key=True, index=True)
    d_codigo = Column(String(10), index=True)
    d_asenta = Column(String(70))
    d_tipo_asenta = Column(String(50))
    D_mnpio = Column(String(50))
    d_estado = Column(String(50))
    d_ciudad = Column(String(50))
    d_CP = Column(String(10))
    c_estado = Column(String(5))
    c_oficina = Column(String(50))
    c_CP = Column(String(10))
    c_tipo_asenta = Column(String(50))
    c_mnpio = Column(String(50))
    id_asenta_cpcons = Column(String(5))
    d_zona = Column(String(50))
    c_cve_ciudad = Column(String(5))



        