import os
import pytest
from achaekek import Client
from achaekek.request_types import (
    GetBetsRequest,
    GetCommentsRequest,
    GetGroupsRequest,
    GetLeaguesRequest,
    GetManagramsRequest,
    GetMarketsByIdRequest,
    GetMarketsRequest,
    GetPositionsRequest,
    GetUserLimitOrdersRequest,
    GetUsersRequest,
    SearchRequest,
)

API_KEY = os.environ.get("MANIFOLD_API_KEY", "")

pytestmark = pytest.mark.skipif(not API_KEY, reason="MANIFOLD_API_KEY not set")


@pytest.fixture(scope="module")
def client():
    return Client(api_key=API_KEY)


@pytest.fixture(scope="module")
def me(client):
    r = client.get_me()
    assert r.status_code == 200
    return r.json()


@pytest.fixture(scope="module")
def some_market(client):
    """Fetch a single market to reuse its ID/slug across tests."""
    r = client.get_markets(GetMarketsRequest(limit=1))
    assert r.status_code == 200
    markets = r.json()
    assert len(markets) > 0
    return markets[0]


@pytest.fixture(scope="module")
def some_mc_market(client):
    """Fetch a multiple-choice market so we can test get_answers."""
    r = client.search_markets(
        SearchRequest(term="", contractType="MULTIPLE_CHOICE", limit=1)
    )
    assert r.status_code == 200
    data = r.json()
    assert len(data) > 0
    return data[0]


@pytest.fixture(scope="module")
def some_group(client):
    r = client.get_groups(GetGroupsRequest())
    assert r.status_code == 200
    groups = r.json()
    assert len(groups) > 0
    return groups[0]


# ── User endpoints ──


def test_get_me(me):
    assert "id" in me
    assert "username" in me


def test_get_user(client, me):
    r = client.get_user(me["username"])
    assert r.status_code == 200
    assert r.json()["id"] == me["id"]


def test_get_user_by_id(client, me):
    r = client.get_user_by_id(me["id"])
    assert r.status_code == 200
    assert r.json()["username"] == me["username"]


def test_get_users(client):
    r = client.get_users(GetUsersRequest(limit=5))
    assert r.status_code == 200
    users = r.json()
    assert isinstance(users, list)
    assert len(users) <= 5


# ── Market endpoints ──


def test_get_markets(client):
    r = client.get_markets(GetMarketsRequest(limit=3))
    assert r.status_code == 200
    assert len(r.json()) <= 3


def test_get_markets_sorted(client):
    r = client.get_markets(
        GetMarketsRequest(limit=2, sort="last-bet-time", order="desc")
    )
    assert r.status_code == 200
    assert isinstance(r.json(), list)


def test_get_market(client, some_market):
    r = client.get_market(some_market["id"])
    assert r.status_code == 200
    assert r.json()["id"] == some_market["id"]


def test_get_market_by_slug(client, some_market):
    slug = some_market.get("slug")
    if slug is None:
        pytest.skip("market has no slug")
    r = client.get_market_by_slug(slug)
    assert r.status_code == 200
    assert r.json()["id"] == some_market["id"]


def test_get_market_probability(client, some_market):
    r = client.get_market_probability(some_market["id"])
    # Some market types may not support this; accept 200 or 400
    assert r.status_code in (200, 400)


def test_get_market_probabilities(client, some_market):
    r = client.get_market_probabilities(
        GetMarketsByIdRequest(ids=[some_market["id"]])
    )
    assert r.status_code == 200


def test_get_positions(client, some_market):
    r = client.get_positions(
        some_market["id"], GetPositionsRequest(top=5)
    )
    assert r.status_code == 200
    assert isinstance(r.json(), list)


def test_search_markets(client):
    r = client.search_markets(SearchRequest(term="AI", limit=3))
    assert r.status_code == 200
    assert isinstance(r.json(), list)


def test_search_markets_with_filters(client):
    r = client.search_markets(
        SearchRequest(term="", filter="open", sort="liquidity", limit=2)
    )
    assert r.status_code == 200


# ── Group / topic endpoints ──


def test_get_groups(client):
    r = client.get_groups(GetGroupsRequest())
    assert r.status_code == 200
    assert isinstance(r.json(), list)


def test_get_group(client, some_group):
    slug = some_group.get("slug")
    if slug is None:
        pytest.skip("group has no slug")
    r = client.get_group(slug)
    assert r.status_code == 200
    assert r.json()["id"] == some_group["id"]


def test_get_group_by_id(client, some_group):
    r = client.get_group_by_id(some_group["id"])
    assert r.status_code == 200
    assert r.json()["id"] == some_group["id"]


# ── Bets ──


def test_get_bets(client):
    r = client.get_bets(GetBetsRequest(limit=5))
    assert r.status_code == 200
    assert isinstance(r.json(), list)
    assert len(r.json()) <= 5


def test_get_bets_by_user(client, me):
    r = client.get_bets(GetBetsRequest(userId=me["id"], limit=3))
    assert r.status_code == 200


# ── Comments ──


def test_get_comments(client):
    r = client.get_comments(GetCommentsRequest(limit=5))
    assert r.status_code == 200
    assert isinstance(r.json(), list)


def test_get_comments_for_market(client, some_market):
    r = client.get_comments(GetCommentsRequest(contractId=some_market["id"], limit=3))
    assert r.status_code == 200


# ── Managrams ──


def test_get_managrams(client):
    r = client.get_managrams(GetManagramsRequest(limit=5))
    assert r.status_code == 200


# ── Leagues ──


def test_get_leagues(client):
    r = client.get_leagues(GetLeaguesRequest())
    assert r.status_code == 200


def test_get_leagues_by_user(client, me):
    r = client.get_leagues(GetLeaguesRequest(userId=me["id"]))
    assert r.status_code == 200


# ── Answers ──


def test_get_answers(client, some_mc_market):
    r = client.get_answers(some_mc_market["id"])
    assert r.status_code == 200
    answers = r.json()
    assert isinstance(answers, list)


def test_get_answer(client, some_mc_market):
    answers_resp = client.get_answers(some_mc_market["id"])
    if answers_resp.status_code != 200:
        pytest.skip("could not fetch answers")
    answers = answers_resp.json()
    if not answers:
        pytest.skip("no answers on market")
    r = client.get_answer(answers[0]["id"])
    assert r.status_code == 200
    assert r.json()["id"] == answers[0]["id"]


# ── Undocumented endpoints ──


def test_get_user_limit_orders_undocumented(client, me):
    r = client.get_user_limit_orders_undocumented(
        GetUserLimitOrdersRequest(userId=me["id"], count=5)
    )
    # Undocumented — accept 200 or graceful failure
    assert r.status_code in (200, 400, 404)


def test_get_markets_by_id_undocumented(client, some_market):
    r = client.get_markets_by_id_undocumented(
        GetMarketsByIdRequest(ids=[some_market["id"]])
    )
    assert r.status_code in (200, 400, 404)


def test_request_loan(client):
    r = client.request_loan()
    # May require specific conditions; accept non-500
    assert r.status_code < 500
