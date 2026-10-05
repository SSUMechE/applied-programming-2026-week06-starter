import math
import pytest
from ap_week06.adapter import AdapterError
from ap_week06.candidates import supplied_candidates
from ap_week06.model import PlanningSettings
from ap_week06.results import CandidateResult
from ap_week06.selection import evaluate_candidates, select_shortest
from ap_week06.support import make_evaluator


def completed_results(settings=None):
    candidates = supplied_candidates(settings)
    evaluator = make_evaluator(candidates["detour_2"])
    return {key: CandidateResult(evaluator.evaluate(problem), None)
            for key, problem in candidates.items()}


def test_evaluation_keeps_every_id_and_returned_report():
    candidates = supplied_candidates()
    evaluator = make_evaluator(candidates["detour_2"])
    results = evaluate_candidates(candidates, evaluator)
    assert list(results) == list(candidates)
    assert results == completed_results()
    assert results["direct"].report.valid is False
    assert results["direct"].error is None


def test_evaluation_records_one_failure_and_checks_later_candidates():
    candidates = supplied_candidates()
    provided = make_evaluator(candidates["detour_2"])
    class UnavailableForOnePath:
        def evaluate(self, problem):
            if problem is candidates["triangle"]:
                raise AdapterError("announced checker failure")
            return provided.evaluate(problem)
    results = evaluate_candidates(candidates, UnavailableForOnePath())
    assert results["triangle"] == CandidateResult(None, "announced checker failure")
    assert results["corner_cut"].report.valid is True
    assert list(results) == list(candidates)


def test_evaluation_visits_each_candidate_once_without_changing_input():
    candidates = supplied_candidates()
    before = list(candidates.items())
    seen = []
    provided = make_evaluator(candidates["detour_2"])
    class CountingEvaluator:
        def evaluate(self, problem):
            seen.append(problem)
            return provided.evaluate(problem)
    evaluate_candidates(candidates, CountingEvaluator())
    assert seen == list(candidates.values())
    assert list(candidates.items()) == before


def test_evaluation_does_not_hide_unrelated_programming_error():
    class BrokenEvaluator:
        def evaluate(self, problem):
            raise TypeError("programming mistake")
    with pytest.raises(TypeError, match="programming mistake"):
        evaluate_candidates(supplied_candidates(), BrokenEvaluator())


def test_evaluation_of_empty_candidate_mapping_returns_empty_results():
    assert evaluate_candidates({}, None) == {}


def test_selection_improves_first_accepted_and_rejects_shorter_invalid_paths():
    results = completed_results()
    assert select_shortest(results) == "corner_cut"
    assert results["corner_cut"].report.metrics.length_m == pytest.approx(
        2.0 + 2.0 * math.sqrt(2), abs=1e-12)
    assert results["detour_2"].report.metrics.length_m == 8.0
    assert results["direct"].report.metrics.length_m == 4.0
    assert results["direct"].report.valid is False
    assert results["low_detour"].report.valid is False
    assert results["long_zigzag"].report.valid is False


def test_exact_tie_keeps_the_first_id():
    same = completed_results()["corner_cut"]
    assert select_shortest({"first": same, "second": same}) == "first"


def test_failed_record_is_not_an_accepted_candidate():
    results = {"failed": CandidateResult(None, "unavailable"),
               "accepted": completed_results()["triangle"]}
    assert select_shortest(results) == "accepted"


def test_all_rejected_returns_none():
    assert select_shortest(completed_results(PlanningSettings(max_length_m=4.0))) is None


def test_empty_results_return_none():
    assert select_shortest({}) is None


def test_selection_does_not_change_records():
    results = completed_results()
    before = list(results.items())
    select_shortest(results)
    assert list(results.items()) == before
