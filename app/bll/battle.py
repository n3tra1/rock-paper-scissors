from contextlib import suppress
from typing import List, Optional

from fastapi_sqlalchemy import db
from sqlalchemy.exc import NoResultFound

from app.bll.game_mechanics import Shape
from app.db import models


def make_offer(**kwargs) -> models.Offer:
    offer = models.Offer(**kwargs)
    db.session.add(offer)
    db.session.commit()
    return offer


def show_offers() -> List[models.Offer]:
    return db.session.query(models.Offer).all()


def accept(offer_id: int, nft_id: int, user_id: int
           ) -> Optional[models.Accept]:
    with suppress(NoResultFound):
        db.session.query(models.Offer.id).filter(
            models.Offer.id == offer_id,
            models.Offer.user_id != user_id,
        ).one()
        accept_entity = models.Accept(
            offer_id=offer_id, nft_id=nft_id, user_id=user_id
        )
        db.session.add(accept_entity)
        db.session.commit()
        return accept_entity
    return None


def start_battle(offer_id: int, accept_id: int) -> Optional[models.Battle]:
    with suppress(NoResultFound):
        db.session.query(models.Accept).filter(
            models.Accept.id == accept_id,
            models.Accept.offer_id == offer_id
        ).one()
        battle = models.Battle(accept_id=accept_id)
        db.session.add(battle)
        db.session.flush()
        battle_round = models.BattleRound(battle_id=battle.id,
                                          number=1)
        db.session.add(battle_round)
        db.session.commit()
        return battle
    return None


async def make_turn(user_id: int, battle_id: int, choice: Shape, round_: int
                    ) -> Optional[dict]:
    battle = db.session.query(models.Battle).get(battle_id)
    battle_round = battle.get_round(round_)
    if battle_round and not battle_round.is_didnt_make_turn(user_id):
        return None
    db.session.add(models.UserBattleTurn(
        battle_round_id=battle_round.id, user_id=user_id, shape=choice))
    db.session.commit()
    msg = {"battle_id": battle_id, "round": round_, "results": []}
    if battle_round.is_everybody_made_turns:
        msg["results"], winner = battle_round.calc_life_points()
        db.session.add_all((
            models.BattleRoundResult(
                battle_round_id=battle_round.id,
                user_id=result["user_id"],
                life_points=result["life_points"])
            for result in msg["results"]))
        if winner:
            battle.winner = winner
            msg.update({"winner": winner})
        else:
            db.session.add(models.BattleRound(
                battle_id=battle_round.battle_id,
                number=battle_round.number + 1))
        db.session.commit()
    return msg
