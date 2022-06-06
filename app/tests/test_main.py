import random


def test_random_integration(test_app):
    first_user_id = test_app.post("/user").json()["userId"]
    second_user_id = test_app.post("/user").json()["userId"]
    offer_id = test_app.post("/battles_create",
                             json={"userId": first_user_id, "nftId": 1}
                             ).json()["offerId"]
    accept_id = test_app.post("/battles/accept",
                              json={"userId": second_user_id,
                                    "nftId": 2,
                                    "offerId": offer_id}
                              ).json()["acceptId"]
    battle_id = test_app.post("/battles_start",
                              json={"offerId": offer_id,
                                    "acceptId": accept_id}
                              ).json()["battleId"]
    first_payload = {"userId": first_user_id, "battleId": battle_id}
    second_payload = {"userId": second_user_id, "battleId": battle_id}
    round_ = 0
    have_winner = False
    ws_path_1 = f"/battle/{first_user_id}/{battle_id}"
    ws_path_2 = f"/battle/{second_user_id}/{battle_id}"
    with test_app.websocket_connect(ws_path_1) as ws1:
        with test_app.websocket_connect(ws_path_2) as ws2:
            while not have_winner:
                round_ += 1
                first_payload.update({
                    "choice": random.choice(("ROCK", "PAPER", "SCISSORS")),
                    "round": round_,
                })
                second_payload.update({
                    "choice": random.choice(("ROCK", "PAPER", "SCISSORS")),
                    "round": round_,
                })
                res = test_app.post("/battles_move", json=first_payload)
                assert res.status_code == 200
                res = test_app.post("/battles_move", json=second_payload)
                assert res.status_code == 200
                data = ws1.receive_json()
                assert data == ws2.receive_json()
                have_winner = bool(data.get("winner"))
