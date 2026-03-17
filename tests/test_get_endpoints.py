import os
import pytest
from achaekek import Client
from achaekek.request_types import *

API_KEY = os.environ.get("MANIFOLD_API_KEY", "")

pytestmark = pytest.mark.skipif(not API_KEY, reason="MANIFOLD_API_KEY not set")


@pytest.fixture(scope="module")
def client():
    return Client(api_key=API_KEY)


@pytest.fixture(scope="module")
def me(client: Client):
    r = client.get_me()
    assert r.status_code == 200
    return r.json()


@pytest.fixture(scope="module")
def some_market(client: Client):
    """Fetch a single market to reuse its ID/slug across tests."""
    r = client.get_markets(GetMarketsRequest(limit=1))
    assert r.status_code == 200
    markets = r.json()
    assert len(markets) > 0
    return markets[0]


@pytest.fixture(scope="module")
def some_mc_market(client: Client):
    """Fetch a multiple-choice market so we can test get_answers."""
    r = client.search_markets(
        SearchRequest(term="", contractType="MULTIPLE_CHOICE", limit=1)
    )
    assert r.status_code == 200
    data = r.json()
    assert len(data) > 0
    return data[0]


@pytest.fixture(scope="module")
def some_group(client: Client):
    r = client.get_groups(GetGroupsRequest())
    assert r.status_code == 200
    groups = r.json()
    assert len(groups) > 0
    return groups[0]


# ── User endpoints ──


def test_get_me(me):
    assert "id" in me
    assert "username" in me


def test_get_user(client: Client, me):
    r = client.get_user(me["username"])
    assert r.status_code == 200
    assert r.json()["id"] == me["id"]


def test_get_user_lite(client: Client, me):
    r = client.get_user(me["username"], lite=True)
    assert r.status_code == 200
    assert r.json()["id"] == me["id"]


def test_get_user_by_id(client: Client, me):
    r = client.get_user_by_id(me["id"])
    assert r.status_code == 200
    assert r.json()["username"] == me["username"]


def test_get_user_by_id_lite(client: Client, me):
    r = client.get_user_by_id(me["id"], lite=True)
    assert r.status_code == 200
    assert r.json()["id"] == me["id"]


def test_get_user_portfolio(client: Client, me):
    r = client.get_user_portfolio(GetUserPortfolioRequest(userId=me["id"]))
    assert r.status_code == 200


def test_get_user_portfolio_history(client: Client, me):
    r = client.get_user_portfolio_history(
        GetUserPortfolioHistoryRequest(userId=me["id"], period="monthly")
    )
    assert r.status_code == 200


def test_get_user_contract_metrics_with_contracts(client: Client, me):
    r = client.get_user_contract_metrics_with_contracts(
        GetUserContractMetricsWithContractsRequest(userId=me["id"], limit=5)
    )
    assert r.status_code == 200


def test_get_users(client: Client):
    r = client.get_users(GetUsersRequest(limit=5))
    assert r.status_code == 200
    users = r.json()
    assert isinstance(users, list)
    assert len(users) <= 5


# ── Market endpoints ──


def test_get_markets(client: Client):
    r = client.get_markets(GetMarketsRequest(limit=3))
    assert r.status_code == 200
    assert len(r.json()) <= 3


def test_get_markets_sorted(client: Client):
    r = client.get_markets(
        GetMarketsRequest(limit=2, sort="last-bet-time", order="desc")
    )
    assert r.status_code == 200
    assert isinstance(r.json(), list)


def test_get_market(client: Client, some_market):
    r = client.get_market(some_market["id"])
    assert r.status_code == 200
    assert r.json()["id"] == some_market["id"]


def test_get_market_by_slug(client: Client, some_market):
    slug = some_market.get("slug")
    if slug is None:
        pytest.skip("market has no slug")
    r = client.get_market_by_slug(slug)
    assert r.status_code == 200
    assert r.json()["id"] == some_market["id"]


def test_get_market_probability(client: Client, some_market):
    r = client.get_market_probability(some_market["id"])
    # Some market types may not support this; accept 200 or 400
    assert r.status_code in (200, 400)


def test_get_market_probabilities(client: Client, some_market):
    r = client.get_market_probabilities(
        GetMarketProbabilitiesRequest(ids=[some_market["id"], some_market["id"]])
    )
    assert r.status_code == 200


def test_get_positions(client: Client, some_market):
    r = client.get_positions(some_market["id"], GetPositionsRequest(top=5))
    assert r.status_code == 200
    assert isinstance(r.json(), list)


def test_search_markets(client: Client):
    r = client.search_markets(SearchRequest(term="AI", limit=3))
    assert r.status_code == 200
    assert isinstance(r.json(), list)


def test_search_markets_with_filters(client: Client):
    r = client.search_markets(
        SearchRequest(term="", filter="open", sort="liquidity", limit=2)
    )
    assert r.status_code == 200


# ── Group / topic endpoints ──


def test_get_groups(client: Client):
    r = client.get_groups(GetGroupsRequest())
    assert r.status_code == 200
    assert isinstance(r.json(), list)


def test_get_group(client: Client, some_group):
    slug = some_group.get("slug")
    if slug is None:
        pytest.skip("group has no slug")
    r = client.get_group(slug)
    assert r.status_code == 200
    assert r.json()["id"] == some_group["id"]


def test_get_group_by_id(client: Client, some_group):
    r = client.get_group_by_id(some_group["id"])
    assert r.status_code == 200
    assert r.json()["id"] == some_group["id"]


# ── Bets ──


def test_get_bets(client: Client):
    r = client.get_bets(GetBetsRequest(limit=5))
    assert r.status_code == 200
    assert isinstance(r.json(), list)
    assert len(r.json()) <= 5


def test_get_bets_by_user(client: Client, me):
    r = client.get_bets(GetBetsRequest(userId=me["id"], limit=3))
    assert r.status_code == 200


# ── Comments ──


def test_get_comments(client: Client, some_market):
    r = client.get_comments(GetCommentsRequest(contractId=some_market["id"], limit=5))
    assert r.status_code == 200
    assert isinstance(r.json(), list)


def test_get_comments_for_market(client: Client, some_market):
    r = client.get_comments(GetCommentsRequest(contractId=some_market["id"], limit=3))
    assert r.status_code == 200


# ── Managrams ──


def test_get_managrams(client: Client):
    r = client.get_managrams(GetManagramsRequest(limit=5))
    assert r.status_code == 200


# ── Leagues ──


def test_get_leagues(client: Client):
    r = client.get_leagues(GetLeaguesRequest(season=1))
    assert r.status_code == 200


def test_get_leagues_by_user(client: Client, me):
    r = client.get_leagues(GetLeaguesRequest(userId=me["id"]))
    assert r.status_code == 200


# ── Transactions ──


def test_get_transactions(client: Client):
    r = client.get_transactions(GetTransactionsRequest(limit=5))
    assert r.status_code == 200
    assert isinstance(r.json(), list)


def test_get_transactions_by_token(client: Client):
    r = client.get_transactions(GetTransactionsRequest(token="MANA", limit=3))
    assert r.status_code == 200


# ── Boost history ──


def test_get_boost_history(client: Client):
    r = client.get_boost_history(GetBoostHistoryRequest(limit=5))
    assert r.status_code == 200


# ── Undocumented endpoints ──


def test_get_user_limit_orders_undocumented(client: Client, me):
    r = client.get_user_limit_orders_undocumented(
        GetUserLimitOrdersRequest(userId=me["id"], count=5)
    )
    # Undocumented — accept 200 or graceful failure
    assert r.status_code in (200, 400, 404)


def test_get_markets_by_id_undocumented(client: Client, some_market):
    r = client.get_markets_by_id_undocumented(
        GetMarketsByIdRequest(ids=[some_market["id"]])
    )
    assert r.status_code in (200, 400, 404)


def test_request_loan(client: Client):
    r = client.request_loan()
    # May require specific conditions; accept non-500
    assert r.status_code < 500
