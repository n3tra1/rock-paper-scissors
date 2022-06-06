import logging
from typing import List

from fastapi import APIRouter, Depends
from fastapi.exceptions import HTTPException
from starlette.websockets import WebSocket

import app.bll.user
import app.bll.battle
import app.schemas as schemas
from app import RedisMessage

router = APIRouter()

logging.basicConfig(filename="log.txt", filemode="a", level=logging.INFO)


@router.post("/user", response_model=schemas.User, status_code=201)
async def make_user():
    return app.bll.user.make_user()


@router.post("/battles_create", response_model=schemas.Offer, status_code=201)
async def create_battle(payload: schemas.OfferIn):
    return app.bll.battle.make_offer(**payload.dict())


@router.get("/battles_list", response_model=List[schemas.Offer])
async def get_battles_list():
    return app.bll.battle.show_offers()


@router.post("/battles/accept",
             response_model=schemas.Accept,
             status_code=201,
             responses={
                 201: {"description": "Created"},
                 400: {"description": "The offer is not found"}
             })
async def accept_battle(payload: schemas.AcceptIn):
    accept = app.bll.battle.accept(**payload.dict())
    if accept:
        return accept
    raise HTTPException(400, f"The offer {payload.offer_id} is not found "
                             f"or you try to accept your offer")


@router.post("/battles_start", response_model=schemas.Battle,
             responses={
                 200: {"description": "Success"},
                 400: {"description": "Cannot start the battle"}
             })
async def start_battle(payload: schemas.StartBattle):
    battle = app.bll.battle.start_battle(**payload.dict())
    if battle:
        return battle
    raise HTTPException(400, f"Cannot start the battle "
                             f"(offer {payload.offer_id}) "
                             f"(accept {payload.accept_id})")


@router.post("/battles_move",
             responses={
                 200: {"description": "Success"},
                 400: {"description": "Something is wrong with your turn"}
             })
async def move_battle(payload: schemas.BattleTurn,
                      redis_m: RedisMessage = Depends(RedisMessage)):
    msg = await app.bll.battle.make_turn(
        payload.user_id,
        payload.battle_id,
        payload.choice,
        payload.round,
    )
    if msg:
        logging.info(f"BATTLES_MOVE: {msg}") if msg["results"] else None
        for result in msg["results"]:
            await redis_m.put_message(result["user_id"], msg["battle_id"], msg)
        return
    raise HTTPException(400, f"Something is wrong with your turn")


@router.websocket("/battle/{user_id}/{battle_id}")
async def websocket_battle(websocket: WebSocket,
                           user_id: int,
                           battle_id: int,
                           redis_m: RedisMessage = Depends(RedisMessage)):
    await websocket.accept()
    run = True
    while run:
        msg = await redis_m.get_message(user_id, battle_id)
        await websocket.send_json(msg)
        run = not msg.get("winner")
        if not run:
            await redis_m.remove_queue(user_id, battle_id)
            await websocket.close()

