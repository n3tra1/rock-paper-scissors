from fastapi_camelcase import CamelModel
from pydantic import Field

from app.bll.game_mechanics import Shape


class ORMModel(CamelModel):

    class Config:
        orm_mode = True
        allow_population_by_field_name = True


class User(ORMModel):
    id: int = Field(..., example=1, alias="userId")


class OfferIn(ORMModel):
    nft_id: int = Field(..., example=1)
    user_id: int = Field(..., example=1)


class Offer(OfferIn):
    id: int = Field(..., example=1, alias="offerId")


class AcceptIn(ORMModel):
    offer_id: int = Field(..., example=1)
    nft_id: int = Field(..., example=1)
    user_id: int = Field(..., example=1)


class Accept(AcceptIn):
    id: int = Field(..., example=1, alias="acceptId")


class StartBattle(ORMModel):
    offer_id: int = Field(..., example=1)
    accept_id: int = Field(..., example=1)


class Battle(ORMModel):
    id: int = Field(..., example=1, alias="battleId")


class BattleTurn(ORMModel):
    user_id: int = Field(..., example=1)
    battle_id: int = Field(..., example=1)
    choice: Shape = Field(..., example=Shape.ROCK)
    round: int = Field(..., example=1)
