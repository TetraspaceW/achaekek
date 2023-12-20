import requests
from typing import TypedDict
from enum import Enum


class OutcomeType(Enum):
    BINARY = "BINARY"
    MULTIPLE_CHOICE = "MULTIPLE_CHOICE"
    PSEUDO_NUMERIC = "PSEUDO_NUMERIC"
    POLL = "POLL"
    BOUNTIED_QUESTION = "BOUNTIED_QUESTION"


class CreateBaseMarket(TypedDict):
    outcomeType: OutcomeType
    question: str


class CreateBinaryMarket(CreateBaseMarket):
    initialProb: int


class CreatePseudoNumericMarket(CreateBaseMarket):
    min: float
    max: float
    isLogScale: bool
    initialValue: float


class AddAnswersMode(Enum):
    DISABLED = "DISABLED"
    ONLY_CREATORS = "ONLY_CREATORS"
    ANYONE = "DISABLED"


class CreateMultipleChoiceMarket(CreateBaseMarket):
    answers: list[str]
    addAnswersMode: AddAnswersMode


class CreateBountiedQuestionMarket(CreateBaseMarket):
    totalBounty: int


class CreatePollMarket(CreateBaseMarket):
    answers: list[str]


MarketCreationRequest = (
    CreateBinaryMarket
    | CreatePseudoNumericMarket
    | CreateMultipleChoiceMarket
    | CreateBountiedQuestionMarket
    | CreatePollMarket
)


class Client:
    def __init__(self, api_key: str):
        self.api_key = api_key

    def create_market(self, market: MarketCreationRequest):
        return requests.post(
            "https://api.manifold.markets/v0/market",
            json=market,
            headers={"Authorization": f"Bearer {self.api_key}"},
        )
