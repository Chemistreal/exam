#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
fix_t12p1_layer5.py — 감사 층5 첫 적용 결과 조치 (T12 P1)

층5 독립 패스(저작 근거를 가리고 문항만 놓고 다시 푼 뒤 오답을 공격)를
M01807~M01816 에 처음 적용한 결과, **F2 복수 정답 위험 1건**이 나왔다.

  M01814 ③ "원자 속의 전자가 알파 입자를 밀어내지 못한다는 것"
    → 이 진술은 그 자체로 사실이다. 전자는 알파 입자보다 약 7,300배 가벼워
       실제로 알파 입자를 밀어내지 못한다. 게다가 '대부분 통과'에서 추론할
       수도 있어, 잘 아는 학생일수록 끌린다 → 변별도를 깎는 오답.
    → '확실히 틀린' 진술로 교체하되, 아무 진술이 아니라 **실제 오개념**을 쓴다.
       빈 공간이 원자 '사이'에 있다고 여기는 착각은 이 실험에서 매우 흔하다.
       금속은 원자가 빽빽이 붙어 있으므로 명백히 거짓이고, 교정 가치도 크다.

나머지 9제는 F1(정답 정확성)·F2·F5(자족성) 전부 통과.
F4·F6·F7 기계 검사도 전건 통과(factcheck.py).

사용: python3 master/fix_t12p1_layer5.py [--apply]
"""
import json, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
BANK = os.path.join(HERE, 'master_bank.json')

OLD = "원자 속의 전자가 알파 입자를 밀어내지 못한다는 것"
NEW = "원자와 원자 사이에 아주 넓은 틈이 벌어져 있다는 것"
OLD_WMAP = "전자가 가벼운 건 맞지만 이 결과의 결론은 '비어 있다'야."
NEW_WMAP = "빈 공간은 원자 사이가 아니라 원자 '속'에 있어 — 금속은 원자가 빽빽이 붙어 있지."
OLD_TAIL = "전자가 가벼워 알파 입자를 못 막는 것도 사실이지만 이 결과가 곧바로 말해 주는 것은 '비어 있다'는 쪽이야."
NEW_TAIL = ("꽉 찬 덩어리였다면 통과하지 못했을 테고, 금박은 원자 한 겹이 아니야. "
            "특히 헷갈리기 쉬운 것이 '빈 공간이 어디에 있느냐'인데 — 원자와 원자 사이가 아니라 "
            "원자 '속'이 비어 있는 거야. 금속에서 원자들은 오히려 빽빽하게 맞붙어 있거든.")
OLD_ERR = "전자가 가벼운 것은 맞으나 결론은 빈 공간"
NEW_ERR = "빈 공간의 위치를 원자 사이로 오해"

VERIFIED = {"layer5": "F1~F7 통과", "at": "T12 P1 층5 첫 적용", "by": "독립 패스"}
VERIFIED_FIXED = {"layer5": "F2 지적 후 조치·재통과", "at": "T12 P1 층5 첫 적용",
                  "by": "독립 패스", "note": "오답 ③ 이 사실 진술이라 복수 정답 위험 → 오개념형으로 교체"}

PAGE = {'M01807': 70, 'M01808': 71, 'M01809': 71, 'M01810': 71, 'M01811': 71,
        'M01812': 70, 'M01813': 72, 'M01814': 72, 'M01815': 72, 'M01816': 72}
OBJ = {
 'M01807': "모형 변천에서 어떤 발견이 어떤 명제를 뒤집었는지 짝짓기",
 'M01808': "실험 결과에서 성질을 추론 — 밀림 = 질량",
 'M01809': "실험 결과에서 성질을 추론 — 그림자 = 직진성",
 'M01810': "실험 결과에서 성질을 추론 — 휘는 방향 = 전하 부호",
 'M01811': "불변량(비전하)에서 입자의 동일성을 추론",
 'M01812': "모형의 내용을 다른 모형과 구별",
 'M01813': "모형으로부터 실험 결과를 예측",
 'M01814': "실험 결과에서 구조를 추론 — 통과 = 빈 공간",
 'M01815': "실험 결과에서 구조를 추론 — 되튐 = 작고 무거운 (+)덩어리",
 'M01816': "모형의 한계를 이론과의 모순으로 설명",
}
PRE = {
 'M01807': ["돌턴 원자설"], 'M01808': ["힘과 질량"], 'M01809': ["빛의 직진과 그림자"],
 'M01810': ["전하의 인력·척력"], 'M01811': ["비(比)의 불변성"], 'M01812': ["전하의 상쇄"],
 'M01813': ["톰슨 모형의 전하 분포"], 'M01814': ["원자의 크기"],
 'M01815': ["전하의 척력", "질량과 운동량"], 'M01816': ["원운동", "전자기파 방출"],
}


def apply(bank):
    idx = {x['id']: x for x in bank}
    # 1) F2 조치
    it = idx['M01814']
    assert OLD in it['choices'], "M01814 오답 ③ 을 찾지 못함"
    it['choices'][it['choices'].index(OLD)] = NEW
    for d in it['distractors']:
        if d.get('error') == OLD_ERR:
            d['error'] = NEW_ERR
    it['solution'] = (it['solution'].replace(OLD, NEW)
                                    .replace(OLD_WMAP, NEW_WMAP)
                                    .replace(OLD_TAIL, NEW_TAIL))
    assert NEW in it['solution'] and OLD not in it['solution'], "해설 반영 실패"
    # 2) 층5 통과 기록 + 스키마 채우기
    for fid in PAGE:
        x = idx[fid]
        x['source_page'] = PAGE[fid]
        x['objective'] = OBJ[fid]
        x['prereq'] = PRE[fid]
        x['verified'] = VERIFIED_FIXED if fid == 'M01814' else VERIFIED
    return bank


if __name__ == '__main__':
    bank = json.load(open(BANK, encoding='utf-8'))
    bank = apply(bank)
    idx = {x['id']: x for x in bank}
    x = idx['M01814']
    print("M01814 조치 후 보기:")
    for i, c in enumerate(x['choices']):
        print(f"   {'①②③④'[i]} {len(c):3d}자 {'★' if i == x['answer'] else ' '} {c}")
    sys.path.insert(0, HERE)
    from batch_template import len_rank, spread
    print(f"   순위{len_rank(x)} 산포{spread(x['choices']):.2f}")
    n = sum(1 for y in bank if (y.get('verified') or {}).get('layer5'))
    print(f"\n층5 통과 기록: {n}제 · source_page {sum(1 for y in bank if y.get('source_page'))}제")
    if '--apply' in sys.argv:
        json.dump(bank, open(BANK, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
        print("✅ 반영 완료")
    else:
        print("※ 검증만. 반영하려면 --apply")
