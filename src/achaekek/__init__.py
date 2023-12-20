import requests
from enum import Enum
from datetime import datetime
from dataclasses import dataclass


class OutcomeType(Enum):
    BINARY = "BINARY"
    MULTIPLE_CHOICE = "MULTIPLE_CHOICE"
    PSEUDO_NUMERIC = "PSEUDO_NUMERIC"
    POLL = "POLL"
    BOUNTIED_QUESTION = "BOUNTIED_QUESTION"


@dataclass(kw_only=True)
class CreateMarket:
    outcomeType: OutcomeType
    question: str
    closeTime: datetime = None


@dataclass
class CreateBinaryMarket(CreateMarket):
    initialProb: int
    outcomeType = OutcomeType.BINARY


@dataclass
class CreatePseudoNumericMarket(CreateMarket):
    question: str
    min: float
    max: float
    isLogScale: bool
    initialValue: float
    outcomeType = OutcomeType.PSEUDO_NUMERIC


class AddAnswersMode(Enum):
    DISABLED = "DISABLED"
    ONLY_CREATORS = "ONLY_CREATORS"
    ANYONE = "DISABLED"


@dataclass
class CreateMultipleChoiceMarket(CreateMarket):
    question: str
    answers: list[str]
    addAnswersMode: AddAnswersMode
    outcomeType = OutcomeType.MULTIPLE_CHOICE


@dataclass
class CreatePollMarket(CreateMarket):
    answers: list[str]
    outcomeType = OutcomeType.POLL


@dataclass
class CreateBountiedQuestionMarket(CreateMarket):
    totalBounty: int
    outcomeType = OutcomeType.BOUNTIED_QUESTION


CreateMarketRequest = (
    CreateBinaryMarket
    | CreatePseudoNumericMarket
    | CreateMultipleChoiceMarket
    | CreateBountiedQuestionMarket
    | CreatePollMarket
)


class Client:
    def __init__(self, api_key: str):
        self.api_key = api_key

    def create_market(self, market: CreateMarketRequest):
        return requests.post(
            "https://api.manifold.markets/v0/market",
            json=market,
            headers={"Authorization": f"Bearer {self.api_key}"},
        )
