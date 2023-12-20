import requests
from typing import TypedDict
from enum import Enum


class OutcomeType(Enum):
    BINARY = "BINARY"
    MULTIPLE_CHOICE = "MULTIPLE_CHOICE"
    PSEUDO_NUMERIC = "PSEUDO_NUMERIC"
    POLL = "POLL"
    BOUNTIED_QUESTION = "BOUNTIED_QUESTION"


class CreateMarket:
    outcomeType: OutcomeType
    question: str


class CreateBinaryMarket(CreateMarket):
    def __init__(self, question: str, initialProb: int):
        super().__init__(outcomeType=OutcomeType.BINARY, question=question)
        self.initialProb = initialProb


class CreatePseudoNumericMarket(CreateMarket):
    def __init__(
        self,
        question: str,
        min: float,
        max: float,
        isLogScale: bool,
        initialValue: float,
    ):
        super().__init__(outcomeType=OutcomeType.PSEUDO_NUMERIC, question=question)
        self.min = min
        self.max = max
        self.isLogScale = isLogScale
        self.initialValue = initialValue


class AddAnswersMode(Enum):
    DISABLED = "DISABLED"
    ONLY_CREATORS = "ONLY_CREATORS"
    ANYONE = "DISABLED"


class CreateMultipleChoiceMarket(CreateMarket):
    def __init__(
        self, question: str, answers: list[str], addAnswersMode: AddAnswersMode
    ):
        super().__init__(outcomeType=OutcomeType.MULTIPLE_CHOICE, question=question)
        self.answers = answers
        self.addAnswersMode = addAnswersMode


class CreatePollMarket(CreateMarket):
    def __init__(self, question: str, answers: list[str]):
        super().__init__(outcomeType=OutcomeType.POLL, question=question)
        self.answers = answers


class CreateBountiedQuestionMarket(CreateMarket):
    def __init__(self, question: str, totalBounty: int):
        super().__init__(outcomeType=OutcomeType.BOUNTIED_QUESTION, question=question)
        self.totalBounty = totalBounty


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
