import os
import random
from enum import Enum
from types import MappingProxyType

import attr


class Shape(Enum):
    ROCK = "ROCK"
    PAPER = "PAPER"
    SCISSORS = "SCISSORS"


class Result(Enum):
    WIN = "WIN"
    DRAW = "DRAW"
    LOSS = "LOSS"


MAIN_GAME_MATRIX = MappingProxyType({
    (Shape.ROCK, Shape.SCISSORS): (Result.WIN, Result.LOSS),
    (Shape.ROCK, Shape.ROCK): (Result.DRAW, Result.DRAW),
    (Shape.ROCK, Shape.PAPER): (Result.LOSS, Result.WIN),
    (Shape.PAPER, Shape.ROCK): (Result.WIN, Result.LOSS),
    (Shape.PAPER, Shape.PAPER): (Result.DRAW, Result.DRAW),
    (Shape.PAPER, Shape.SCISSORS): (Result.LOSS, Result.WIN),
    (Shape.SCISSORS, Shape.PAPER): (Result.WIN, Result.LOSS),
    (Shape.SCISSORS, Shape.SCISSORS): (Result.DRAW, Result.DRAW),
    (Shape.SCISSORS, Shape.ROCK): (Result.LOSS, Result.WIN)
})


class BattleRoundResult:

    @staticmethod
    def loss_life_points(res: Result):
        return -random.randint(
            int(os.getenv("MIN_DAMAGE", 10)),
            int(os.getenv("MAX_DAMAGE", 20))) if res == Result.LOSS else 0

    def __get__(self, obj, objtype=None) -> tuple:
        return tuple(map(BattleRoundResult.loss_life_points,
                         MAIN_GAME_MATRIX.get((obj.shape_1, obj.shape_2))))


@attr.s(frozen=True, slots=True)
class BattleRoundLifePoints:
    shape_1: Shape = attr.ib()
    shape_2: Shape = attr.ib()
    result = BattleRoundResult()
