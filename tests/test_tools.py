"""agent.tools — 스키마 생성·검증·예산 산수를 결정적으로 검증한다."""

import json

from agent import tools


# ── 스키마 생성 ──


def test_registry_exposes_three_tools():
    names = [t["function"]["name"] for t in tools.tool_schemas()]
    assert names == ["search_places", "estimate_travel_time", "calc_budget"]


def test_schema_carries_constraints():
    schema = {t["function"]["name"]: t["function"] for t in tools.tool_schemas()}
    budget = schema["calc_budget"]["parameters"]["properties"]
    assert budget["nights"]["minimum"] == 0
    assert budget["people"]["minimum"] == 1
    assert set(budget["style"]["enum"]) == {"절약", "보통", "고급"}
    # docstring이 설명으로 실린다
    assert "예산" in schema["calc_budget"]["description"]


# ── 예산 산수 ──


def test_budget_math_default_style():
    result = json.loads(tools.run_tool("calc_budget", '{"nights": 3, "people": 2}'))
    assert result["숙박"] == 120_000 * 3
    assert result["식비"] == 50_000 * 2 * 4  # 3박 4일
    assert result["항공"] == 350_000 * 2
    assert result["합계"] == result["숙박"] + result["식비"] + result["항공"]


def test_budget_without_flight():
    result = json.loads(
        tools.run_tool("calc_budget", '{"nights": 1, "people": 1, "include_flight": false}')
    )
    assert result["항공"] == 0


# ── 검색·이동시간 ──


def test_search_filters_by_category():
    result = json.loads(tools.run_tool("search_places", '{"city": "오사카", "category": "식당"}'))
    assert result["places"]
    assert all(p["category"] == "식당" for p in result["places"])


def test_search_unknown_city_returns_error_not_exception():
    result = json.loads(tools.run_tool("search_places", '{"city": "파리"}'))
    assert "error" in result and "파리" in result["error"]


def test_travel_time_symmetric():
    a = json.loads(tools.run_tool("estimate_travel_time", '{"from_area": "난바", "to_area": "우메다"}'))
    b = json.loads(tools.run_tool("estimate_travel_time", '{"from_area": "우메다", "to_area": "난바"}'))
    assert a["minutes"] == b["minutes"] == 20


# ── 실행 관문의 방어 ──


def test_invalid_args_become_error_result():
    result = json.loads(tools.run_tool("calc_budget", '{"nights": -1, "people": 0}'))
    assert "error" in result and "검증 실패" in result["error"]


def test_unknown_tool_becomes_error_result():
    result = json.loads(tools.run_tool("teleport", "{}"))
    assert "error" in result
