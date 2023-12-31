from datetime import datetime
from typing import Any
import requests

from .request_types import (
    AwardBountyRequest,
    CreateCommentRequest,
    CreateMarketRequest,
    GetBetsRequest,
    GetCommentsRequest,
    GetGroupsRequest,
    GetLeaguesRequest,
    GetManagramsRequest,
    GetMarketsRequest,
    GetPositionsRequest,
    GetUsersRequest,
    ModifyGroupRequest,
    ResolveMarketRequest,
    SearchRequest,
    CreateBetRequest,
    RequestModel,
    SellSharesDPMRequest,
    SellSharesRequest,
)


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

    def _get(
        self, endpoint: str, params: RequestModel = RequestModel()
    ) -> requests.Response:
        return requests.get(
            f"{self.API_ROOT}{endpoint}",
            params=params.to_json(),
            headers={"Authorization": f"Key {self.api_key}"},
        )

    def _post(
        self, endpoint: str, request: RequestModel = RequestModel()
    ) -> requests.Response:
        return requests.post(
            f"{self.API_ROOT}{endpoint}",
            json=request.to_json(),
            headers={"Authorization": f"Key {self.api_key}"},
        )

    def get_user(self, username: str) -> requests.Response:
        return self._get(f"/user/{username}")

    def get_user_by_id(self, id: str) -> requests.Response:
        return self._get(f"/user/by-id/{id}")

    def get_me(self) -> requests.Response:
        return self._get("/me")

    def get_groups(
        self, request: GetGroupsRequest = GetGroupsRequest()
    ) -> requests.Response:
        return self._get("/groups", params=request)

    def get_group(self, slug: str) -> requests.Response:
        return self._get(f"/group/{slug}")

    def get_group_by_id(self, id: str) -> requests.Response:
        return self._get(f"/group/by-id/{id}")

    def get_markets(
        self, request: GetMarketsRequest = GetMarketsRequest()
    ) -> requests.Response:
        return self._get("/markets", params=request)

    def get_market(self, market_id: str) -> requests.Response:
        return self._get(f"/market/{market_id}")

    def get_positions(
        self, market_id: str, request: GetPositionsRequest
    ) -> requests.Response:
        return self._get(f"/market/{market_id}/positions", params=request)

    def get_market_by_slug(self, market_slug: str) -> requests.Response:
        return self._get(f"/slug/{market_slug}")

    def search_markets(self, request: SearchRequest) -> requests.Response:
        return self._get("/search-markets", params=request)

    def get_users(self, request: GetUsersRequest) -> requests.Response:
        return self._get("/users", params=request)

    def create_bet(self, request: CreateBetRequest) -> requests.Response:
        return self._post("/bet", params=request)

    def cancel_bet(self, id: str) -> requests.Response:
        return self._post(f"/bet/cancel/{id}")

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
        return self._post("/market", market)

    def create_market_answer(self, market_id: str, text: str) -> requests.Response:
        return self._post(f"/market/{market_id}/answer", {"text": text})

    def add_liquidity(self, market_id: str, amount: int) -> requests.Response:
        return self._post(f"/market/{market_id}/add-liquidity", {"amount": amount})

    def add_bounty(self, market_id: str, amount: int) -> requests.Response:
        return self._post(f"/market/{market_id}/add-bounty", {"amount": amount})

    def award_bounty(
        self, market_id: str, award: AwardBountyRequest
    ) -> requests.Response:
        return self._post(f"/market/{market_id}/award-bounty", award)

    def set_close_time(
        self, market_id: str, close_time: datetime = None
    ) -> requests.Response:
        close_time_millis = int(close_time.timestamp() * 1000) if close_time else None
        return self._post(
            f"/market/{market_id}/close",
            {"closeTime": close_time_millis} if close_time else {},
        )

    def modify_group(
        self, market_id: str, request: ModifyGroupRequest
    ) -> requests.Response:
        return self._post(f"/market/{market_id}/group", request)

    def resolve_market(
        self, market_id: str, resolution: ResolveMarketRequest
    ) -> requests.Response:
        return self._post(f"/market/{market_id}/resolve", resolution)

    def sell_shares(
        self, market_id: str, request: SellSharesRequest
    ) -> requests.Response:
        return self._post(f"/market/{market_id}/sell", request)

    def sell_shares_dpm(
        self, market_id: str, request: SellSharesDPMRequest
    ) -> requests.Response:
        return self._post(f"/sell-shares-dpm", request)

    def create_comment(self, comment: CreateCommentRequest) -> requests.Response:  #
        return self._post("/comment", comment)

    def get_comments(
        self, request: GetCommentsRequest = GetCommentsRequest()
    ) -> requests.Response:
        return self._get("/comments", params=request)

    def get_bets(self, request: GetBetsRequest = GetBetsRequest()) -> requests.Response:
        return self._get("/bets", params=request)

    def get_managrams(
        self, request: GetManagramsRequest = GetManagramsRequest()
    ) -> requests.Response:
        return self._get("/managrams", params=request)

    def get_leagues(
        self, request: GetLeaguesRequest = GetLeaguesRequest()
    ) -> requests.Response:
        return self._get("/leagues", params=request)
