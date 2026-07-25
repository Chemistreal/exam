#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
KMChC 명작 10,000제 — 배치 생산 템플릿
================================================================
사용법:
    1) 이 파일을 복사:  cp master/batch_template.py /tmp/t11_p11.py
    2) CONFIG 의 START_ID / EXPECT_LEN / THEME 를 맞춘다
    3) build() 안에 문항 10개를 채운다
    4) python3 /tmp/t11_p11.py            → 설계 검증만 (파일 안 건드림)
    5) python3 /tmp/t11_p11.py --merge    → 안전 게이트 통과 시 병합 + housekeeping

핵심 원칙(HANDOFF.md 3~5장 참조):
    · 위치 사전배치(정답 ①②③④ 균형) · 자수 실측(G3) · 쌍대조 선수행(판례)
    · 저장 직전 안전 게이트: len 실측 + ID 충돌 확인, 앞서 있으면 설계본 폐기
"""
import json, os, re, sys, shutil, subprocess
from collections import Counter

# ─────────────────────────── CONFIG ───────────────────────────
BASE       = os.path.dirname(os.path.abspath(__file__))       # master/ 위치
BANK       = os.path.join(BASE, 'master_bank.json')
MIRROR     = os.environ.get('KMCHC_MIRROR', '')               # 사본 경로(선택). 없으면 동기화 생략
START_ID   = 'M01743'          # ★이번 배치 첫 ID★
COUNT      = 10
EXPECT_LEN = 1742              # ★병합 직전에 파일이 가져야 할 문항 수★
THEME      = '방사성붕괴'
TT         = 11                # textbook_theme
UNIT       = 'I'
BATCH_NOTE = '[T11 P11] …배치 요지·폐기 사유를 여기 적어 rejection_log 에 남긴다'

CIR = '①②③④'
sys.path.insert(0, BASE)
try:
    from expr_assert import assert_no_placeholder
except ImportError:
    def assert_no_placeholder(items): pass


# ─────────────────────────── 헬퍼 ───────────────────────────
def mk(id, skill, track, dok, diff, esr, stem, choices, ans, proof, wrongs,
       device, calc, scen, aexpr=None):
    """문항 1개 생성. wrongs = [(오답텍스트, 오류사유, 'proc|sign|surface'[, expr]), ...]"""
    ds = []
    for w in wrongs:
        dd = {"opt": choices.index(w[0]), "error": w[1], "type": w[2]}
        if len(w) > 3 and w[3]:
            dd["expr"] = w[3]
        ds.append(dd)
    it = {"id": id, "skill": skill, "unit": UNIT, "theme": THEME, "textbook_theme": TT,
          "track": track, "dok": dok, "difficulty": diff, "expected_solve_rate": esr,
          "stem": stem, "choices": choices, "answer": ans, "answer_proof": proof,
          "distractors": sorted(ds, key=lambda x: x['opt']),
          "device": device, "calc_check": calc, "scenario": scen,
          "linked_concepts": [THEME], "source": "hand-crafted"}
    if aexpr:                      # ★G1: 정답 보기가 순수 수치일 때만★
        it["answer_expr"] = aexpr
    return it


def sol(it, lead, cor, wmap, diag):
    """해설 생성. lead=도입 1문장, cor=정답 설명, wmap={오답텍스트: 설명}, diag=자가진단"""
    c, a = it['choices'], it['answer']
    it['solution'] = (f"{lead}\n\n[정답] {CIR[a]} {c[a]} — {cor}\n\n"
                      + "\n".join(f"{CIR[i]} {c[i]}: {wmap[c[i]]}" for i in range(4) if i != a)
                      + f"\n\n자가진단: {diag}")


def ext(it, idx, new_txt):
    """G3 해소용 — 오답 선지를 늘리거나 줄인다(해설 라벨도 함께 갱신)."""
    old = it['choices'][idx]
    it['solution'] = it['solution'].replace(f"{CIR[idx]} {old}:", f"{CIR[idx]} {new_txt}:")
    it['choices'][idx] = new_txt


def swap(it, i, j):
    """정답 위치 조정 — 선지 i↔j 교환 + 오답 매핑·해설 라벨 일괄 재생성.
       ★수치 보기 문항에는 쓰지 말 것(G6 오름차순이 깨짐)★"""
    c = it['choices']; c[i], c[j] = c[j], c[i]
    if it['answer'] == i:   it['answer'] = j
    elif it['answer'] == j: it['answer'] = i
    for dd in it['distractors']:
        if dd['opt'] == i:   dd['opt'] = j
        elif dd['opt'] == j: dd['opt'] = i
    it['distractors'] = sorted(it['distractors'], key=lambda x: x['opt'])
    a = it['answer']; parts = it['solution'].split('\n\n')
    for k, p in enumerate(parts):
        if p.startswith('[정답]'):
            parts[k] = f"[정답] {CIR[a]} {c[a]} — " + p.split('— ', 1)[1]
        elif p.startswith(tuple(CIR)):
            lines = {}
            for ln in p.split('\n'):
                t = ln.split(': ', 1)
                lines[t[0][2:].strip()] = t[1] if len(t) > 1 else ''
            parts[k] = '\n'.join(f"{CIR[x]} {c[x]}: {lines.get(c[x], '')}"
                                 for x in range(4) if x != a)
    it['solution'] = '\n\n'.join(parts)


# ─────────────────────────── 검증 ───────────────────────────
G3B_MIN_MEDIAN = 8      # 이보다 짧은 보기(수치형)는 길이가 단서가 될 수 없어 면제
G3B_MAX_SPREAD = 0.25


def spread(choices):
    """보기 길이 산포 (max−min)/median. G3b 판정용."""
    L = sorted(len(str(c)) for c in choices)
    return (L[3] - L[0]) / ((L[1] + L[2]) / 2 or 1)


def g3b_applies(choices):
    """수치형 짧은 보기는 면제. 실측 근거:
       중앙길이 ~7자 구간은 산포와 무관하게 정답 2위 비중 30%/27%(차이 없음),
       15~29자 구간은 산포>0.25 에서 65.9% vs 36.8% 로 갈린다."""
    L = sorted(len(str(c)) for c in choices)
    return (L[1] + L[2]) / 2 >= G3B_MIN_MEDIAN


def len_rank(it):
    """정답 보기의 길이 순위(1=가장 긺)."""
    L = [len(str(c)) for c in it['choices']]
    return sorted(range(4), key=lambda i: -L[i]).index(it['answer']) + 1


def verify(items):
    """G1/G3/G3b/G6 + 해설 길이·구조 + expr 검산 + 위치·길이순위 분포. 문제 목록 반환."""
    issues = []
    for it in items:
        ln, a = [len(x) for x in it['choices']], it['answer']
        if (ln[a] == max(ln) and ln.count(max(ln)) == 1):
            issues.append((it['id'], 'G3 정답 유일최장', ln, a))
        if (ln[a] == min(ln) and ln.count(min(ln)) == 1):
            issues.append((it['id'], 'G3 정답 유일최단', ln, a))
        # ★G3b — 보기 길이를 나란히. 산포가 크면 '몇 번째로 긴 것'이 단서가 된다.
        #   G3 를 오답 패딩으로 해소해 온 관행이 정답을 길이 2위로 몰아 왔다(실측 T11 45%).
        sp = spread(it['choices'])
        if g3b_applies(it['choices']) and sp > G3B_MAX_SPREAD:
            issues.append((it['id'], f'G3b 보기 길이 산포 {sp:.2f}>{G3B_MAX_SPREAD} — 보기를 나란히', ln, a))
        if len(it.get('solution', '')) < 300:
            issues.append((it['id'], f"해설 {len(it.get('solution',''))}자(<300)", '', ''))
        if '[정답]' not in it.get('solution', '') or '자가진단' not in it.get('solution', ''):
            issues.append((it['id'], '해설 구조 결손', '', ''))
        if len(it['distractors']) != 3:
            issues.append((it['id'], f"오답 {len(it['distractors'])}개", '', ''))
        nums = [int(m.group(1)) for c in it['choices'] if (m := re.match(r'^(\d+)', c.strip()))]
        if len(nums) == 4 and nums != sorted(nums):
            issues.append((it['id'], f'G6 수치 비오름차순 {nums}', '', ''))
        if it.get('answer_expr'):
            ansc = it['choices'][it['answer']]
            if not re.match(r'^-?[\d.]+', ansc.strip()):
                issues.append((it['id'], f"G1 정답이 순수 수치 아님({ansc}) → answer_expr 제거", '', ''))
            else:
                val = eval(it['answer_expr'].replace('//', '/'))
                if abs(val - float(re.match(r'^-?[\d.]+', ansc.strip()).group())) > 1e-9:
                    issues.append((it['id'], f"expr 불일치 {it['answer_expr']}={val} vs {ansc}", '', ''))
    # ★G3c 배치 수준 — 정답 길이순위가 한쪽에 몰리면 지식 없이 찍어서 맞힐 수 있다.
    rr = Counter(len_rank(it) for it in items)
    if items and max(rr.values()) > max(4, len(items) * 0.4):
        issues.append(('[배치]', f"G3c 정답 길이순위 편중 {dict(sorted(rr.items()))} "
                                 f"— 한 순위 {max(rr.values())}/{len(items)}", '', ''))

    pp = Counter(it['answer'] for it in items)
    print(f"위치: ①{pp[0]} ②{pp[1]} ③{pp[2]} ④{pp[3]}"
          f" | 길이순위: " + " ".join(f"{r}위{rr.get(r,0)}" for r in (1, 2, 3, 4))
          + f" | 산포 평균 {sum(spread(i['choices']) for i in items)/max(1,len(items)):.2f}")
    for i in issues:
        print(f"  ⚠ {i[0]}: {i[1]} {i[2] if i[2] else ''} {i[3] if i[3] != '' else ''}")
    print(f"검증: {'무결 ✓' if not issues else str(len(issues)) + '건 조치 필요'}")
    return issues


# ─────────────────────────── 파이프라인 ───────────────────────────
def safety_gate(new):
    """★저장 직전 안전 게이트★ — 파일이 앞서 있으면 중단(설계본 폐기)."""
    b = json.load(open(BANK, encoding='utf-8'))
    ids = set(x['id'] for x in b)
    col = [x['id'] for x in new if x['id'] in ids]
    assert len(b) == EXPECT_LEN and not col, \
        f"⛔ 비동기 감지: 파일 {len(b)}제(예상 {EXPECT_LEN}) 충돌={col} → 설계본 폐기·파일 존중"
    return b


def merge_and_house(new, note=BATCH_NOTE):
    b = safety_gate(new)
    b += new
    json.dump(b, open(BANK, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    ad = Counter(x['answer'] for x in b)
    tn = sum(1 for x in b if x['textbook_theme'] == TT)
    print(f"✅ 병합: {len(b)}제 · T{TT} {tn}/164 · "
          f"①{ad[0]}②{ad[1]}③{ad[2]}④{ad[3]}(편차{max(ad.values())-min(ad.values())})")

    # housekeeping
    with open(os.path.join(BASE, 'rejection_log.md'), 'a', encoding='utf-8') as f:
        f.write(f"- {note}\n")
    idx = [{"id": it["id"], "skill": it["skill"], "scenario": it["scenario"],
            "key": it["answer_proof"][:20], "linked": it["linked_concepts"]} for it in b]
    json.dump(idx, open(os.path.join(BASE, 'scenario_index.json'), 'w', encoding='utf-8'),
              ensure_ascii=False, indent=1)
    pp = os.path.join(BASE, 'production_plan.json')
    if os.path.exists(pp):
        plan = json.load(open(pp, encoding='utf-8'))
        done = Counter(it['textbook_theme'] for it in b)
        for no, p in plan.get('theme_plan', {}).items():
            p['done'] = done.get(int(no), 0)
        json.dump(plan, open(pp, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)

    # 검증 스크립트 자동 실행
    lo, hi = new[0]['id'], new[-1]['id']
    for cmd in (['python3', os.path.join(BASE, 'selfaudit.py'), lo, hi],
                ['python3', os.path.join(BASE, 'master_gate.py')]):
        r = subprocess.run(cmd, capture_output=True, text=True)
        for l in r.stdout.split('\n'):
            if any(k in l for k in ('강한 충돌', '판정', '전 항목', '🔴')):
                print('  ' + l.strip())

    # 사본 동기화(설정된 경우)
    if MIRROR and os.path.isdir(MIRROR):
        for f in ('master_bank.json', 'scenario_index.json', 'production_plan.json',
                  'rejection_log.md', 'RESUME.md', 'selfaudit.py', 'master_gate.py',
                  'expr_assert.py', 'precedents.json', 'theme_order_final.json',
                  'batch_template.py'):
            src = os.path.join(BASE, f)
            if os.path.exists(src):
                shutil.copy(src, os.path.join(MIRROR, f))
        print(f"✅ 사본 동기화 → {MIRROR}")
    print("※ RESUME.md 는 손으로 갱신하세요(다음 배치 지침·소진 목록·감사 계획).")


# ─────────────────────────── 문항 작성 ───────────────────────────
def build():
    """★여기에 문항 10개를 채운다★ (아래는 형식을 보여 주는 예시 1개)

    ※ 이 예시는 일부러 G3(정답 유일최단)·해설 300자 미만에 걸리도록 두었습니다.
       그대로 실행하면 검사기가 두 건을 잡아내는 모습을 볼 수 있습니다.
    """
    new = []

    it = mk("M01743", "짧은 기능명", "심화", 3, "중간", 0.32,
            "문제 본문. 자료가 있으면 줄바꿈(\\n)으로 표에 준하는 형태로 넣는다.",
            ["오답 선지 가 — 흔한 오개념", "정답 선지 — 핵심 지식", "오답 선지 나 — 개념 혼동", "오답 선지 다 — 표면 오해"], 1,
            "정답 근거 한 줄(왜 이것이 답인가)",
            [("오답 선지 가 — 흔한 오개념", "무엇을 어떻게 잘못 보았는가", "proc"),
             ("오답 선지 나 — 개념 혼동", "다른 개념과 혼동", "sign"),
             ("오답 선지 다 — 표면 오해", "표면적 오해", "surface")],
            "핵심 장치", "검산 메모", "중복검색용 시나리오 키")
    sol(it,
        "도입 — 학생이 스스로 떠올리도록 실마리를 던지는 1문장.",
        "정답 설명. 원리를 풀어 주고, 왜 나머지가 아닌지의 뼈대까지 담는다. "
        "구어체로 길게 쓰되 사실은 정확하게. 전체 해설이 300자 이상이 되도록 한다.",
        {"오답 선지 가 — 흔한 오개념": "어디서 어긋났는지 짚고 정답 방향을 가리킨다.",
         "오답 선지 나 — 개념 혼동": "혼동한 개념을 분리해 준다.",
         "오답 선지 다 — 표면 오해": "표면만 본 지점을 교정한다."},
        "한 줄 압축 — 규칙과 적용을 함께.")
    new.append(it)

    # … 나머지 9개 …
    return new


if __name__ == '__main__':
    items = build()
    assert_no_placeholder(items)
    ids = [f"M{int(START_ID[1:]) + i:05d}" for i in range(COUNT)]
    if [x['id'] for x in items] != ids[:len(items)]:
        print(f"⚠ ID 확인: 기대 {ids[:len(items)]}")
    issues = verify(items)
    json.dump(items, open('/tmp/batch_new.json', 'w', encoding='utf-8'),
              ensure_ascii=False, indent=1)
    print("설계본 저장 → /tmp/batch_new.json")
    if '--merge' in sys.argv:
        assert not issues, "⛔ 검증 미통과 — 조치 후 병합"
        merge_and_house(items)
    else:
        print("※ 검증만 수행했습니다. 병합하려면 --merge 를 붙이세요.")
