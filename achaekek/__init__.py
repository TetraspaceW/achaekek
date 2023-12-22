import requests
from enum import Enum
from datetime import datetime
import time
from dataclasses import dataclass, field


class OutcomeType(Enum):
    BINARY = "BINARY"
    MULTIPLE_CHOICE = "MULTIPLE_CHOICE"
    PSEUDO_NUMERIC = "PSEUDO_NUMERIC"
    POLL = "POLL"
    BOUNTIED_QUESTION = "BOUNTIED_QUESTION"


class Visibility(Enum):
    PUBLIC = "public"
    UNLISTED = "unlisted"


class DescriptionFormat(Enum):
    HTML = "descriptionHTML"
    MARKDOWN = "descriptionMarkdown"
    JSON = "descriptionJSON"


@dataclass(kw_only=True)
class _CreateMarket:
    question: str
    closeTime: datetime = None
    description: str | tuple[str, DescriptionFormat] = None
    visibility: Visibility = None
    groupIds: list[str] = None
    extraLiquidity: int = None

    def to_json(self):
        """
        Converts the create market request dataclass to a JSON dictionary suitable for sending as a request to the Manifold API, reformatting the close time and description as needed.

        Returns
        -------
        json: dict[str, Any]
            The JSON dictionary to be sent as a request.
        """
        json = {k: v for k, v in self.__dict__.items() if v is not None}
        if "outcomeType" in json:
            json["outcomeType"] = self.outcomeType.value
        if "closeTime" in json:
            json["closeTime"] = int(time.mktime(self.closeTime.timetuple()) * 1000)
        if "description" in json and isinstance(self.description, tuple):
            json[self.description[1].value] = self.description[0]
            del json["description"]

        return json


@dataclass
class CreateBinaryMarket(_CreateMarket):
    initialProb: int
    outcomeType: OutcomeType = field(default=OutcomeType.BINARY)


@dataclass
class CreatePseudoNumericMarket(_CreateMarket):
    question: str
    min: float
    max: float
    isLogScale: bool
    initialValue: float
    outcomeType: OutcomeType = field(default=OutcomeType.PSEUDO_NUMERIC)


class AddAnswersMode(Enum):
    DISABLED = "DISABLED"
    ONLY_CREATORS = "ONLY_CREATORS"
    ANYONE = "ANYONE"


@dataclass
class CreateMultipleChoiceMarket(_CreateMarket):
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
class CreatePollMarket(_CreateMarket):
    answers: list[str]
    outcomeType: OutcomeType = field(default=OutcomeType.POLL)


@dataclass
class CreateBountiedQuestionMarket(_CreateMarket):
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
        """
        Creates a new Manifold client with a given API key.

        Parameters
        ----------
        api_key : str
            Your Manifold API key, which can be found at https://manifold.markets/profile.
        """
        self.api_key = api_key

    def create_market(self, market: CreateMarketRequest) -> requests.Response:
        """
        Posts a request to create a market on Manifold.

        Parameters
        ----------
        market : { CreateBinaryMarket, CreatePseudoNumericMarket, CreateMultipleChoiceMarket, CreateBountiedQuestionMarket, CreatePollMarket }
            The market to create. Can be of any of the types supported by Manifold: binary (0% - 100%), pseudo-numeric (minimum to maximum), multiple choice, bountied question, or a poll question.

        Returns
        -------
        requests.Response
            The response from the Manifold API.
        """
        return requests.post(
            "https://api.manifold.markets/v0/market",
            json=market.to_json(),
            headers={"Authorization": f"Key {self.api_key}"},
        )
