import pytest

from app.tags import TAG_MAX, normalize_tag


@pytest.mark.parametrize(
    "raw, expected",
    [
        ("Горячий", "горячий"),
        ("  горячий  ", "горячий"),
        ("#Горячий", "горячий"),
        ("# горячий", "горячий"),
        ("Горячий   клиент", "горячий клиент"),
        ("B2B", "b2b"),
        ("", ""),
        ("   ", ""),
        ("#", ""),
    ],
)
def test_normalize_tag(raw, expected):
    assert normalize_tag(raw) == expected


def test_normalize_tag_limits_length():
    assert len(normalize_tag("а" * (TAG_MAX + 10))) == TAG_MAX
