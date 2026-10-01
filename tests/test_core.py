from datetime import UTC, datetime

from feature_gates import Flag, GateSet


def test_rollout_is_stable_for_subject():
    gates = GateSet([Flag("search_v2", enabled=True, rollout=50)])
    first = gates.decide("search_v2", subject="u-1")
    second = gates.decide("search_v2", subject="u-1")
    assert (first.enabled, first.reason) == (second.enabled, second.reason)


def test_environment_and_attributes_fail_closed():
    gates = GateSet([Flag("checkout", enabled=True, environments=frozenset({"prod"}), attributes={"plan": "pro"})])
    assert not gates.enabled("checkout", subject="u", environment="staging", attributes={"plan": "pro"})
    assert not gates.enabled("checkout", subject="u", environment="prod", attributes={"plan": "free"})


def test_unknown_and_missing_subject_are_safe():
    gates = GateSet([Flag("x", enabled=True)], clock=lambda: datetime(2026, 1, 1, tzinfo=UTC))
    assert gates.decide("missing").reason == "unknown_flag"
    assert gates.decide("x").reason == "subject_required"
    assert gates.decide("x").evaluated_at.startswith("2026-01-01")
