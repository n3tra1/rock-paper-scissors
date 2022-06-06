import os
from typing import List, Dict, Optional

from fastapi_sqlalchemy import db
from sqlalchemy import Column, ForeignKey, Integer, Enum
from sqlalchemy.orm import relationship

from app.bll.game_mechanics import Shape, BattleRoundLifePoints
from . import Base


class User(Base):
    __tablename__ = "user"

    id = Column(Integer, primary_key=True, autoincrement=True)


class Offer(Base):
    __tablename__ = "offer"

    id = Column(Integer, primary_key=True, autoincrement=True)
    nft_id = Column(Integer)
    user_id = Column(Integer, ForeignKey("user.id"))
    accept = relationship("Accept", back_populates="offer")
    user = relationship("User")


class Accept(Base):
    __tablename__ = "accept"

    id = Column(Integer, primary_key=True, autoincrement=True)
    offer_id = Column(Integer, ForeignKey("offer.id"))
    nft_id = Column(Integer)
    user_id = Column(Integer, ForeignKey("user.id"))
    battle = relationship("Battle", back_populates="accept")
    offer = relationship("Offer", back_populates="accept")
    user = relationship("User")


class BattleRound(Base):
    __tablename__ = "battle_round"

    id = Column(Integer, primary_key=True, autoincrement=True)
    battle_id = Column(Integer, ForeignKey("battle.id"))
    number = Column(Integer)
    battle = relationship("Battle", back_populates="rounds")
    turns = relationship("UserBattleTurn")
    results = relationship("BattleRoundResult")

    @property
    def users(self) -> List[int]:
        return [t.user_id for t in self.turns]

    @property
    def shapes(self) -> Dict[int, Shape]:
        return {t.user_id: t.shape for t in self.turns}

    def calc_life_points(self):
        is_finish = False
        winner = None
        out = []
        previous_life_points = self.battle.get_previous_life_points(
            self.number)
        shapes = self.shapes
        life_points = tuple(
            zip(shapes.keys(), BattleRoundLifePoints(*shapes.values()).result))
        for user_id, lp in life_points:
            current_lp = previous_life_points[user_id] + lp
            is_finish = is_finish or current_lp < 1
            out.append({"user_id": user_id,
                        "choice": shapes[user_id].value,
                        "life_points": current_lp})
        if is_finish:
            winner = next((u["user_id"] for u in out if u["life_points"] > 0))
        return out, winner

    @property
    def is_everybody_made_turns(self) -> bool:
        return set(self.battle.users) == set(self.users)

    def is_didnt_make_turn(self, user_id: int) -> bool:
        return user_id in self.battle.users and user_id not in self.users


class Battle(Base):
    __tablename__ = "battle"

    id = Column(Integer, primary_key=True, autoincrement=True)
    accept_id = Column(Integer, ForeignKey("accept.id"))
    winner = Column(Integer, ForeignKey("user.id"), nullable=True,
                    default=None)
    rounds = relationship("BattleRound", back_populates="battle",
                          lazy="dynamic")
    accept = relationship("Accept", back_populates="battle")

    @property
    def users(self):
        return self.accept.offer.user_id, self.accept.user_id

    def get_round(self, round_: int) -> Optional[BattleRound]:
        return self.rounds.filter(BattleRound.number == round_).one_or_none()

    def get_previous_life_points(self, round_: int):
        previous_round = self.get_round(round_ - 1)
        if previous_round:
            previous_life_points = {
                r.user_id: r.life_points for r in previous_round.results
            }
        else:
            previous_life_points = {
                user_id: int(os.getenv("LIFE_POINTS", 100))
                for user_id in self.users
            }
        return previous_life_points


class UserBattleTurn(Base):
    __tablename__ = "user_battle_turn"

    id = Column(Integer, primary_key=True, autoincrement=True)
    battle_round_id = Column(Integer, ForeignKey("battle_round.id"))
    user_id = Column(Integer, ForeignKey("user.id"))
    shape = Column(Enum(Shape))


class BattleRoundResult(Base):
    __tablename__ = "battle_round_result"

    id = Column(Integer, primary_key=True, autoincrement=True)
    battle_round_id = Column(Integer, ForeignKey("battle_round.id"))
    user_id = Column(Integer, ForeignKey("user.id"))
    life_points = Column(Integer)


with db():
    Base.metadata.create_all(bind=db.session.get_bind())

