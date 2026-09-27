"""T12 P9 9차 순회 조치 — solver 0 · ★defender 0(F2 후보 없음, 처음)★ · factchecker ✗1

■ 채택 M01889 ③ 반박 — ★8차에 내가 새로 쓴 한 줄이 틀렸다★
  8차에 ③을 "수소 분자 1 mol 이 지닌 에너지"로 바꾸면서 반박을
  "분자 1 mol 이면 원자가 2 mol 이라 값도 달라진다"라고 적었다. ★개수 환산 논리다.★
  · 산술(1 mol H₂ = 2 mol H)만 떼면 참이고 결론("값이 달라진다")도 참이지만,
    ★근거로 제시된 추론이 성립하지 않는다★ — "적용은 되는데 개수가 달라 값이 다르다"로 읽힌다.
  · 실제로 H₂ 의 전자 에너지는 원자 준위의 2배가 아니다. 분자 오비탈을 이루므로 바닥 상태
    2 H 보다 결합 에너지(약 436 kJ/mol)만큼 더 낮다 — 어떤 정수배도 아니다.
  · 더 근본적으로 ★Eₙ = −1312/n² 은 핵 하나에 전자 하나인 수소꼴 원자에만 성립하는 식★ 이고,
    분자에는 이런 n 준위가 ★아예 없다.★ 갖다 댈 대상 자체가 없는 것이지 배수가 다른 것이 아니다.
  · 학생이 얻어 갈 잘못된 규칙이 정확히 여기다 — "분자면 원자 수만큼 곱하면 된다".
    뒤에 이온화 에너지·결합 에너지를 다룰 때 그대로 사고가 난다.
  ▸ 근거를 ★개수 환산에서 적용 범위로★ 옮긴다.
  ▸ 오답 유형도 'scale'(눈금·배수)에서 ★'overgen'(적용 범위를 넘겨 씀)★ 으로 고친다 —
    이 오답이 겨누는 오류는 배수 착각이 아니라 ★식을 제 자리 밖으로 끌고 가는 것★ 이다.

  ★교훈★ — 8차에서 나는 '틀을 바꾸는' 큰 조치를 했고, 그 새 문면은 앞선 여덟 회의 검증을
  거치지 않은 것이었다. ★큰 조치를 한 회차의 산출물은 반드시 다음 회차에서 새로 검증된다★ 는 것이
  재순회 규칙의 값어치다. defender 가 0 을 냈어도 factchecker 가 이 한 줄을 잡았다.
"""
import json, os

BANK = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'master_bank.json')

SUB = [
    ('M01889', 'answer_proof',
     '수소 분자 1 mol 이라면 원자가 2 mol 이라 값이 달라진다',
     '수소 분자에는 이런 n 준위가 아예 없어 이 식을 갖다 댈 수 없다'),
    ('M01889', 'solution',
     '③ 수소 분자 1 mol 이 지닌 에너지: 이 식은 수소 원자의 준위를 주는 거야. '
     '분자 1 mol 이면 원자가 2 mol 이라 값도 달라지지.',
     '③ 수소 분자 1 mol 이 지닌 에너지: 이 식은 핵 하나에 전자 하나인 수소 원자의 준위를 주는 거야. '
     '분자에는 이런 n 준위가 아예 없어서 갖다 댈 수가 없지.'),
]

ERR_SUB = [
    ('M01889', 2,
     '이 식은 수소 원자의 준위를 준다. 분자 1 mol 이면 원자가 2 mol 이라 값도 달라진다',
     '이 식은 핵 하나에 전자 하나인 수소 원자의 준위를 준다. 분자에는 이런 n 준위가 아예 없어 갖다 댈 수 없다'),
]
TYPE_SUB = [('M01889', 2, 'overgen')]


def main():
    bank = json.load(open(BANK, encoding='utf-8'))
    d = {x['id']: x for x in bank}
    n = 0
    for fid, field, old, new in SUB:
        x = d[fid]
        assert old in x[field], f'{fid}.{field}: 대상 문면 없음'
        x[field] = x[field].replace(old, new, 1); n += 1
    for fid, opt, old, new in ERR_SUB:
        w = [y for y in d[fid]['distractors'] if y['opt'] == opt][0]
        assert w['error'] == old, f'{fid} opt{opt}: error 어긋남 -> {w["error"]}'
        w['error'] = new; n += 1
    for fid, opt, t in TYPE_SUB:
        w = [y for y in d[fid]['distractors'] if y['opt'] == opt][0]
        assert w['type'] != t
        w['type'] = t; n += 1

    x = d['M01889']
    for w in x['distractors']:
        assert x['choices'][w['opt']] in x['solution'], f'해설에 오답 문면 없음 {w["opt"]}'
    assert x['choices'][x['answer']] in x['solution']
    assert len(x['solution']) >= 300
    for f in ('stem', 'solution'):
        for bad in ('**', '★'):
            assert bad not in x[f]
    blob = json.dumps(x, ensure_ascii=False)
    for p in ('원자가 2 mol', '이온화'):
        assert p not in blob, f'M01889: 걷어낸 문면 잔존 -> {p}'
    assert '갖다 댈' in blob, 'M01889: 적용 범위 논거가 들어가지 않았다'

    json.dump(bank, open(BANK, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    print(f'P9 9차 조치 {n}곳 · 채택 1(factchecker ✗) · defender 0')
    print('  M01889 ③', x['distractors'][2]['type'], '|', x['distractors'][2]['error'])


if __name__ == '__main__':
    main()
