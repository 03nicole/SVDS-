import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from plate_utils import clean_plate_text, is_recent_duplicate


def test_clean_plate_text_strips_punctuation_and_uppercases():
    assert clean_plate_text("baa 1234") == "BAA1234"
    assert clean_plate_text("BAA-1234") == "BAA1234"


def test_clean_plate_text_rejects_too_short_or_too_long():
    assert clean_plate_text("AB1") is None
    assert clean_plate_text("A" * 20) is None


def test_clean_plate_text_rejects_non_alphanumeric_only_input():
    assert clean_plate_text("###???") is None


def test_exact_repeat_within_cooldown_is_a_duplicate():
    recent = []
    assert is_recent_duplicate(recent, "ALX3665", now=0.0, cooldown_seconds=15) is False
    recent.append(("ALX3665", 0.0))
    assert is_recent_duplicate(recent, "ALX3665", now=5.0, cooldown_seconds=15) is True


def test_ocr_jitter_variants_are_treated_as_duplicates():
    """Regression test: a stationary vehicle produces slightly different OCR
    readings almost every frame (ALX3665 / ALK3665 / AL3065 / ...). The old
    exact-match cooldown let every variant bypass it; fuzzy matching should
    catch near-identical readings."""
    recent = [("ALX3665", 0.0)]
    assert is_recent_duplicate(recent, "ALK3665", now=1.0, cooldown_seconds=15) is True
    assert is_recent_duplicate(recent, "AL3065", now=2.0, cooldown_seconds=15) is True


def test_genuinely_different_plate_is_not_a_duplicate():
    recent = [("ALX3665", 0.0)]
    assert is_recent_duplicate(recent, "BCD9999", now=1.0, cooldown_seconds=15) is False


def test_expired_entries_no_longer_count_as_duplicates():
    recent = [("ALX3665", 0.0)]
    assert is_recent_duplicate(recent, "ALX3665", now=20.0, cooldown_seconds=15) is False


def test_expired_entries_are_pruned():
    recent = [("ALX3665", 0.0), ("BCD9999", 10.0)]
    is_recent_duplicate(recent, "ZZZ0000", now=20.0, cooldown_seconds=15)
    # ALX3665 (age 20s) should be pruned, BCD9999 (age 10s) should remain
    assert recent == [("BCD9999", 10.0)]
