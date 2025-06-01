from geoalchemy2 import Geometry
from pgvector.sqlalchemy import Vector
from sqlalchemy import Column, Integer, Float

from . import Base


class Photo(Base):
    __tablename__ = "photos"

    id = Column(Integer, primary_key=True)
    lat = Column(Float, nullable=False)
    lon = Column(Float, nullable=False)

    geom = Column(Geometry(geometry_type="POINT", srid=4326))
    vlad = Column(Vector(128))
