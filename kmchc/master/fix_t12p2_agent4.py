#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
fix_t12p2_agent4.py — T12 P2 에이전트 4차(마감) 패스 조치

3차 조치 40곳 뒤 마감 순회를 돌렸다. 판정이 크게 좋아졌다.
  · defender  오답 30개 전수 **F2 실패 0건** · 정답 유일성 전 문항 확보
  · solver    정답 10/10 일치 · **어미·표기 불일치 0건**(직전 회차에서 5건 지적)
남은 것은 두 가지뿐이다.

[N] ★3차 수정이 만든 새 결함 — 같은 자리, 형태만 바꿔서★
  N1 M01822 → M01820 누출 (solver)
     3차에서 M01822 보기를 "도착 준위가 n=2" 로 통일해 삼자 구도를 만들었다.
     C 를 가르는 데는 성공했지만, 그 문장이 **'발머 = 도착 준위 n=2' 라는 판정 규칙을
     그대로 공개**한다. 그러면 M01820 은 파셴이 n=3 이라는 지식 없이도 풀린다 —
     4→2 는 발머이니 ③④ 탈락, 5→3 은 n=2 도착이 아니니 발머가 아니라 ① 탈락, 남는 건 ②.
     ★두 문항이 같은 축(계열↔도착 준위)에 있는 한, 보기를 어떻게 바꿔도 이 충돌은 되풀이된다.★
     → 이번에는 **M01820 의 전이를 바꿔** 발머를 세트에서 뺀다(5→3 파셴 · 6→1 라이먼).
       M01822 가 알려 주는 것은 발머의 도착 준위이므로, 발머가 없으면 아무 도움이 안 된다.
     ※ M01822 쪽을 고치는 길도 있었으나 기각했다 — "도착 준위 n=2" 를 빼면 정답이
       "가시광선 범위라서 가시광선"이라는 동어 반복이 되어 문항이 죽는다.

[D] 모호어 — defender + solver 가 같은 곳을 지적
  D1 M01825 ② "n 이 커질수록 에너지가 작아지도록" — 부호 있는 값으로는 명백히 거짓이지만
     (−1312 → −328 → −146 으로 증가), 학생이 |E| 로 읽으면 앞 절이 참으로 보인다.
     → "0 보다 더 내려간다" 로 바꿔 절댓값 해석의 여지를 없앤다.

[기록만] 고치지 않고 남기는 것
  · M01822 정답 "도착 준위가 n=2 라 자외선과 적외선 사이" 는 교과서 표준 단순화다.
    발머 계열한계 364.6 nm 는 자외선이라 엄밀히는 전체가 가시광선이 아니다.
    해설 본문이 이미 그 단서를 달고 있고, solver·defender 모두 "수정 없이 두어도 무방"으로
    판정했다. **회전 자체가 결함을 부르므로 여기서 멈춘다.**
  · M01819 발문의 "전하는 그대로 두면서 남는 질량만" 이 정답과 낱말이 대응한다(solver, 경미).
    이는 채드윅 논증의 전제를 명시한 것이라 논증형 문항의 의도된 골격으로 본다.
    ★게다가 이 구절을 빼면 '핵 속 양성자 4개 + 전자 2개'가 두 번째 정답이 된다★(1차 기록).

사용: python3 master/fix_t12p2_agent4.py [--apply]
"""
import json, os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))
BANK = os.path.join(HERE, 'master_bank.json')
CIR = '①②③④'

# ── [N1] M01820 — 전이를 바꿔 발머를 세트에서 뺀다 · 정답 ② ──
M20_STEM = ("수소 원자에서 전자가 n=5 인 궤도에서 n=3 인 궤도로 떨어지는 경우와, "
            "n=6 인 궤도에서 n=1 인 궤도로 떨어지는 경우가 있다. "
            "두 경우가 속한 계열을 차례로 바르게 짝지은 것은?")
M20_CH = ["둘 다 라이먼 계열에 속한다", "파셴 계열과 라이먼 계열에 속한다",
          "라이먼 계열과 파셴 계열에 속한다", "둘 다 파셴 계열에 속한다"]
M20_DIST = [
 {'opt': 0, 'text': M20_CH[0], 'error': '앞은 n=3 도착이라 파셴', 'type': 'proc'},
 {'opt': 2, 'text': M20_CH[2], 'error': '두 계열의 순서를 뒤바꿈', 'type': 'sign'},
 {'opt': 3, 'text': M20_CH[3], 'error': '뒤는 n=1 도착이라 라이먼', 'type': 'proc'},
]
M20_SOL = """계열을 가르는 것은 출발한 자리가 아니라 도착한 자리야. 둘을 따로따로 짚어 보자.

[정답] ② 파셴 계열과 라이먼 계열에 속한다 — 계열의 이름은 전자가 어느 준위에 '도착'했느냐로 정해져. n=1 에 도착하면 라이먼, n=2 면 발머, n=3 이면 파셴이지. 앞의 경우는 n=3 에 도착했으니 파셴 계열이고, 뒤의 경우는 n=1 에 도착했으니 라이먼 계열이야. 차례대로 파셴 · 라이먼이므로 ②가 옳아.
출발한 자리가 각각 n=5 와 n=6 이라는 것에 눈이 가기 쉬운데, 출발 준위는 계열을 정하지 않아. n=6 에서 출발하더라도 n=1 로 가면 라이먼, n=2 로 가면 발머, n=3 으로 가면 파셴이 되지. 같은 계열 안에서 출발 준위가 달라지면 선의 자리가 옮겨 갈 뿐 계열이 바뀌지는 않아.
두 경우를 한꺼번에 물으면 가장 흔한 미끄러짐이 순서를 뒤집는 거야. 어느 쪽이 앞인지 헷갈리거든. 하나씩 도착 준위만 확인하고 차례대로 적어 두면 실수가 줄어. 그리고 에너지로도 가늠해 두자 — 아래쪽으로 떨어질수록 준위 차가 크니 라이먼 쪽이 파셴 쪽보다 훨씬 큰 에너지를 내놓아.

① 둘 다 라이먼 계열에 속한다: 앞의 경우는 n=3 에 도착했으니 파셴이야.
③ 라이먼 계열과 파셴 계열에 속한다: 두 계열을 맞게 골랐지만 순서가 뒤바뀌었어.
④ 둘 다 파셴 계열에 속한다: 뒤의 경우는 n=1 에 도착했으니 라이먼이야.

자가진단: 계열 = 도착한 자리. 둘을 물으면 순서까지 맞춰야 한다."""

CH_REPL = [
 ('M01825', 1, "n 이 커질수록 에너지가 작아지도록 (−)를 붙였기 때문이다",
              "n 이 커질수록 에너지 값이 0 보다 더 내려가기 때문이다"),
]

SOL_REPL = [
 ('M01825',
  "② n 이 커질수록 에너지가 작아지도록 (−)를 붙였기 때문이다: 거꾸로야 — n 이 커지면 "
  "0 에 가까워지니 값은 오히려 커져.",
  "② n 이 커질수록 에너지 값이 0 보다 더 내려가기 때문이다: 거꾸로야 — n 이 커지면 "
  "0 에 가까워지며 값은 위로 올라가지."),
]

WATCH = {
 'M01819': "★편집 금지★ stem 의 '전하는 양성자 2개로 이미 설명된다'와 '전하는 그대로 두면서'를 "
           "빼면 '핵 속 양성자 4개 + 전자 2개'가 전하·질량을 모두 만족해 두 번째 정답이 된다",
 'M01820': "★설계 의도★ 이 문항과 M01822 는 같은 축(계열↔도착 준위)에 있다. M01822 보기가 "
           "'도착 준위가 n=2'를 공개하므로 **이 문항에 발머를 등장시키지 말 것** — "
           "3차에서 실제로 소거만으로 풀리는 상태가 됐다",
 'M01822': "★설계 의도★ ②③④ 가 '도착 준위 n=2'를 공유하고 에너지 서열에서만 갈린다. "
           "이 세트에서 C(부분 이해)와 D(숙달)를 가르는 구조이므로 흩뜨리지 말 것. "
           "다만 그 공유 전제가 M01820 으로 새므로 두 문항의 소재를 겹치지 않게 유지할 것. "
           "정답의 '자외선과 적외선 사이'는 교과서 표준 단순화 — 계열한계 364.6 nm 는 자외선이다",
 'M01823': "★편집 금지★ ④ 를 '더 큰 에너지도 흡수한다'로 되돌리면 그 절이 독립 진술로 참이 된다",
 'M01825': "★편집 금지★ ① 을 '전자가 (−)전하라서'로 되돌리면 쿨롱 퍼텐셜상 반쯤 참이 되고, "
           "② 를 '에너지가 작아지도록'으로 되돌리면 절댓값으로 읽는 학생에게 참으로 보인다",
 'M01818': "범위 메모: 양극선의 생성 기작과 입자 질량은 교재에 없다 — 해설의 배경 설명으로만",
}
VERIFIED = {"layer5": "F1~F7 통과 · 에이전트 4차 순회 종료",
            "at": "T12 P2",
            "by": "독립 에이전트 4종 × 4회 (solver·defender·factchecker·student-sim)",
            "note": "마감 순회에서 defender 오답 30개 전수 F2 실패 0건 · 정답 유일성 전 문항 확보 · "
                    "solver 정답 10/10 일치 · 어미·표기 불일치 0건"}


def apply(bank):
    idx = {x['id']: x for x in bank}
    n = 0

    it = idx['M01820']
    assert it['choices'][0] == "둘 다 발머 계열이다", "M01820 원본 보기 불일치"
    it['stem'] = M20_STEM; it['choices'] = list(M20_CH)
    it['distractors'] = [dict(d) for d in M20_DIST]
    it['solution'] = M20_SOL
    n += 4

    for fid, i, old, new in CH_REPL:
        x = idx[fid]
        assert x['choices'][i] == old, f"{fid} {CIR[i]} 불일치: {x['choices'][i]}"
        x['choices'][i] = new
        for d in x['distractors']:
            if d['opt'] == i:
                d['text'] = new
        n += 1
    for fid, old, new in SOL_REPL:
        x = idx[fid]
        assert old in x['solution'], f"{fid} 해설 불일치: {old[:44]}"
        x['solution'] = x['solution'].replace(old, new, 1); n += 1

    hit = [d for d in idx['M01825']['distractors'] if d['opt'] == 1]
    hit[0]['error'] = 'n 이 커지면 0 에 가까워져 값은 오히려 올라감'; hit[0]['type'] = 'sign'; n += 1

    for fid in [f"M0{i}" for i in range(1817, 1827)]:
        idx[fid]['verified'] = dict(VERIFIED)
        if fid in WATCH:
            idx[fid]['verified']['watch'] = WATCH[fid]
    return bank, n


if __name__ == '__main__':
    bank = json.load(open(BANK, encoding='utf-8'))
    bank, n = apply(bank)
    sys.path.insert(0, HERE)
    from batch_template import len_rank, spread, g3b_applies
    idx = {x['id']: x for x in bank}
    print(f"조치 {n}곳\n")
    ranks, bad, pos = {}, [], {}
    for fid in [f"M0{i}" for i in range(1817, 1827)]:
        x = idx[fid]
        L = [len(c) for c in x['choices']]
        r = len_rank(x); sp = spread(x['choices'])
        ranks[r] = ranks.get(r, 0) + 1
        pos[x['answer']] = pos.get(x['answer'], 0) + 1
        flag = ''
        if g3b_applies(x['choices']) and sp > 0.25: flag += ' ⛔G3b'; bad.append(fid)
        if L[x['answer']] == max(L) and L.count(max(L)) == 1: flag += ' ⛔G3최장'; bad.append(fid)
        if L[x['answer']] == min(L) and L.count(min(L)) == 1: flag += ' ⛔G3최단'; bad.append(fid)
        if len(x['solution']) < 300: flag += ' ⛔해설<300'; bad.append(fid)
        for d in x['distractors']:
            if d.get('text') and d['text'] != x['choices'][d['opt']]:
                flag += f" ⛔메타불일치{CIR[d['opt']]}"; bad.append(fid)
            if d['opt'] == x['answer']:
                flag += ' ⛔정답에오답메타'; bad.append(fid)
        if re.search(r'n = [0-9∞]|→\s*\d', x['stem'] + x['solution'] + ''.join(x['choices'])):
            flag += ' ⛔표기'; bad.append(fid)
        for j, c in enumerate(x['choices']):
            if j != x['answer'] and f"{CIR[j]} {c}:" not in x['solution']:
                flag += f" ⛔풀이누락{CIR[j]}"; bad.append(fid)
        print(f"{fid} 답{CIR[x['answer']]} 길이{L} 순위{r} 산포{sp:.2f} 해설{len(x['solution'])}자{flag}")
    # 세트 내 누출 기계 점검 — '발머'가 M01820 과 M01822 에 동시에 나오면 경고
    m20 = idx['M01820']['stem'] + ''.join(idx['M01820']['choices'])
    m22 = idx['M01822']['stem'] + ''.join(idx['M01822']['choices'])
    if '발머' in m20 and 'n=2' in m22:
        print("⛔ 세트 누출: M01822 가 공개하는 '발머=n=2' 가 M01820 의 보기를 지운다"); bad.append('LEAK')
    print(f"\n위치 {' '.join(f'{CIR[k]}{v}' for k, v in sorted(pos.items()))} · 길이순위 {dict(sorted(ranks.items()))}")
    over = [k for k, v in ranks.items() if v > 4]
    if bad or over:
        print(f"⛔ 위반 {sorted(set(bad))} · 순위초과 {over}"); sys.exit(1)
    print("✅ 규칙 위반 없음 · 세트 누출 없음")
    if '--apply' in sys.argv:
        json.dump(bank, open(BANK, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
        print("✅ 반영 완료")
    else:
        print("※ 검증만. 반영하려면 --apply")
