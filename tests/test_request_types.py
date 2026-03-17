import pytest
from datetime import datetime
from achaekek.request_types import (
    CreateBinaryMarket,
    CreatePseudoNumericMarket,
    CreateMultipleChoiceMarket,
    CreatePollMarket,
    CreateBountiedQuestionMarket,
    CreateBetRequest,
    CreateCommentRequest,
    GetGroupsRequest,
    GetManagramsRequest,
    GetMarketsRequest,
    GetBetsRequest,
    GetCommentsRequest,
    GetPositionsRequest,
    GetUsersRequest,
    GetLeaguesRequest,
    GetUserLimitOrdersRequest,
    GetMarketProbabilitiesRequest,
    SearchRequest,
    AwardBountyRequest,
    ModifyGroupRequest,
    ResolveBinaryMarket,
    ResolveMultipleChoiceMarket,
    ResolveNumericMarket,
    MultipleChoiceResolution,
    SellSharesRequest,
    SellSharesDPMRequest,
    CreateManagramRequest,
    RequestModel,
    DescriptionFormat,
)
import time


# ── RequestModel base ──


def test_request_model_empty():
    rm = RequestModel()
    assert rm.to_json() == {}


# ── _CreateMarket.to_json() ──


def test_create_binary_market_minimal():
    m = CreateBinaryMarket(question="Will it rain?", initialProb=50)
    j = m.to_json()
    assert j["question"] == "Will it rain?"
    assert j["initialProb"] == 50
    assert j["outcomeType"] == "BINARY"
    assert "closeTime" not in j
    assert "description" not in j
    assert "visibility" not in j
    assert "groupIds" not in j
    assert "extraLiquidity" not in j


def test_create_binary_market_close_time():
    dt = datetime(2025, 6, 15, 12, 0, 0)
    m = CreateBinaryMarket(question="Q", initialProb=50, closeTime=dt)
    j = m.to_json()
    expected_ms = int(time.mktime(dt.timetuple()) * 1000)
    assert j["closeTime"] == expected_ms


def test_create_binary_market_description_string():
    m = CreateBinaryMarket(question="Q", initialProb=50, description="plain text")
    j = m.to_json()
    assert j["description"] == "plain text"


def test_create_binary_market_description_tuple_html():
    m = CreateBinaryMarket(
        question="Q",
        initialProb=50,
        description=("<b>bold</b>", DescriptionFormat.HTML),
    )
    j = m.to_json()
    assert j["descriptionHTML"] == "<b>bold</b>"
    assert "description" not in j


def test_create_binary_market_description_tuple_markdown():
    m = CreateBinaryMarket(
        question="Q",
        initialProb=50,
        description=("# Heading", DescriptionFormat.MARKDOWN),
    )
    j = m.to_json()
    assert j["descriptionMarkdown"] == "# Heading"
    assert "description" not in j


def test_create_binary_market_description_tuple_json():
    m = CreateBinaryMarket(
        question="Q",
        initialProb=50,
        description=('{"type":"doc"}', DescriptionFormat.JSON),
    )
    j = m.to_json()
    assert j["descriptionJSON"] == '{"type":"doc"}'
    assert "description" not in j


def test_create_binary_market_all_optional_fields():
    dt = datetime(2025, 1, 1)
    m = CreateBinaryMarket(
        question="Q",
        initialProb=75,
        closeTime=dt,
        description="desc",
        visibility="unlisted",
        groupIds=["g1", "g2"],
        extraLiquidity=100,
    )
    j = m.to_json()
    assert j["visibility"] == "unlisted"
    assert j["groupIds"] == ["g1", "g2"]
    assert j["extraLiquidity"] == 100


# ── CreatePseudoNumericMarket ──


def test_create_pseudo_numeric_market():
    m = CreatePseudoNumericMarket(
        question="How many?", min=0, max=100, isLogScale=False, initialValue=50
    )
    j = m.to_json()
    assert j["outcomeType"] == "PSEUDO_NUMERIC"
    assert j["min"] == 0
    assert j["max"] == 100
    assert j["isLogScale"] is False
    assert j["initialValue"] == 50


# ── CreateMultipleChoiceMarket ──


def test_create_multiple_choice_market_default_sum_to_one():
    m = CreateMultipleChoiceMarket(question="Pick one", answers=["A", "B", "C"])
    j = m.to_json()
    assert j["outcomeType"] == "MULTIPLE_CHOICE"
    assert j["answers"] == ["A", "B", "C"]
    assert j["addAnswersMode"] == "DISABLED"
    # shouldAnswersSumToOne=True (default) should be removed
    assert "shouldAnswersSumToOne" not in j


def test_create_multiple_choice_market_sum_to_one_false():
    m = CreateMultipleChoiceMarket(
        question="Pick one", answers=["A", "B"], shouldAnswersSumToOne=False
    )
    j = m.to_json()
    assert j["shouldAnswersSumToOne"] is False


def test_create_multiple_choice_market_add_answers_anyone():
    m = CreateMultipleChoiceMarket(question="Q", answers=["A"], addAnswersMode="ANYONE")
    j = m.to_json()
    assert j["addAnswersMode"] == "ANYONE"


# ── CreatePollMarket ──


def test_create_poll_market():
    m = CreatePollMarket(question="Favourite?", answers=["X", "Y"])
    j = m.to_json()
    assert j["outcomeType"] == "POLL"
    assert j["answers"] == ["X", "Y"]


# ── CreateBountiedQuestionMarket ──


def test_create_bountied_question_market():
    m = CreateBountiedQuestionMarket(question="How?", totalBounty=500)
    j = m.to_json()
    assert j["outcomeType"] == "BOUNTIED_QUESTION"
    assert j["totalBounty"] == 500


# ── CreateBetRequest ──


def test_create_bet_request_minimal():
    r = CreateBetRequest(amount=100, contractId="abc123")
    j = r.to_json()
    assert j["amount"] == 100
    assert j["contractId"] == "abc123"
    assert j["outcome"] == "YES"
    assert "limitprob" not in j
    assert "expiresAt" not in j


def test_create_bet_request_limitprob_rounding():
    r = CreateBetRequest(amount=10, contractId="c1", limitprob=0.12345)
    j = r.to_json()
    assert j["limitprob"] == 0.12


def test_create_bet_request_expires_at():
    dt = datetime(2025, 3, 1, 18, 30, 0)
    r = CreateBetRequest(amount=10, contractId="c1", expiresAt=dt)
    j = r.to_json()
    expected_ms = int(time.mktime(dt.timetuple()) * 1000)
    assert j["expiresAt"] == expected_ms


def test_create_bet_request_outcome_no():
    r = CreateBetRequest(amount=10, contractId="c1", outcome="NO")
    j = r.to_json()
    assert j["outcome"] == "NO"


def test_create_bet_request_answer_id():
    r = CreateBetRequest(amount=10, contractId="c1", answerId="ans1")
    j = r.to_json()
    assert j["answerId"] == "ans1"


# ── GetMarketsRequest ──


def test_get_markets_request_empty():
    r = GetMarketsRequest()
    assert r.to_json() == {}


def test_get_markets_request_all_fields():
    r = GetMarketsRequest(
        limit=10,
        sort="updated-time",
        order="asc",
        before="id1",
        userId="u1",
        groupId="g1",
    )
    j = r.to_json()
    assert j == {
        "limit": 10,
        "sort": "updated-time",
        "order": "asc",
        "before": "id1",
        "userId": "u1",
        "groupId": "g1",
    }


# ── GetBetsRequest ──


def test_get_bets_request_partial():
    r = GetBetsRequest(userId="u1", limit=5, kinds="open-limit")
    j = r.to_json()
    assert j["userId"] == "u1"
    assert j["limit"] == 5
    assert j["kinds"] == "open-limit"
    assert "username" not in j


# ── GetCommentsRequest ──


def test_get_comments_request():
    r = GetCommentsRequest(contractId="c1", limit=20)
    j = r.to_json()
    assert j == {"contractId": "c1", "limit": 20}


# ── SearchRequest ──


def test_search_request_minimal():
    r = SearchRequest(term="AI")
    j = r.to_json()
    assert j["term"] == "AI"
    assert "sort" not in j


def test_search_request_full():
    r = SearchRequest(
        term="AI",
        sort="newest",
        filter="open",
        contractType="BINARY",
        limit=5,
        offset=10,
    )
    j = r.to_json()
    assert j["sort"] == "newest"
    assert j["filter"] == "open"
    assert j["contractType"] == "BINARY"
    assert j["limit"] == 5
    assert j["offset"] == 10


# ── GetGroupsRequest ──


def test_get_groups_request_before_time():
    dt = datetime(2025, 4, 10, 8, 0, 0)
    r = GetGroupsRequest(beforeTime=dt)
    j = r.to_json()
    expected_ms = int(time.mktime(dt.timetuple()) * 1000)
    assert j["beforeTime"] == expected_ms


def test_get_groups_request_empty():
    r = GetGroupsRequest()
    assert r.to_json() == {}


# ── GetPositionsRequest ──


def test_get_positions_request():
    r = GetPositionsRequest(order="profit", top=10)
    j = r.to_json()
    assert j == {"order": "profit", "top": 10}


# ── GetUsersRequest ──


def test_get_users_request():
    r = GetUsersRequest(limit=50, before="uid")
    j = r.to_json()
    assert j == {"limit": 50, "before": "uid"}


# ── AwardBountyRequest ──


def test_award_bounty_request():
    r = AwardBountyRequest(amount=100, commentId="cmt1")
    j = r.to_json()
    assert j == {"amount": 100, "commentId": "cmt1"}


# ── ModifyGroupRequest ──


def test_modify_group_request():
    r = ModifyGroupRequest(groupId="g1", remove=True)
    j = r.to_json()
    assert j == {"groupId": "g1", "remove": True}


def test_modify_group_request_no_remove():
    r = ModifyGroupRequest(groupId="g1")
    j = r.to_json()
    assert j == {"groupId": "g1"}


# ── ResolveBinaryMarket ──


def test_resolve_binary_market_yes():
    r = ResolveBinaryMarket(outcome="YES")
    j = r.to_json()
    assert j == {"outcome": "YES"}


def test_resolve_binary_market_mkt_with_prob():
    r = ResolveBinaryMarket(outcome="MKT", probabilityInt=60)
    j = r.to_json()
    assert j == {"outcome": "MKT", "probabilityInt": 60}


# ── ResolveMultipleChoiceMarket ──


def test_resolve_multiple_choice_cancel():
    r = ResolveMultipleChoiceMarket(outcome="CANCEL")
    j = r.to_json()
    assert j == {"outcome": "CANCEL"}


def test_resolve_multiple_choice_single_answer():
    r = ResolveMultipleChoiceMarket(outcome=42)
    j = r.to_json()
    assert j == {"outcome": 42}


def test_resolve_multiple_choice_mkt_with_resolutions():
    r = ResolveMultipleChoiceMarket(
        outcome="MKT",
        resolutions=[
            MultipleChoiceResolution(answer="A", pct=70),
            MultipleChoiceResolution(answer="B", pct=30),
        ],
    )
    j = r.to_json()
    assert j["outcome"] == "MKT"
    assert j["resolutions"] == [
        {"answer": "A", "pct": 70},
        {"answer": "B", "pct": 30},
    ]


# ── ResolveNumericMarket ──


def test_resolve_numeric_market_cancel():
    r = ResolveNumericMarket(outcome="CANCEL")
    j = r.to_json()
    assert j == {"outcome": "CANCEL"}


def test_resolve_numeric_market_with_value():
    r = ResolveNumericMarket(outcome=5, value=42.5, probabilityInt=0.75)
    j = r.to_json()
    assert j == {"outcome": 5, "value": 42.5, "probabilityInt": 0.75}


# ── SellSharesRequest ──


def test_sell_shares_request():
    r = SellSharesRequest(outcome="YES", shares=10, answerId="a1")
    j = r.to_json()
    assert j == {"outcome": "YES", "shares": 10, "answerId": "a1"}


def test_sell_shares_request_empty():
    r = SellSharesRequest()
    assert r.to_json() == {}


# ── SellSharesDPMRequest ──


def test_sell_shares_dpm_request():
    r = SellSharesDPMRequest(contractId="c1", betId="b1")
    j = r.to_json()
    assert j == {"contractId": "c1", "betId": "b1"}


# ── CreateCommentRequest ──


def test_create_comment_plain_description():
    r = CreateCommentRequest(contractId="c1", description="hello")
    j = r.to_json()
    assert j["contractId"] == "c1"
    assert j["description"] == "hello"


def test_create_comment_tuple_markdown():
    r = CreateCommentRequest(contractId="c1", description=("# Hi", "markdown"))
    j = r.to_json()
    assert j["markdown"] == "# Hi"
    assert "description" not in j
    assert j["contractId"] == "c1"


def test_create_comment_tuple_html():
    r = CreateCommentRequest(contractId="c1", description=("<p>Hi</p>", "html"))
    j = r.to_json()
    assert j["html"] == "<p>Hi</p>"
    assert "description" not in j


def test_create_comment_tuple_content():
    r = CreateCommentRequest(contractId="c1", description=('{"type":"doc"}', "content"))
    j = r.to_json()
    assert j["content"] == '{"type":"doc"}'
    assert "description" not in j


def test_create_comment_no_description():
    r = CreateCommentRequest(contractId="c1")
    j = r.to_json()
    assert j == {"contractId": "c1"}


# ── GetManagramsRequest ──


def test_get_managrams_request_empty():
    r = GetManagramsRequest()
    assert r.to_json() == {}


def test_get_managrams_request_with_dates():
    before = datetime(2025, 6, 1, 0, 0, 0)
    after = datetime(2025, 1, 1, 0, 0, 0)
    r = GetManagramsRequest(toId="u1", before=before, after=after)
    j = r.to_json()
    assert j["toId"] == "u1"
    assert j["before"] == int(time.mktime(before.timetuple()) * 1000)
    assert j["after"] == int(time.mktime(after.timetuple()) * 1000)


# ── GetLeaguesRequest ──


def test_get_leagues_request():
    r = GetLeaguesRequest(season=3, cohort="diamond")
    j = r.to_json()
    assert j == {"season": 3, "cohort": "diamond"}


def test_get_leagues_request_user_id_only():
    r = GetLeaguesRequest(userId="u1")
    j = r.to_json()
    assert j == {"userId": "u1"}


def test_get_leagues_request_requires_user_or_season():
    with pytest.raises(ValueError, match="userId or season"):
        GetLeaguesRequest()

    with pytest.raises(ValueError, match="userId or season"):
        GetLeaguesRequest(cohort="diamond")


# ── GetUserLimitOrdersRequest ──


def test_get_user_limit_orders_request():
    r = GetUserLimitOrdersRequest(userId="u1", count=20, includeExpired=True)
    j = r.to_json()
    assert j == {"userId": "u1", "count": 20, "includeExpired": True}


# ── GetMarketsByIdRequest ──


def test_get_markets_by_id_request():
    r = GetMarketProbabilitiesRequest(ids=["m1", "m2"])
    j = r.to_json()
    assert j == {"ids": ["m1", "m2"]}


def test_get_market_probabilities_request_too_few_ids():
    with pytest.raises(ValueError, match="at least 2"):
        GetMarketProbabilitiesRequest()

    with pytest.raises(ValueError, match="at least 2"):
        GetMarketProbabilitiesRequest(ids=["only_one"])


# ── CreateManagramRequest ──


def test_create_managram_request():
    r = CreateManagramRequest(amount=100, toIds=["u1", "u2"], message="thanks")
    j = r.to_json()
    assert j == {
        "amount": 100,
        "toIds": ["u1", "u2"],
        "message": "thanks",
        "token": "M$",
    }


def test_create_managram_request_cash():
    r = CreateManagramRequest(amount=50, toIds=["u1"], token="CASH")
    j = r.to_json()
    assert j["token"] == "CASH"
