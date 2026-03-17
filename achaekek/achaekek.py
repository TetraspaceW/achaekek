from datetime import datetime
import requests
import logging
from warnings import deprecated

from .request_types import (
    AwardBountyRequest,
    CreateCommentRequest,
    CreateManagramRequest,
    CreateMarketRequest,
    CreateMultiBetRequest,
    GetBetsRequest,
    GetBoostHistoryRequest,
    GetCommentsRequest,
    GetGroupsRequest,
    GetLeaguesRequest,
    GetManagramsRequest,
    GetMarketProbabilitiesRequest,
    GetMarketsByIdRequest,
    GetMarketsRequest,
    GetPositionsRequest,
    GetTransactionsRequest,
    GetUserContractMetricsWithContractsRequest,
    GetUserLimitOrdersRequest,
    GetUserPortfolioHistoryRequest,
    GetUserPortfolioRequest,
    GetUsersRequest,
    ModifyGroupRequest,
    ResolveMarketRequest,
    SearchRequest,
    CreateBetRequest,
    RequestModel,
    SellSharesRequest,
)


class Client:
    def __init__(self, api_key: str, api_url: str = "https://api.manifold.markets"):
        """
        Creates a new Manifold client with a given API key.

        Parameters
        ----------
        api_key : str
            Your Manifold API key, which can be found in the settings on your profile.
        api_url : str, optional
            The URL of the Manifold API. Defaults to the current production Manifold API domain, "https://api.manifold.markets".
        """
        self.api_url = api_url
        self.api_key = api_key

    def _get(
        self, endpoint: str, params: RequestModel = RequestModel()
    ) -> requests.Response:
        logging.info(f"GETting from {self.api_url}{endpoint} with {params.to_json()}")
        return requests.get(
            f"{self.api_url}/v0{endpoint}",
            params=params.to_json(),
            headers={"Authorization": f"Key {self.api_key}"},
        )

    def _get_undocumented(
        self, endpoint: str, params: RequestModel = RequestModel()
    ) -> requests.Response:
        logging.info(f"GETting from {self.api_url}{endpoint} with {params.to_json()}")
        return requests.get(
            f"{self.api_url}{endpoint}",
            params=params.to_json(),
            headers={"Authorization": f"Key {self.api_key}"},
        )

    def _post(
        self, endpoint: str, request: RequestModel = RequestModel()
    ) -> requests.Response:
        logging.info(f"POSTing to {self.api_url}{endpoint} with {request.to_json()}")
        return requests.post(
            f"{self.api_url}/v0{endpoint}",
            json=request.to_json(),
            headers={"Authorization": f"Key {self.api_key}"},
        )

    # GET REQUESTS

    def get_user(self, username: str, lite: bool = False) -> requests.Response:
        return self._get(f"/user/{username}" + ("/lite" if lite else ""))

    def get_user_by_id(self, id: str, lite: bool = False) -> requests.Response:
        return self._get(f"/user/by-id/{id}" + ("/lite" if lite else ""))

    def get_me(self) -> requests.Response:
        return self._get("/me")

    def get_user_portfolio(self, request: GetUserPortfolioRequest) -> requests.Response:
        return self._get("/get-user-portfolio", params=request)

    def get_user_portfolio_history(
        self, request: GetUserPortfolioHistoryRequest
    ) -> requests.Response:
        return self._get("/get-user-portfolio-history", params=request)

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

    def get_market_by_slug(self, market_slug: str) -> requests.Response:
        return self._get(f"/slug/{market_slug}")

    def search_markets(self, request: SearchRequest) -> requests.Response:
        return self._get("/search-markets", params=request)

    def get_market_probability(self, market_id: str) -> requests.Response:
        return self._get(f"/market/{market_id}/prob")

    def get_market_probabilities(
        self,
        request: GetMarketProbabilitiesRequest,
    ) -> requests.Response:
        """
        Gets the probabilities for a list of markets.

        Parameters
        ----------
        request : GetMarketsByIdRequest
            An array of two or more market IDs.

        Returns
        -------
        requests.Response
            The response from the Manifold API.
        """
        return self._get(f"/market-probs", params=request)

    def get_positions(
        self, market_id: str, request: GetPositionsRequest
    ) -> requests.Response:
        return self._get(f"/market/{market_id}/positions", params=request)

    def get_user_contract_metrics_with_contracts(
        self, request: GetUserContractMetricsWithContractsRequest
    ) -> requests.Response:
        return self._get("/get-user-contract-metrics-with-contracts", params=request)

    def get_users(self, request: GetUsersRequest) -> requests.Response:
        return self._get("/users", params=request)

    # POST REQUESTS

    def create_bet(self, request: CreateBetRequest) -> requests.Response:
        return self._post("/bet", request)

    def create_multi_bet(self, request: CreateMultiBetRequest) -> requests.Response:
        return self._post("/bet/multi", request)

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

    def create_comment(self, comment: CreateCommentRequest) -> requests.Response:  #
        return self._post("/comment", comment)

    # MISC REQUESTS

    def get_comments(self, request: GetCommentsRequest) -> requests.Response:
        return self._get("/comments", params=request)

    def get_bets(self, request: GetBetsRequest = GetBetsRequest()) -> requests.Response:
        return self._get("/bets", params=request)

    @deprecated("Use get_transactions instead")
    def get_managrams(
        self, request: GetManagramsRequest = GetManagramsRequest()
    ) -> requests.Response:
        return self._get("/managrams", params=request)

    def create_managram(self, request: CreateManagramRequest) -> requests.Response:
        # amount shoud be > 10 unless you are a mod
        return self._post("/managram", request)

    def get_leagues(self, request: GetLeaguesRequest) -> requests.Response:
        return self._get("/leagues", params=request)

    def get_transactions(self, request: GetTransactionsRequest) -> requests.Response:
        return self._get("/txns", params=request)

    def get_boost_history(self, request: GetBoostHistoryRequest) -> requests.Response:
        return self._get("/get-boost-history", params=request)

    # UNDOCUMENTED REQUESTS

    def get_user_limit_orders_undocumented(
        self, request: GetUserLimitOrdersRequest
    ) -> requests.Response:
        return self._get_undocumented(
            f"/get-user-limit-orders-with-contracts", params=request
        )

    def get_markets_by_id_undocumented(
        self,
        request: GetMarketsByIdRequest = GetMarketsByIdRequest(),
    ) -> requests.Response:
        return self._get_undocumented(f"/markets-by-ids", params=request)

    def request_loan(self):
        return self._get_undocumented(f"/request-loan")

    def get_answer(self, answer_id: str) -> requests.Response:
        return self._get_undocumented(f"/answer/{answer_id}")
