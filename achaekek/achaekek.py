from typing import Any, Literal
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


class Outcome(Enum):
    YES = "YES"
    NO = "NO"


@dataclass
class CreateBetRequest:
    amount: int
    contractId: str
    outcome: Outcome = field(default=Outcome.YES)
    limitprob: float = None
    expiresAt: datetime = None

    def to_json(self):
        json = {k: v for k, v in self.__dict__.items() if v is not None}
        json["outcome"] = json["outcome"].value
        if "limitprob" in json:
            json["limitprob"] = round(json["limitprob"], 2)
        if "expiresAt" in json:
            json["expiresAt"] = int(time.mktime(self.expiresAt.timetuple()) * 1000)
        return json


@dataclass
class GetMarketsRequest:
    """
    Request parameters for the get_markets method, to list all markets, defaulting to creation date descending.

    Parameters
    ----------
    limit : int
        Optional. The maximum number of markets to return.
    sort : Literal["created-time", "updated-time", "last-bet-time", "last-comment-time"]
        Optional. The timestamp to sort by. Default is creation time.
    order : Literal["asc", "desc"]
        Optional. The order to sort by. Default is descending.
    before : str
        Optional. The ID of the market before which the list will start.
    userId : str
        Optional. Include only markets created by this user.
    groupId : str
        Optional. Include only markets tagged with this topic.
    """

    limit: int = None
    sort: Literal[
        "created-time", "updated-time", "last-bet-time", "last-comment-time"
    ] = None
    order: Literal["asc", "desc"] = None
    before: str = None
    userId: str = None
    groupId: str = None


@dataclass
class GetBetsRequest:
    userId: str = None
    username: str = None
    contractId: str = None
    contractSlug: str = None
    limit: int = None
    before: str = None
    after: str = None
    kinds: Literal["open-limit"] = None
    order: Literal["asc", "desc"] = None


@dataclass
class GetCommentsRequest:
    contractId: str = None
    contractSlug: str = None
    limit: int = None
    page: int = None
    userId: str = None


@dataclass
class SearchRequest:
    term: str
    sort: Literal["score", "newest", "liquidity"] = None
    filter: Literal[
        "all", "open", "closed", "resolved", "closing-this-month", "closing-next-month"
    ] = None
    contractType: Literal["ALL", "BINARY", "MULTIPLE_CHOICE", "BOUNTY", "POLL"] = None
    topicSlug: str = None
    creatorId: str = None
    limit: int = None
    offset: int = None


class Client:
    API_ROOT = "https://api.manifold.markets/v0"

    def __init__(self, api_key: str):
        """
        Creates a new Manifold client with a given API key.

        Parameters
        ----------
        api_key : str
            Your Manifold API key, which can be found at https://manifold.markets/profile.
        """
        self.api_key = api_key

    def _get(self, endpoint: str, params: dict[str, Any] = None) -> requests.Response:
        return requests.get(
            f"{self.API_ROOT}{endpoint}",
            params=params,
            headers={"Authorization": f"Key {self.api_key}"},
        )

    def _post(self, endpoint: str, json: dict[str, Any] = None) -> requests.Response:
        return requests.post(
            f"{self.API_ROOT}{endpoint}",
            json=json,
            headers={"Authorization": f"Key {self.api_key}"},
        )

    def create_market(self, market: CreateMarketRequest) -> requests.Response:
        """
        Posts a request to create a market on Manifold.

        Parameters
        ----------
        market : CreateMarketRequest
            The market to create. Can be of any of the types supported by Manifold: binary (0% - 100%), pseudo-numeric (minimum to maximum), multiple choice, bountied question, or a poll question.

        Returns
        -------
        requests.Response
            The response from the Manifold API.
        """
        return self._post("/market", market.to_json())

    def get_group(self, slug: str) -> requests.Response:
        return self._get(f"/group/{slug}")

    def get_markets(
        self, request: GetMarketsRequest = GetMarketsRequest()
    ) -> requests.Response:
        return self._get("/markets", params=request.__dict__)

    def get_market(self, market_id: str) -> requests.Response:
        return self._get(f"/market/{market_id}")

    def search_markets(self, request: SearchRequest) -> requests.Response:
        return self._get("/search-markets", params=request.__dict__)

    def create_bet(self, request: CreateBetRequest) -> requests.Response:
        return self._post("/bet", params=request.__dict__)

    def get_comments(
        self, request: GetCommentsRequest = GetCommentsRequest()
    ) -> requests.Response:
        return self._get("/comments", params=request.__dict__)

    def get_bets(self, request: GetBetsRequest = GetBetsRequest()) -> requests.Response:
        return self._get("/bets", params=request.__dict__)

    def get_me(self) -> requests.Response:
        return self._get("/me")

    def get_user(self, username: str) -> requests.Response:
        return self._get(f"/user/{username}")
