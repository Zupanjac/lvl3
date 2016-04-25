from sqlalchemy import Column, ForeignKey, Integer, String, BLOB, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine
import datetime

__author__ = 'Luka Ivkic'

Base = declarative_base()

class Categorie(Base):
    __tablename__ = 'categorie'
    name = Column(String(80), nullable = False)
    id = Column(Integer, primary_key = True)
    @property
    def serialize(self):
        return {
            'id': self.id,
            'name': self.name
        }

class CategorieItem(Base):
    __tablename__ = 'categorie_item'
    name = Column(String(80), nullable = False, unique=True)
    id = Column(Integer, primary_key = True)
    description = Column(String(250))
    dateCreated = Column(DateTime, default=datetime.datetime.utcnow)
    categorie_id = Column(Integer, ForeignKey('categorie.id'))
    categorie = relationship(Categorie)

    @property
    def serialize(self):
        return {
            'name': self.name,
            'description': self.description,
            'dateCreated' : self.dateCreated,
            'id': self.id,
            'categorie_id' : self.categorie_id
        }


engine =create_engine('sqlite:///item.db')

Base.metadata.create_all(engine)
