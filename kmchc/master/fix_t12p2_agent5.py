#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
fix_t12p2_agent5.py — T12 P2 순회 마감 조치 (5차 · 종료)

4차 마감 순회에서 판정이 처음으로 깨끗해졌다.
  · factchecker  **✗ 0건** — 앞선 세 회차에서 매번 나오던 '수정이 만든 어긋남'이 처음으로 없다
  · defender     오답 30개 전수 **F2 실패 0건** · 정답 유일성 전 문항
  · solver       정답 10/10 · **어미·표기 불일치 0건**

[F] 남은 실질 결함 하나 — student-sim + solver
  M01819 는 발문이 "전하는 그대로 두면서 남는 질량만 채우려면"이라고 **정답을 문장으로
  써 주고 있다.** 가상 응시에서 A(개념 미형성)까지 어휘 대조만으로 맞혔고 오답 셋이 전부
  죽었다 — 사실상 변별력 0 이다.
  ★그런데 이 구절을 통째로 빼면 '핵 속 양성자 4개 + 전자 2개'가 전하·질량을 모두 만족해
   두 번째 정답이 된다★(1차 기록). 전하 제약은 남기고 **물음만 바꿔** 어휘 대응을 끊는다.

[★설계 원칙 수정★] student-sim 이 3차의 진단을 스스로 정정했다
  C=D 일치율이 8/10 → 9/10 → 10/10 으로 오히려 역행했다. 원인 진단이 정확하다.
  > **"추가 비교 단계를 오답에만 심었기 때문이다.
  >   C 를 가르려면 정답 진술 자체가 상대 판단을 요구해야 한다."**
  정답이 다른 보기를 보지 않고도 독립적으로 참임이 확인되면, C 는 오답을 검토할 필요 없이
  정답에 도달한다. 예컨대 M01821 의 정답 "에너지 합이 같다"는 에너지 보존만으로 즉시 참이라,
  ②③에 심어 둔 파장·준위 간격 판단을 C 가 지나가 버린다.
  → 처방: 발문을 **"옳은 것은?"이 아니라 "어느 쪽이 더 큰가 / 가장 ~한 것 / 순서"** 로.
    정답을 고르는 행위 안에 비교가 강제로 들어가야 한다.
  ★이것은 이 배치를 더 고치는 근거가 아니라 P3 이후의 설계 표준이다.★
  같은 자리를 네 번 돌린 결과 세 번 새 결함이 생겼다. **회전을 멈춘다.**

[△] 함께 손보는 문구 (factchecker, 전부 사실 오류는 아님)
  A1 M01818 ④ 오답 근거가 실험 밖 사실('전극 금속이 아니라 기체에서 생긴다')이라
     바로 앞 문장("이 실험은 그것을 알려 주지 않아")과 층위가 어긋난다
  A2 M01820 "계열을 가르는 것은 도착한 자리" 는 방출에서만 성립 → 한정
  A3 M01822 자가진단이 "발머가 가운데라 가시광선"으로 단정 → 본문의 단서와 맞춘다
  A4 M01826 본문은 "약 −146", 보기·자가진단은 "−146" → 표기 통일
  A5 M01819 "2배분" 이 '2배'인지 '양성자 2개 몫'인지 갈린다 → 통일

사용: python3 master/fix_t12p2_agent5.py [--apply]
"""
import json, os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))
BANK = os.path.join(HERE, 'master_bank.json')
CIR = '①②③④'

STEM_REPL = [
 # [F] 전하 제약은 남기고 물음만 바꿔 어휘 대응을 끊는다
 ('M01819',
  "헬륨 원자핵의 전하는 양성자 2개로 이미 설명이 된다. 그런데 질량을 재어 보니 "
  "수소 원자핵의 4배여서, 양성자 2개 몫인 2배보다 2배분이 더 남는다. "
  "전하는 그대로 두면서 남는 질량만 채우려면 어느 것을 받아들여야 하는가?",
  "헬륨 원자핵의 전하는 양성자 2개로 이미 설명이 된다. 그런데 질량을 재어 보니 "
  "수소 원자핵의 4배여서, 양성자 두 개 몫인 2배보다 두 개 몫이 더 남는다. "
  "이 어긋남을 설명하려면 어느 것을 받아들여야 하는가?"),
]

SOL_REPL = [
 # [A1] M01818 층위 분리
 ('M01818',
  "④ 구멍을 지난 흐름이 (−)극 금속에서 튀어나왔다는 것: 전극 금속이 아니라 관 속 기체에서 "
  "생긴 흐름이야.",
  "④ 구멍을 지난 흐름이 (−)극 금속에서 튀어나왔다는 것: (−)극 '쪽으로' 나아갔으니 그곳이 "
  "출발점일 수는 없지."),
 # [A2] M01820 방출 한정
 ('M01820',
  "계열을 가르는 것은 출발한 자리가 아니라 도착한 자리야. 둘을 따로따로 짚어 보자.",
  "빛을 낼 때 계열을 가르는 것은 출발한 자리가 아니라 도착한 자리야. 둘을 따로따로 짚어 보자."),
 ('M01820',
  "자가진단: 계열 = 도착한 자리. 둘을 물으면 순서까지 맞춰야 한다.",
  "자가진단: 방출에서 계열 = 두 준위 중 낮은 쪽. 둘을 물으면 순서까지 맞춰야 한다."),
 # [A3] M01822 자가진단 완화
 ('M01822',
  "자가진단: 도착 준위가 에너지를 가른다 — 라이먼>발머>파셴. 발머가 가운데라 가시광선.",
  "자가진단: 도착 준위가 에너지를 가른다 — 라이먼>발머>파셴. 발머는 그 사이라 주요 선이 가시광선."),
 # [A4] M01826 표기 통일
 ('M01826',
  "그런데 n=3 은 약 −146 이라 두 번째 칸의 폭은 182 로 훨씬 좁아.",
  "그런데 n=3 은 −146 이라 두 번째 칸의 폭은 182 로 훨씬 좁아."),
 # [A5] M01819 '2배분' 통일
 ('M01819',
  "전하는 이미 양성자 2개로 딱 맞았고, 질량만 2배분이 비어 있지.",
  "전하는 이미 양성자 2개로 딱 맞았고, 질량만 양성자 두 개 몫이 비어 있지."),
]

WATCH = {
 'M01819': "★편집 금지★ stem 의 '전하는 양성자 2개로 이미 설명된다'를 빼면 "
           "'핵 속 양성자 4개 + 전자 2개'가 전하·질량을 모두 만족해 두 번째 정답이 된다. "
           "★설계 부채★ 가상 응시에서 A 까지 맞혀 상위 변별이 낮다 — 발문의 어휘 대응은 "
           "5차에서 끊었으나, 근본 처방은 '정답을 고르는 행위에 비교를 넣는' 재설계다",
 'M01820': "★설계 의도★ M01822 가 '발머 = 도착 준위 n=2'를 공개하므로 이 문항에 "
           "발머를 등장시키지 말 것(3차에서 실제로 소거만으로 풀리는 상태가 됐다)",
 'M01822': "★설계 의도★ ②③④ 가 '도착 준위 n=2'를 공유하고 에너지 서열에서만 갈린다. "
           "정답의 '자외선과 적외선 사이'는 교과서 표준 단순화 — 계열한계 364.6 nm 는 자외선",
 'M01823': "★편집 금지★ ④ 를 '더 큰 에너지도 흡수한다'로 되돌리면 그 절이 독립 진술로 참이 된다",
 'M01825': "★편집 금지★ ① 을 '전자가 (−)전하라서'로 되돌리면 쿨롱 퍼텐셜상 반쯤 참이 되고, "
           "② 를 '에너지가 작아지도록'으로 되돌리면 절댓값으로 읽는 학생에게 참으로 보인다",
 'M01818': "범위 메모: 양극선의 생성 기작과 입자 질량은 교재에 없다 — 해설의 배경 설명으로만",
}
VERIFIED = {"layer5": "F1~F7 통과 · 에이전트 순회 종료(4회)",
            "at": "T12 P2",
            "by": "독립 에이전트 4종 × 4회 (solver·defender·factchecker·student-sim)",
            "note": "마감 순회: factchecker ✗ 0건 · defender 오답 30개 전수 F2 실패 0건 및 "
                    "정답 유일성 전 문항 · solver 정답 10/10 및 어미·표기 불일치 0건. "
                    "미해결 부채: 가상 응시 C=D 일치율 10/10 — 상위권 변별이 낮다. "
                    "정답을 고르는 행위 안에 비교를 넣는 재설계는 P3 이후 설계 표준으로 넘긴다"}


def apply(bank):
    idx = {x['id']: x for x in bank}
    n = 0
    for fid, old, new in STEM_REPL:
        x = idx[fid]
        assert x['stem'] == old, f"{fid} stem 불일치"
        x['stem'] = new; n += 1
    for fid, old, new in SOL_REPL:
        x = idx[fid]
        assert old in x['solution'], f"{fid} 해설 불일치: {old[:44]}"
        x['solution'] = x['solution'].replace(old, new, 1); n += 1
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
    m20 = idx['M01820']['stem'] + ''.join(idx['M01820']['choices'])
    m22 = idx['M01822']['stem'] + ''.join(idx['M01822']['choices'])
    if '발머' in m20 and 'n=2' in m22:
        print("⛔ 세트 누출: M01822 의 '발머=n=2' 가 M01820 의 보기를 지운다"); bad.append('LEAK')
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
