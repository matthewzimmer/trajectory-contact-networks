from app.lib.search import FindNeedleOp


def test_find_needle():
    haystack = [11, 24, 55, 39, 48]
    assert FindNeedleOp(haystack, needle=11).output() == 0
    assert FindNeedleOp(haystack, needle=24).output() == 1
    assert FindNeedleOp(haystack, needle=55).output() == 2
    assert FindNeedleOp(haystack, needle=39).output() == 3
    assert FindNeedleOp(haystack, needle=48).output() == 4
    assert FindNeedleOp(haystack, needle=66).output() == -1
