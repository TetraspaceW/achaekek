import requests
from enum import Enum
from datetime import datetime
from dataclasses import dataclass, field


class OutcomeType(Enum):
    BINARY = "BINARY"
    MULTIPLE_CHOICE = "MULTIPLE_CHOICE"
    PSEUDO_NUMERIC = "PSEUDO_NUMERIC"
    POLL = "POLL"
    BOUNTIED_QUESTION = "BOUNTIED_QUESTION"


@dataclass(kw_only=True)
class CreateMarket:
    question: str
    closeTime: datetime = None

    def to_json(self):
        json = {k: v for k, v in self.__dict__.items() if v is not None}
        if "outcomeType" in json:
            json["outcomeType"] = json["outcomeType"].value

        return json


@dataclass
class CreateBinaryMarket(CreateMarket):
    initialProb: int
    outcomeType: OutcomeType = field(default=OutcomeType.BINARY)


@dataclass
class CreatePseudoNumericMarket(CreateMarket):
    question: str
    min: float
    max: float
    isLogScale: bool
    initialValue: float
    outcomeType: OutcomeType = field(default=OutcomeType.PSEUDO_NUMERIC)


class AddAnswersMode(Enum):
    DISABLED = "DISABLED"
    ONLY_CREATORS = "ONLY_CREATORS"
    ANYONE = "DISABLED"


@dataclass
class CreateMultipleChoiceMarket(CreateMarket):
    question: str
    answers: list[str]
    addAnswersMode: AddAnswersMode
    outcomeType: OutcomeType = field(default=OutcomeType.MULTIPLE_CHOICE)

    def to_json(self):
        dictionary = super().to_json()
        if "addAnswersMode" in dictionary:
            dictionary["addAnswersMode"] = dictionary["addAnswersMode"].value
        return dictionary


@dataclass
class CreatePollMarket(CreateMarket):
    answers: list[str]
    outcomeType: OutcomeType = field(default=OutcomeType.POLL)


@dataclass
class CreateBountiedQuestionMarket(CreateMarket):
    totalBounty: int
    outcomeType: OutcomeType = field(default=OutcomeType.BOUNTIED_QUESTION)


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
            json=market.to_json(),
            headers={"Authorization": f"Key {self.api_key}"},
        )


if __name__ == "__main__":
    market = CreateBinaryMarket(
        question="Will the library that Tetraspace used to create this question be in a releasable state by the end of February?",
        initialProb=50,
    )
    client = Client("")
    print(market.to_json())
    response = client.create_market(market)
    print(response)
    print(response.json())
