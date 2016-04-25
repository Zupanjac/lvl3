

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from database_setup import Base, CategorieItem, Categorie
#from flask.ext.sqlalchemy import SQLAlchemy
from random import randint
import datetime
import random

__author__ = 'Luka Ivkic'

engine = create_engine('sqlite:///item.db')

Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()

# Add categories to the database
categorie1 = Categorie(name="Soccer")
session.add(categorie1)

categorie2 = Categorie(name="Basketball")
session.add(categorie2)

categorie3 = Categorie(name="Baseball")
session.add(categorie3)

categorie4 = Categorie(name="Frisbee")
session.add(categorie4)

categorie5 = Categorie(name="Snowboarding")
session.add(categorie5)

categorie6 = Categorie(name="Rook Climbing")
session.add(categorie6)

categorie7 = Categorie(name="Foosball")
session.add(categorie7)

categorie9 = Categorie(name="Skating")
session.add(categorie9)

categorie10 = Categorie(name="Hockey")
session.add(categorie10)

name = session.query(Categorie).filter_by(name="Soccer").one()

print name.id
catalogitem = CategorieItem(name="Ball",
                            description="A football, soccer ball, or association football "
                                        "ball is the ball used in the sport of association football. ",
                            categorie_id=name.id)
session.add(catalogitem)

catalogitem = CategorieItem(name="Kit",
                            description="In association football, as in a number of other sports, "
                                        "kit refers to the standard equipment"
                                        " and attire worn by players",
                            categorie_id=name.id)
session.add(catalogitem)


name = session.query(Categorie).filter_by(name="Snowboarding").one()

catalogitem = CategorieItem(name="Underwear",
                            description="Thermal underwear is the best apparel to use as a first level of clothing."
                                        " Polypropylene thermal underwear is"
                                        " readily available and does not scratch. ",
                            categorie_id=name.id)
session.add(catalogitem)

catalogitem = CategorieItem(name="Gloves",
                            description="Protect your hands from snow, ice and impacts with padded gloves",
                            categorie_id=name.id)
session.add(catalogitem)

name = session.query(Categorie).filter_by(name="Basketball").one()

catalogitem = CategorieItem(name="Sleeve",
                            description="A basketball sleeve, like the wristband, is an accessory "
                                        "that basketball players wear. Made out of nylon and spandex,"
                                        " it extends from the biceps to the wrist. "
                                        "It is sometimes called a shooter sleeve or an arm sleeve.",
                            categorie_id=name.id)
session.add(catalogitem)

name = session.query(Categorie).filter_by(name="Rook Climbing").one()

catalogitem = CategorieItem(name="Rope",
                            description="Climbing ropes are typically of kernmantle construction, "
                                        "consisting of a core (kern) of long twisted fibres and an outer "
                                        "sheath (mantle) of woven coloured fibres",
                            categorie_id=name.id)
session.add(catalogitem)

catalogitem = CategorieItem(name="Quickdraws",
                            description="Quickdraws (often referred to as draws) "
                                        "are used by climbers to connect ropes to bolt "
                                        "anchors, or to other traditional protection," \
                                        " allowing the rope to move through the anchoring system with minimal friction",
                            categorie_id=name.id)
session.add(catalogitem)

catalogitem = CategorieItem(name="Harnesses",
                            description="A harness is a system used for connecting the rope to the climber",
                            categorie_id=name.id)
session.add(catalogitem)

name = session.query(Categorie).filter_by(name="Hockey").one()

catalogitem = CategorieItem(name="Skates",
                            description="The first thing that you must understand is that there are 2"
                                        " different types of skates - those for figure"
                                        " skating and those for ice hockey.",
                            categorie_id=name.id)
session.add(catalogitem)

catalogitem = CategorieItem(name="Stick",
                            description="Originally made of wood (ash, birch and willow),"
                                        " sticks are now primarily made of carbon fibers and graphite."
                                        " These materials provide added flexibility and durability.",
                            categorie_id=name.id)
session.add(catalogitem)

catalogitem = CategorieItem(name="Pads",
                            description="Equipped with adjustable Velcro straps, "
                                        "these pads cover the forearm, elbows and triceps and help "
                                        "avoid injury from falls and pucks. As with most protective equipment, elbow pads are required in most every league."
                                        " Available in Junior, Intermediate and Adult sizes.",
                            categorie_id=name.id)
session.add(catalogitem)
session.commit()




