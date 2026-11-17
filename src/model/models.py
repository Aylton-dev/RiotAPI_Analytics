from sqlalchemy import Column, Integer, String, ForeignKey, Boolean
from src.repository.database import Base

class Match(Base):
    __tablename__ = 'matches'

    match_id = Column(String, primary_key=True, index=True)
    duration = Column(Integer)
    kindred_winner = Column(Boolean)
    enemy_jungler = Column(String)

class ItemPartida(Base):
    __tablename__ = 'item_partida'

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    match_id = Column(String, ForeignKey('matches.match_id'), index=True)
    item_name = Column(String)
    buy_order = Column(Integer)

class RunaPartida(Base):
    __tablename__ = "runa_partida"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    match_id = Column(String, ForeignKey('matches.match_id'), index=True)
    perk_name = Column(String, index=True)
    category = Column(String)
    style_id = Column(String)
    