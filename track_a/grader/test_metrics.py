"""Unit tests for the closure metrics. Run: python3 -m pytest track_a/grader -q
(or plain `python3 track_a/grader/test_metrics.py`)."""

import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from closure import grade, logic_closure, physics_closure, shape_closure, worst  # noqa: E402


def test_identical_is_exact():
    r = [1.0, 2.0, 3.0]
    assert logic_closure(r, r) == 0.0
    assert grade(0.0, None) == "exact"


def test_delta_value():
    assert math.isclose(logic_closure([1.0, 2.0], [1.0, 1.0]), 0.5)


def test_empty_reference():
    assert logic_closure([0.0], [0.0]) == 0.0
    assert logic_closure([1.0], [0.0]) == math.inf


def test_pi_in_data_units():
    # 1% difference, data known to 10%: pi = 0.1
    pi, used = physics_closure([1.01], [1.0], [5.0], [0.5])
    assert used == 1 and math.isclose(pi, 0.1)


def test_pi_skips_sparse_and_empty_data_bins():
    pi, used = physics_closure([2.0, 1.0, 1.0], [1.0, 1.0, 1.0], [1.0, 0.0, 1.0], [0.1, 0.1, 0.1],
                               entries=[3, 100, 100], min_entries=10)
    assert used == 1 and pi == 0.0


def test_one_migrating_event_is_noise():
    # 50 entries of value 1 each; one event moves out: 2% change, data at 5%.
    # Without noise subtraction pi = 0.4 (wrong); with it, pi = 0.
    pi_raw, _ = physics_closure([49.0], [50.0], [50.0], [2.5])
    pi, _ = physics_closure([49.0], [50.0], [50.0], [2.5], entries=[50])
    assert math.isclose(pi_raw, 0.4) and pi == 0.0


def test_real_shift_survives_noise():
    # 10000 entries, 3% shift (300 events): noise sqrt(300) ~ 17 events, k=2 removes ~35.
    pi, _ = physics_closure([10300.0], [10000.0], [1.0], [0.05], entries=[10000])
    assert 0.5 < pi < 0.6


def test_pi_new_fill_in_empty_reference_bin():
    pi, _ = physics_closure([1.0], [0.0], [1.0], [0.1])
    assert pi == math.inf


def test_grades():
    assert grade(5e-5, None) == "exact"
    assert grade(0.01, 0.05) == "equivalent"
    assert grade(0.01, 0.5) == "wrong"
    assert grade(0.01, None) == "wrong"
    assert worst(["exact", "equivalent", "exact"]) == "equivalent"
    assert worst(["exact", "wrong"]) == "wrong"


def test_shape_ignores_norm():
    assert shape_closure([2.0, 4.0], [1.0, 2.0]) == 0.0
    assert logic_closure([2.0, 4.0], [1.0, 2.0]) == 1.0


if __name__ == "__main__":
    for k, f in list(globals().items()):
        if k.startswith("test_"):
            f()
    print("all metric tests passed")
