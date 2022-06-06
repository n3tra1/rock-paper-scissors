# ROCK PAPER SCISSORS

## How to run
### docker-compose
```bash
docker-compose up
```
### uvicorn
```bash
uvicorn app.main:create_app --reload --workers 1 --host 0.0.0.0 --port 8000 --factory
```
## Swagger
http://0.0.0.0:8000/swagger/
## Check websockets
Websockets path: `ws://0.0.0.0:8000/battle/{user_id}/{battle_id}`  
For example:
`ws://0.0.0.0:8000/battle/1/2` for user_id=1 and battle_id=2  
https://addons.mozilla.org/en-US/firefox/addon/websocket-weasel/?utm_source=addons.mozilla.org&utm_medium=referral&utm_content=search