from typing import Literal
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


class DescriptionFormat(Enum):
    HTML = "descriptionHTML"
    MARKDOWN = "descriptionMarkdown"
    JSON = "descriptionJSON"


@dataclass(kw_only=True)
class _CreateMarket:
    question: str
    closeTime: datetime = None
    description: str | tuple[str, DescriptionFormat] = None
    visibility: Literal["public", "unlisted"] = None
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


@dataclass
class CreateMultipleChoiceMarket(_CreateMarket):
    question: str
    answers: list[str]
    addAnswersMode: Literal["DISABLED", "ONLY_CREATORS", "ANYONE"]
    outcomeType: OutcomeType = field(default=OutcomeType.MULTIPLE_CHOICE)
    shouldAnswersSumToOne: bool = True

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


class RequestModel:
    def to_json(self):
        return {k: v for k, v in self.__dict__.items() if v is not None}


@dataclass
class CreateBetRequest(RequestModel):
    amount: int
    contractId: str
    outcome: Literal["YES", "NO"] = field(default="YES")
    limitprob: float = None
    expiresAt: datetime = None

    def to_json(self):
        json = super.to_json()
        json["outcome"] = json["outcome"].value
        if "limitprob" in json:
            json["limitprob"] = round(json["limitprob"], 2)
        if "expiresAt" in json:
            json["expiresAt"] = int(time.mktime(self.expiresAt.timetuple()) * 1000)
        return json


@dataclass
class GetMarketsRequest(RequestModel):
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
class GetBetsRequest(RequestModel):
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
class GetCommentsRequest(RequestModel):
    contractId: str = None
    contractSlug: str = None
    limit: int = None
    page: int = None
    userId: str = None


@dataclass
class SearchRequest(RequestModel):
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


@dataclass
class GetGroupsRequest(RequestModel):
    beforeTime: datetime = None
    availableToUserId: str = None

    def to_json(self):
        json = super.to_json()
        if "beforeTime" in json:
            json["beforeTime"] = int(time.mktime(self.beforeTime.timetuple()) * 1000)
        return json


@dataclass
class GetPositionsRequest(RequestModel):
    order: Literal["shares", "profit"] = None
    top: int = None
    bottom: int = None
    userId: str = None


@dataclass
class GetUsersRequest(RequestModel):
    limit: int = None
    before: str = None


@dataclass
class AwardBountyRequest(RequestModel):
    amount: int
    commentId: str


@dataclass
class ModifyGroupRequest(RequestModel):
    groupId: str
    remove: bool = None


@dataclass
class ResolveBinaryMarket(RequestModel):
    outcome: Literal["YES", "NO", "MKT", "CANCEL"]
    probabilityInt: int = None


@dataclass
class MultipleChoiceResolution:
    answer: str
    pct: int


@dataclass
class ResolveMultipleChoiceMarket(RequestModel):
    outcome: Literal["MKT", "CANCEL"] | int
    resolutions: list[MultipleChoiceResolution] = None

    def to_json(self):
        json = super.to_json()
        if "resolutions" in json:
            json["resolutions"] = [r.__dict__ for r in self.resolutions]
        return json


@dataclass
class ResolveNumericMarket(RequestModel):
    """
    Parameters
    ----------
    outcome : Literal["CANCEL"] | int
        One of `CANCEL`, or a number indicating the selected numeric bucket ID.

    value : float
        The value that the market resolves to.

    probabilityInt : float
        Required if value is present. Should be equal to
        - If log scale: `log10(value - min + 1) / log10(max - min + 1)`
        - Otherwise: `(value - min) / (max - min)`
    """

    outcome: Literal["CANCEL"] | int
    value: float = None
    probabilityInt: float = None


ResolveMarketRequest = (
    ResolveBinaryMarket | ResolveMultipleChoiceMarket | ResolveNumericMarket
)


@dataclass
class SellSharesRequest(RequestModel):
    outcome: Literal["YES", "NO"] = None
    shares: int = None
    answerId: str = None


@dataclass
class SellSharesDPMRequest(RequestModel):
    contractId: str = None
    betId: str = None


@dataclass
class CreateCommentRequest(RequestModel):
    contractId: str
    description: str | tuple[str, Literal["content", "html", "markdown"]] = None

    def to_json(self):
        json = super().to_json()
        if "description" in json and isinstance(self.description, tuple):
            json[self.description[1]] = self.description[0]
            del json["description"]

        return json


@dataclass
class GetManagramsRequest(RequestModel):
    toId: str = None
    fromId: str = None
    limit: int = None
    before: datetime = None
    after: datetime = None

    def to_json(self):
        json = super().to_json()
        if "before" in json:
            json["before"] = int(time.mktime(self.before.timetuple()) * 1000)
        if "after" in json:
            json["after"] = int(time.mktime(self.after.timetuple()) * 1000)
        return json


@dataclass
class GetLeaguesRequest(RequestModel):
    userId: str = None
    season: int = None
    cohort: str = None
