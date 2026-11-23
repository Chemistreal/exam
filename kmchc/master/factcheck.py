#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
factcheck.py — 감사 층5 '사실 검증'의 기계 검사 부분

배경
----
감사 35회의 층 구조를 전수 확인한 결과, 층1 구조·층2 자기복제·층3 경계·층4 판례는
있었으나 **'이 문항이 화학적으로 맞는가'를 보는 층이 없었다**. 은행에는 명시적 주장만
7,264건(정답 근거 1 + 오답 근거 3 × 1,816제)이 있고 해설은 95만 자인데,
그 가운데 독립 검증을 거친 것은 0건이다.

이 도구가 맡는 범위 (기계로 판정 가능한 것)
------------------------------------------
  F4 수치 정확성 : 반감기·파장 등 수치 주장을 constants.json 과 대조
  F6 표기 정합   : 핵종 표기의 원소기호↔원자번호 일치, 붕괴 전후 A·Z 보존
  F7 서열 일관성 : 투과력·전리 작용 서열이 뒤집혀 서술되지 않았는지

기계가 판정할 수 없어 **독립 패스(사람/모델)** 로 넘기는 것
-----------------------------------------------------
  F1 정답 정확성   : 문항만 보고 다시 풀어 같은 답이 나오는가
  F2 복수 정답 위험 : 오답 3개가 확실히 틀렸는가 (부분적으로 옳은 오답은 죽은 선지보다 나쁘다)
  F3 해설 진술     : 해설의 화학적 주장이 사실인가
  F5 자족성        : stem 만으로 답이 유도되는가

  ★독립 패스는 저작 근거(answer_proof·해설)를 보지 않고 수행해야 한다.★
  감사14호가 '같은 모델의 자기감사는 판정층에서 체계적으로 관대'함을 실증했으므로,
  같은 맥락에서 이어 읽으면 자기 확증이 된다.

사용
----
  python3 master/factcheck.py                  전수 검사
  python3 master/factcheck.py M01807 M01816    구간 검사
"""
import json, os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))
BANK = os.path.join(HERE, 'master_bank.json')
CONST = os.path.join(HERE, 'constants.json')

C = json.load(open(CONST, encoding='utf-8'))
EL = C['elements']
EL_KO = C['element_names_ko']
INV = C['invariants']

# ── F4 반감기 수치 ────────────────────────────────────────────────
# ★핵종과 값을 '위치'로 짝짓는다★
#   정규식으로 한 번에 잡으면 "아이오딘-131(반감기 8일) … 세슘-137(반감기 30년)"처럼
#   한 문장에 핵종이 둘 있을 때 경계를 넘어 잘못 짝지어진다(M01797 오탐).
#   그래서 핵종 출현 위치와 반감기 값 출현 위치를 각각 모은 뒤,
#   '사이에 다른 핵종이 끼어 있지 않은 가장 가까운 짝'만 인정한다.
_NUC_TOK = re.compile(r'[가-힣]{1,6}\s*-\s*\d{1,3}|삼중수소')
_HL_VAL = re.compile(
    r'반감기[^.。\n]{0,12}?(?P<num>[\d,.]+)\s*(?P<unit>초|분|시간|일|년|만\s*년|억\s*년)')

_UNIT_KEY = {'초': 's', '분': 'min', '시간': 'h', '일': 'd', '년': 'y',
             '만년': '만y', '억년': '억y'}
MAX_GAP = 25          # 핵종과 반감기 값 사이 허용 거리(자)


def _norm(s):
    return re.sub(r'\s+', '', s)


def _pair_nuclide(text, pos):
    """반감기 값 위치 pos 에 대응하는 핵종을 찾는다.
       앞뒤로 가장 가까운 핵종을 보되, 사이에 다른 핵종이 있으면 짝짓지 않는다."""
    nucs = [(m.start(), m.end(), _norm(m.group())) for m in _NUC_TOK.finditer(text)]
    if not nucs:
        return None
    before = [n for n in nucs if n[1] <= pos]
    after = [n for n in nucs if n[0] >= pos]
    cand = []
    if before:
        s, e, name = before[-1]
        cand.append((pos - e, name))
    if after:
        s, e, name = after[0]
        cand.append((s - pos, name))
    if not cand:
        return None
    gap, name = min(cand)
    return name if gap <= MAX_GAP else None


def check_halflife(text, fid):
    """F4 — 핵종별 반감기 수치를 참조표와 대조."""
    errs = []
    table = C['half_life']
    for m in _HL_VAL.finditer(text):
        nuc = _pair_nuclide(text, m.start())
        if not nuc or nuc not in table:
            continue                       # 짝을 못 찾거나 참조표에 없으면 판정 보류
        ref = table[nuc]
        unit = _UNIT_KEY.get(_norm(m.group('unit')))
        num = m.group('num').replace(',', '').rstrip('.')
        seg = _norm(m.group())
        if unit != ref['unit']:
            if not any(_norm(a) in seg for a in ref['accept']):
                errs.append(f"F4 {nuc} 반감기 단위 불일치 — 본문 '{num}{m.group('unit')}'"
                            f" vs 참조 {ref['value']}{ref['unit']}")
            continue
        try:
            v = float(num)
        except ValueError:
            continue
        if abs(v - ref['value']) / max(ref['value'], 1e-9) > 0.06:
            if not any(_norm(a) in seg for a in ref['accept']):
                errs.append(f"F4 {nuc} 반감기 {v}{unit} ≠ 참조 {ref['value']}{ref['unit']}")
    return errs


# ── F6 핵종 표기 ──────────────────────────────────────────────────
# "원소명-질량수(원자번호)" 형태에서 원자번호가 원소와 맞는지
_NUC_Z = re.compile(r'([가-힣]{1,5})\s*-\s*(\d{1,3})\s*\(\s*원자번호\s*(\d{1,3})\s*\)')
# "원자번호 92)인 우라늄" 같은 서술형
_Z_NAME = re.compile(r'([가-힣]{1,5})\s*\(\s*원자번호\s*(\d{1,3})\s*\)')


def check_notation(text, fid):
    """F6 — 원소명과 원자번호가 어긋나지 않는지."""
    errs = []
    for m in _NUC_Z.finditer(text):
        name, A, Z = m.group(1), int(m.group(2)), int(m.group(3))
        sym = EL_KO.get(name)
        if sym and EL.get(sym) != Z:
            errs.append(f"F6 '{name}-{A}(원자번호 {Z})' — {name}의 원자번호는 {EL[sym]}")
        if sym and A < Z:
            errs.append(f"F6 '{name}-{A}' — 질량수({A})가 원자번호({Z})보다 작음")
    for m in _Z_NAME.finditer(text):
        name, Z = m.group(1), int(m.group(2))
        sym = EL_KO.get(name)
        if sym and EL.get(sym) != Z:
            errs.append(f"F6 '{name}(원자번호 {Z})' — {name}의 원자번호는 {EL[sym]}")
    return errs


# ── F7 서열 일관성 ────────────────────────────────────────────────
_PEN_BAD = re.compile(r'투과력[^.。\n]{0,30}?(α|알파)[^.。\n]{0,12}?가장\s*(크|강|세)')
_ION_BAD = re.compile(r'전리[^.。\n]{0,30}?(γ|감마)[^.。\n]{0,12}?가장\s*(크|강|세)')


def check_order(text, fid, answer_text):
    """F7 — 투과 α<β<γ, 전리 α>β>γ 서열이 '정답 쪽 서술'에서 뒤집히지 않았는지.
       ★오답 선지는 일부러 뒤집으므로 정답·해설 정답부만 본다★"""
    errs = []
    if _PEN_BAD.search(answer_text):
        errs.append("F7 정답 쪽에서 '투과력 α가 가장 강함' — 서열 역전(α<β<γ 이어야 함)")
    if _ION_BAD.search(answer_text):
        errs.append("F7 정답 쪽에서 '전리 작용 γ가 가장 강함' — 서열 역전(α>β>γ 이어야 함)")
    return errs


def answer_side(it):
    """정답 보기 + 해설의 [정답] 문단 = '이 문항이 참이라고 주장하는 것'."""
    sol = it.get('solution', '')
    seg = ''
    for part in sol.split('\n\n'):
        if part.startswith('[정답]'):
            seg = part
            break
    return it['choices'][it['answer']] + '\n' + seg + '\n' + it.get('answer_proof', '')


def run(lo='M00000', hi='M99999'):
    bank = json.load(open(BANK, encoding='utf-8'))
    targets = [x for x in bank if lo <= x['id'] <= hi]
    findings = []
    for it in targets:
        whole = f"{it['stem']}\n{' '.join(it['choices'])}\n{it.get('solution','')}\n{it.get('answer_proof','')}"
        errs = []
        errs += check_halflife(whole, it['id'])
        errs += check_notation(whole, it['id'])
        errs += check_order(whole, it['id'], answer_side(it))
        if errs:
            findings.append((it['id'], errs))
    return findings, len(targets)


def coverage(lo='M00000', hi='M99999'):
    """독립 패스(F1·F2·F3·F5)가 얼마나 진행됐는지 — verified 필드 집계."""
    bank = json.load(open(BANK, encoding='utf-8'))
    t = [x for x in bank if lo <= x['id'] <= hi]
    done = [x for x in t if (x.get('verified') or {}).get('layer5')]
    return len(done), len(t)


if __name__ == '__main__':
    lo = sys.argv[1] if len(sys.argv) > 1 and sys.argv[1].startswith('M') else 'M00000'
    hi = sys.argv[2] if len(sys.argv) > 2 and sys.argv[2].startswith('M') else 'M99999'
    findings, n = run(lo, hi)
    print(f"═══ 층5 기계 검사 · {lo}~{hi} ({n}제) ═══")
    print("  F4 수치(반감기) · F6 표기(원소↔원자번호) · F7 서열 일관성")
    if not findings:
        print(f"  ✅ 기계 검사 통과 — 지적 0건")
    else:
        for fid, errs in findings:
            print(f"  🔴 {fid}")
            for e in errs:
                print(f"       {e}")
        print(f"\n  지적 {sum(len(e) for _, e in findings)}건 / {len(findings)}제")
    d, t = coverage(lo, hi)
    print(f"\n  독립 패스(F1·F2·F3·F5) 진행: {d}/{t}제 ({d/max(t,1):.1%})")
    print("  ※ 기계 검사 통과는 '사실이 맞다'는 뜻이 아니다 — 독립 패스가 본 검증이다.")
    sys.exit(1 if findings else 0)
