#!/usr/bin/env python3
"""재집필본의 ASCII 화학 표기를 유니코드로 바꾼다(원칙 9).

원칙 9는 hwol-2014 를 고치면서 생겼기 때문에, 그 전에 집필된 jmchc 계열에는
`H2O`·`10^23`·`->`·`도씨` 가 그대로 남아 있다. 같은 오답노트 안에서 다른 문항과
어긋나 보이므로 일괄 정정한다.

**섣부른 치환은 새 오류를 만든다.** hwol-2014 때 `BF4-` 가 `BF⁴⁻`(위첨자 4)로,
`(CH₃)4` 가 변환되지 않은 채 남았다. 그래서 여기서는 정규식으로 문자열을 훑지
않고, **화학식처럼 생긴 토큰을 먼저 떼어내 원소 기호로 파싱되는지 확인한 뒤**
숫자를 아래첨자로 내린다. 파싱에 실패하면 건드리지 않는다.

특히 `L2·atm/mol2` 의 `L2` 처럼 단위는 아래첨자가 아니라 위첨자다. L·M·J 는
원소 기호가 아니므로 파싱에서 자동으로 걸러진다.

사용:
    python3 tools/dh_normalize.py            # 바뀔 내용만 보여 준다(기본)
    python3 tools/dh_normalize.py --write    # 실제로 고친다
"""

from __future__ import annotations

import collections
import glob
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

SUB = str.maketrans("0123456789", "₀₁₂₃₄₅₆₇₈₉")
SUP = str.maketrans("0123456789+-", "⁰¹²³⁴⁵⁶⁷⁸⁹⁺⁻")

ELEMENTS = set(
    "H He Li Be B C N O F Ne Na Mg Al Si P S Cl Ar K Ca Sc Ti V Cr Mn Fe Co Ni Cu Zn "
    "Ga Ge As Se Br Kr Rb Sr Y Zr Nb Mo Tc Ru Rh Pd Ag Cd In Sn Sb Te I Xe Cs Ba La Ce "
    "Pr Nd Pm Sm Eu Gd Tb Dy Ho Er Tm Yb Lu Hf Ta W Re Os Ir Pt Au Hg Tl Pb Bi Po At Rn "
    "Fr Ra Ac Th Pa U Np Pu".split()
)
# 문항에서 가상의 원소·물질을 가리키는 글자. 실제 원소 기호와 같은 취급을 한다.
# L(리터)·J(줄) 은 단위라서 뺀다. `L2·atm/mol2` 의 L2 는 아래첨자가 아니라 위첨자다.
PLACEHOLDERS = set("A B C D E G M Q R T X Y Z".split())
SYMBOLS = ELEMENTS | PLACEHOLDERS

# 화학식 후보: 대문자로 시작하고 숫자를 품은, 괄호까지 포함한 덩어리.
TOKEN = re.compile(r"[A-Z][A-Za-z0-9()]*\d[A-Za-z0-9()]*")


def parse_formula(token: str) -> str | None:
    """토큰이 화학식으로 읽히면 아래첨자를 적용해 돌려주고, 아니면 None.

    아래첨자는 원소 기호나 닫는 괄호 바로 뒤에만 올 수 있다. 이 조건이 없으면
    아레니우스 식 `(Ea/R)(1/T1 − 1/T2)` 의 `(1` 을 화학식으로 읽어 `(₁` 로
    망가뜨린다. 여는 괄호 뒤에는 반드시 원소 기호가 와야 한다.

    화학식 뒤에는 상태 기호나 주석이 붙어 있곤 한다(`N2(g)`, `K2SO4(i = 3)`).
    읽히는 데까지만 바꾸고 나머지는 그대로 돌려준다.
    """
    out = []
    i = 0
    saw_digit = False
    prev = ""  # 방금 읽은 것: symbol / open / close / digit
    while i < len(token):
        char = token[i]
        if char == "(":
            if i + 1 >= len(token) or not token[i + 1].isupper():
                break  # `(g)` 같은 꼬리표. 여기까지만 바꾼다.
            out.append(char)
            prev = "open"
            i += 1
        elif char == ")":
            if prev not in ("symbol", "digit", "close"):
                break
            out.append(char)
            prev = "close"
            i += 1
        elif char.isupper():
            symbol = token[i : i + 2]
            if len(symbol) == 2 and symbol[1].islower() and symbol in SYMBOLS:
                out.append(symbol)
                i += 2
            elif char in SYMBOLS:
                out.append(char)
                i += 1
            else:
                break
            prev = "symbol"
        elif char.isdigit():
            if prev not in ("symbol", "close"):
                break
            j = i
            while j < len(token) and token[j].isdigit():
                j += 1
            out.append(token[i:j].translate(SUB))
            saw_digit = True
            prev = "digit"
            i = j
        else:
            break
    return "".join(out) + token[i:] if saw_digit else None


# 이미 반쪽만 올라간 소수 지수를 되돌린다: `10⁴.30` → `10^(4.30)`, `e¹¹.93` → `e^(11.93)`.
# 아래 지수 규칙이 `(?!\.\d)` 를 갖기 전에 만들어진 자국이라 데이터에 남아 있다.
HALF_EXP = re.compile(r"([⁰¹²³⁴⁵⁶⁷⁸⁹]+)(\.\d+)")
UNSUP = str.maketrans("⁰¹²³⁴⁵⁶⁷⁸⁹", "0123456789")


def normalize(text: str) -> str:
    text = HALF_EXP.sub(lambda m: f"^({m.group(1).translate(UNSUP)}{m.group(2)})", text)
    # ⚠ 예전에는 "도씨" 를 ℃(U+2103)로 바꿨다. 그 글자는 CJK 호환용이라
    #   유니코드가 쓰지 말라고 권하고, 글꼴에 따라 작은 크기에서 뭉개지며,
    #   "°C" 로 찾으면 안 걸린다. 저장소 안에서도 한 화면에 두 표기가 섞여
    #   있었다(grade-j0.html: ℃ 11개 · °C 10개). °C 로 모은다.
    text = text.replace("도씨", "°C").replace("℃", "°C").replace("<->", "⇌").replace("<=>", "⇌")
    text = re.sub(r"(?<![<=\-])->", "→", text)
    # 10^23, 10^-5 → 10²³, 10⁻⁵
    #
    # 지수부 뒤에 소수점이 이어지면 건드리지 않는다(`(?!\.\d)`). 유니코드에는 위첨자
    # 소수점이 없어서, 이 조건이 없으면 `10^1.77` 이 `10¹.77` 로 정수부만 올라가
    # 원래보다 더 읽기 어려워진다. 소수 지수는 `10^(1.77)` 처럼 괄호로 묶어 둔다.
    text = re.sub(
        r"(?<=\d)\^\s*(-?\d+)(?!\.\d)", lambda m: m.group(1).translate(SUP), text
    )
    # Na^+, SO4^2- 의 위첨자부
    text = re.sub(
        r"\^\s*(\d*[+-])", lambda m: m.group(1).translate(SUP), text
    )
    # 남은 지수: [F-]^2, n^2, E_n = -13.6/n^2
    text = re.sub(r"\^\s*(-?\d+)(?!\.\d)", lambda m: m.group(1).translate(SUP), text)
    # 상수 이름에 붙는 번호: Ka1, pKa2, Ksp1.
    # 뒤쪽 경계를 \b 로 잡으면 "Ka3가" 처럼 한글이 이어질 때 한글도 낱말 문자라
    # 경계가 서지 않는다. 숫자가 더 오지 않는지만 본다.
    text = re.sub(
        r"\b(p?K(?:sp|a|b|c|p|w))(\d)(?!\d)",
        lambda m: m.group(1) + m.group(2).translate(SUB),
        text,
    )
    text = TOKEN.sub(lambda m: convert(m.group()), text)
    return charges(text)


SUPSIGN = {"+": "⁺", "-": "⁻", "−": "⁻"}

# 위첨자 숫자 뒤에 ASCII 부호가 남은 전하: `SO₄²-`, `Ba²+`.
# 뒤에 숫자가 오면 `10⁶-10⁷` 같은 범위일 수 있으므로 건드리지 않는다.
#
# 위첨자 숫자는 코드포인트가 이어져 있지 않다. ¹²³ 은 U+00B9·U+00B2·U+00B3 이고
# 나머지는 U+2070 대역이라, `[⁰-⁹]` 로 범위를 잡으면 ¹²³ 이 빠진다. 낱낱이 적는다.
SUPD = "⁰¹²³⁴⁵⁶⁷⁸⁹"
# 뒤에 영문자가 오면 전하가 아니다. `d(x²−y²)` 의 `−` 는 오비탈 이름 속 빼기다.
SUP_SIGN = re.compile(f"([{SUPD}])([+\\-−])(?![\\dA-Za-z{SUPD}])")

# 숫자 없는 맨 전하: `H+` → `H⁺`.
#
# **화학식 모양이면 무엇이든 바꾸는 규칙은 쓸 수 없다.** 구조식의 결합선이 화학식
# 뒤에 그대로 붙어 나오기 때문이다. `C₁(CH₃−)` 의 `−` 는 다음 탄소로 가는 결합선이지
# 음전하가 아니고, `−CO−NH−` 도 마찬가지다. 뒤에 낱말 문자가 오는지만 보아서는
# 이 둘을 가릴 수 없다(`CH₃−)` 는 닫는 괄호가 뒤에 온다).
#
# 그래서 **실제로 홑이온으로 쓰이는 화학종만 목록으로 적어 두고** 그것만 바꾼다.
# 목록에 없는 것은 그냥 둔다. 놓치는 쪽이 구조식을 망가뜨리는 쪽보다 낫다.
IONS = (
    "H OH H₃O NH₄ Ag Na K Li Cs Rb Cu Hg Tl "
    "F Cl Br I CN SCN NCS N₃ "
    "NO₂ NO₃ ClO ClO₂ ClO₃ ClO₄ BrO₃ IO₃ MnO₄ "
    "HSO₃ HSO₄ HCO₃ HS HCOO CH₃COO C₆H₅COO C₅H₅NH "
    "H₂PO₄ HC₂O₄ H₂Y "
    "M A B X Y Z R Q"
).split()
BARE_SIGN = re.compile(
    r"(?<![A-Za-z₀-₉" + SUPD + r"\-−])(" + "|".join(sorted(IONS, key=len, reverse=True)) + r")"
    # 한글이 뒤에 오는 것은 조사다(`Cl⁻로`, `Ag⁺가`). 영문자·숫자만 막는다.
    r"([+\-−])(?![A-Za-z\d" + SUPD + r"])"
)


SUB2SUP = str.maketrans("₀₁₂₃₄₅₆₇₈₉", "⁰¹²³⁴⁵⁶⁷⁸⁹")

# 아래첨자로 잘못 내려간 전하: `Cu₂+`, `Al₃+`, `S₂−`.
#
# **이 도구가 만든 오류다.** `Cu2+` 의 2 를 원소 기호 뒤에 오는 화학식 숫자로 읽어
# 아래첨자로 내리는 바람에, '구리(Ⅱ) 이온'이 '구리 원자 2개'가 되었다. 숫자 뒤에
# 부호가 붙어 있으면 그 숫자는 원자 수가 아니라 전하다.
#
# 다만 아래첨자가 진짜 원자 수인 이온도 있다. `I₃⁻`(삼아이오딘화 이온)은 아이오딘이
# 정말 3개고 전하가 1− 이다. 그런 화학종은 목록에 적어 두고 부호만 올린다.
REAL_SUBSCRIPT = {"I₃", "Br₃", "Cl₃", "O₂", "O₃", "N₃", "S₂", "S₄", "C₂", "H₂", "Hg₂"}
SUB_CHARGE = re.compile(r"(?<![A-Za-z₀-₉])([A-Z][a-z]?)([₀-₉])([+\-−])(?![A-Za-z\d])")


def _sub_charge(m: re.Match) -> str:
    symbol, digit, sign = m.groups()
    if symbol + digit in REAL_SUBSCRIPT:
        return symbol + digit + SUPSIGN[sign]
    return symbol + digit.translate(SUB2SUP) + SUPSIGN[sign]


def charges(text: str) -> str:
    text = SUB_CHARGE.sub(_sub_charge, text)
    text = SUP_SIGN.sub(lambda m: m.group(1) + SUPSIGN[m.group(2)], text)
    return BARE_SIGN.sub(lambda m: m.group(1) + SUPSIGN[m.group(2)], text)


def convert(token: str) -> str:
    """토큰을 바꾼다. 앞이 상수 이름이면 괄호 안에서 다시 시도한다.

    `Ksp(Ag2CrO4)` 는 K 다음이 s 라 화학식으로 읽히지 않는다. 이럴 때 여는 괄호
    뒤부터 다시 읽으면 안쪽 화학식을 살릴 수 있다.
    """
    parsed = parse_formula(token)
    if parsed:
        return parsed
    head = token.find("(")
    if 0 < head < len(token) - 1:
        return token[: head + 1] + convert(token[head + 1 :])
    return token


FIELDS = ("stem", "explanation", "misconception")


def walk(write: bool) -> None:
    changes: collections.Counter[tuple[str, str]] = collections.Counter()
    touched = 0
    for path in sorted(glob.glob(str(ROOT / "donghyung" / "*.json"))):
        data = json.loads(Path(path).read_text(encoding="utf-8"))
        if data.get("strategy") != "original-authored":
            continue
        dirty = False
        for question in data["questions"].values():
            for field in FIELDS:
                value = question.get(field)
                if isinstance(value, str):
                    new = normalize(value)
                    if new != value:
                        dirty = True
                        for a, b in diff_tokens(value, new):
                            changes[(a, b)] += 1
                        question[field] = new
            for key in ("choices", "misconceptions"):
                value = question.get(key)
                if isinstance(value, list):
                    new_list = [normalize(v) for v in value]
                    if new_list != value:
                        dirty = True
                        for old, new in zip(value, new_list):
                            for a, b in diff_tokens(old, new):
                                changes[(a, b)] += 1
                        question[key] = new_list
                elif isinstance(value, dict):
                    for k, v in list(value.items()):
                        new = normalize(v)
                        if new != v:
                            dirty = True
                            for a, b in diff_tokens(v, new):
                                changes[(a, b)] += 1
                            value[k] = new
        if dirty:
            touched += 1
            if write:
                Path(path).write_text(
                    json.dumps(data, ensure_ascii=False, indent=1) + "\n",
                    encoding="utf-8",
                )

    print(f"{'고친' if write else '고칠'} 시험 {touched}개 · 서로 다른 치환 {len(changes)}가지")
    for (a, b), count in changes.most_common():
        print(f"  {count:4}회  {a}  →  {b}")


def diff_tokens(old: str, new: str) -> list[tuple[str, str]]:
    """어떤 토큰이 무엇으로 바뀌었는지 뽑는다(검토용)."""
    pairs = []
    for token in set(TOKEN.findall(old)):
        converted = parse_formula(token)
        if converted and converted != token:
            pairs.append((token, converted))
    for symbol, name in (("->", "→"), ("도씨", "°C"), ("^", "위첨자")):
        if symbol in old and symbol not in new:
            pairs.append((symbol, name))
    return pairs


if __name__ == "__main__":
    try:
        walk("--write" in sys.argv[1:])
    except BrokenPipeError:  # `| head` 로 잘라 볼 때 역추적을 남기지 않는다
        pass
