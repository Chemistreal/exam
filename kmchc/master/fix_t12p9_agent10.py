"""T12 P9 10차 순회 조치 — solver 0 · defender 0(2회 연속) · factchecker ✗0 △1

■ 채택 M01889 ③ 반박 — ★9차에 내가 쓴 문면이 이번엔 과했다★
  9차에 "분자 1 mol 이면 원자가 2 mol 이라 값이 달라진다"(개수 환산 오류)를 고치면서
  "분자에는 이런 n 준위가 ★아예 없어★ 갖다 댈 수 없다"로 적었다. ★전칭 부정이 지나치다.★
  · 분자에도 n 으로 이름 붙는 준위가 있다 — 수소 분자의 리드베리 상태는 관례적으로 주양자수 n 으로
    표기되고 E = IE − R/(n−δ)² 꼴의 계열을 이룬다. "아예 없다"는 이 사실과 충돌한다.
  · ★게다가 같은 배치와 어긋난다★ — M01893 은 ②에서 "떨림은 적외선의 몫"(분자의 진동 준위가
    양자화되어 있다)이라 하고 ④에서 물 분자의 이온화 에너지를 말한다. 둘 다 분자에 준위 구조가
    있다는 전제 위에 서 있다. 이어 읽는 학생에게 M01889 가 그 둘을 부정하는 것으로 보인다.
  · 학생이 얻어 갈 잘못된 규칙도 여기다 — "분자에는 준위가 없다". 다음 단원의 뼈대를 무너뜨린다.
  ▸ ★오답을 쳐내는 데 필요한 것은 그보다 훨씬 좁다★ — 이 식이 핵 하나·전자 하나인 계의 식이라는 것
    하나면 충분하다. 분자 쪽에 없는 성질을 지어 붙일 이유가 없었다((dd) 재발).
  ▸ "이 식은 핵 하나에 전자 하나인 계에만 들어맞는다. 수소 분자는 핵도 둘이고 전자도 둘이라
    이 식으로는 준위가 나오지 않는다"로 바꾼다. ★식의 적용 범위만 말하고 분자의 성질은 말하지 않는다.★

  ★이 한 줄이 8·9·10차 세 회차를 끌었다.★ 기록해 둔다 —
  (8차) 이온화 틀을 버리며 새로 씀 → 개수 환산 논리라 근거가 성립하지 않음
  (9차) 적용 범위로 옮김 → '분자에는 준위가 없다'는 전칭 부정으로 과했음
  (10차) 적용 범위를 ★식 쪽에만★ 걸어 마무리
  ◆교훈: 틀을 갈아 끼운 자리는 ★한 번에 맞지 않는다.★ 새 문면은 앞선 회차의 검증을 받지 않은
    것이므로, 큰 조치 뒤에는 순회를 최소 두 번 더 돌 각오를 하고 시작할 것.◆
"""
import json, os

BANK = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'master_bank.json')

SUB = [
    ('M01889', 'answer_proof',
     '수소 분자에는 이런 n 준위가 아예 없어 이 식을 갖다 댈 수 없다',
     '이 식은 핵 하나에 전자 하나인 계에만 들어맞아 핵도 둘이고 전자도 둘인 수소 분자에는 쓸 수 없다'),
    ('M01889', 'solution',
     '③ 수소 분자 1 mol 이 지닌 에너지: 이 식은 핵 하나에 전자 하나인 수소 원자의 준위를 주는 거야. '
     '분자에는 이런 n 준위가 아예 없어서 갖다 댈 수가 없지.',
     '③ 수소 분자 1 mol 이 지닌 에너지: 이 식은 핵 하나에 전자 하나인 계에만 들어맞아. '
     '수소 분자는 핵도 둘이고 전자도 둘이라 이 식으로는 준위가 나오지 않지.'),
]

ERR_SUB = [
    ('M01889', 2,
     '이 식은 핵 하나에 전자 하나인 수소 원자의 준위를 준다. 분자에는 이런 n 준위가 아예 없어 갖다 댈 수 없다',
     '이 식은 핵 하나에 전자 하나인 계에만 들어맞는다. 수소 분자는 핵도 둘이고 전자도 둘이라 '
     '이 식으로는 준위가 나오지 않는다'),
]


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

    x = d['M01889']
    for w in x['distractors']:
        assert x['choices'][w['opt']] in x['solution'], f'해설에 오답 문면 없음 {w["opt"]}'
    assert x['choices'][x['answer']] in x['solution']
    assert len(x['solution']) >= 300
    for f in ('stem', 'solution'):
        for bad in ('**', '★'):
            assert bad not in x[f]
    blob = json.dumps(x, ensure_ascii=False)
    # ★분자의 성질을 말하지 않는다 — 식의 적용 범위만 말한다★
    for p in ('아예 없', '원자가 2 mol', '이온화'):
        assert p not in blob, f'M01889: 걷어낸 문면 잔존 -> {p}'
    assert '핵 하나에 전자 하나인 계' in blob, 'M01889: 적용 범위 논거가 없다'
    assert '핵도 둘이고 전자도 둘' in blob, 'M01889: 분자 쪽 대비가 없다'

    json.dump(bank, open(BANK, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    print(f'P9 10차 조치 {n}곳 · 채택 1(factchecker △) · defender 0(2회 연속)')
    print('  M01889 ③', x['distractors'][2]['error'])


if __name__ == '__main__':
    main()
