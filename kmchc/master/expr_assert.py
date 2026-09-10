"""expr_assert — 등재 전 필수 검증.
answer_expr 및 distractor expr가 placeholder가 아니고 실제로 평가 가능한지 확인한다.
계수 논리형(합·질량·곱만 aexpr)이므로 expr가 없는 항목은 통과.
"""
import re

_PLACEHOLDER = re.compile(r'(?:\bX\b|\bTODO\b|\bFIXME\b|\?\?+|__|placeholder|계산식|여기에)', re.IGNORECASE)


def _check_one(expr, ctx):
    if expr is None:
        return
    if not isinstance(expr, str) or not expr.strip():
        raise AssertionError(f"[expr_assert] 빈 expr: {ctx}")
    if _PLACEHOLDER.search(expr):
        raise AssertionError(f"[expr_assert] placeholder 흔적: {ctx} -> {expr!r}")
    # 평가 가능성(사칙연산·정수만). × 는 * 로 치환.
    safe = expr.replace('×', '*').replace('÷', '/')
    if not re.fullmatch(r'[0-9\.\s\+\-\*/\(\)/]+', safe):
        raise AssertionError(f"[expr_assert] 허용되지 않은 문자: {ctx} -> {expr!r}")
    try:
        eval(safe, {"__builtins__": {}}, {})
    except Exception as e:
        raise AssertionError(f"[expr_assert] 평가 실패: {ctx} -> {expr!r} ({e})")


def assert_no_placeholder(items):
    """items: dict 리스트. answer_expr 및 각 distractor의 expr를 검증한다."""
    for it in items:
        iid = it.get('id', '?')
        _check_one(it.get('answer_expr'), f"{iid}.answer_expr")
        for d in it.get('distractors', []):
            _check_one(d.get('expr'), f"{iid}.distractor[opt{d.get('opt')}]")
    return True
