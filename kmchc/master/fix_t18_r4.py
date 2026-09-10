# -*- coding: utf-8 -*-
"""fix_t18_r4 — T18 P2·P3 4차 검증 순회 조치 (P1 은 같은 회차에 먼저 고쳤다)

  ★4차 결과 — 세 범위 모두 solver 30/30 · 차단 0 · factchecker ✗0★ (세 순회 연속).
  defender 는 P1 1 · P2 1 · P3 3 으로 줄었고, ★3차에 세운 잣대로 세 건이 오탐으로 갈렸다★:
    · M02982④ '전자쌍 수는 결합한 원자 수와 늘 같다' — 변호자 스스로 "오답으로 만드는 것은
      '늘' 한 단어뿐" 이라 적었다. 전칭이 있으면 그 자체로 거짓이다 → 오탐.
    · M02984④ '반발 이론은 어떤 각이든 값을 내준다' — 변호자가 "전칭 독법에서는 오답이
      유지된다" 로 닫았다 → 오탐.
  남은 둘은 ★인식 동사와 겹뜻★ 이라는 새 갈래다.
    ㉦ M02973② '분자식을 보면 결합각을 곧바로 알 수 있다' — ★'알 수 있다' 는 인식 동사★ 다.
      분자식에서 전자점식을 거쳐 각까지 유일하게 따라 나오므로 '알 수 있다' 는 참이 된다.
      이 문항이 재는 것은 ★표기가 무엇을 담는가★ 이므로 ★담김의 말로 고쳐 적는다★.
    ㉧ M02983② '모양 이름에도 비공유 전자쌍까지 세어 붙인다' — '센다' 가 ★고려한다★ 로도
      ★꼭짓점으로 센다★ 로도 읽힌다. 앞의 뜻으로는 참이다(삼각뿔형과 굽은형이 비공유쌍 수로
      갈리니까) → ★'꼭짓점으로' 를 문면에 박아 뜻을 하나로 만든다★.
"""
import json

S = '/tmp/claude-0/-home-user-exam/5f2ecfac-9847-5091-89ed-a121f3b6410f/scratchpad'


def item(d, mid):
    return [x for x in d['items'] if x['id'] == mid][0]


def swap_choice(x, old, new):
    s = json.dumps(x, ensure_ascii=False)
    assert old in s, '선지 문면을 찾지 못했다: %s' % old
    y = json.loads(s.replace(old, new))
    x.clear()
    x.update(y)


def sub(x, field, old, new):
    assert old in x[field], '%s %s 에서 찾지 못했다: %s' % (x['id'], field, old[:44])
    x[field] = x[field].replace(old, new)


def retort(x, text, new):
    for w in x['wmap']:
        if w['text'] == text:
            w['retort'] = new
            return
    raise SystemExit('되받이를 찾지 못했다: %s' % text[:40])


def note(x, text, new):
    for w in x['wrongs']:
        if w['text'] == text:
            w['note'] = new
            return
    raise SystemExit('오답 주석을 찾지 못했다: %s' % text[:40])


def p2():
    p = S + '/t18p2_draft.json'
    d = json.load(open(p, encoding='utf-8'))

    x = item(d, 'M02972')                        # △ '원자 넷이 붙은' 이 두 뜻으로 읽힌다
    swap_choice(x, '원자 넷이 붙은 분자는 모두 평면이다', '원자가 모두 넷이면 평면 분자가 된다')
    retort(x, '원자가 모두 넷이면 평면 분자가 된다', '암모니아가 반례')
    note(x, '원자가 모두 넷이면 평면 분자가 된다',
         '암모니아도 원자가 넷이지만 삼각뿔형이라 한 평면에 놓이지 않는다.')

    x = item(d, 'M02973')                        # ㉦ 인식 동사를 담김의 말로
    swap_choice(x, '분자식을 보면 결합각을 곧바로 알 수 있다', '분자식 표기 안에 결합각이 함께 적혀 있다')
    retort(x, '분자식 표기 안에 결합각이 함께 적혀 있다', '개수만 적혀 있어')
    note(x, '분자식 표기 안에 결합각이 함께 적혀 있다',
         '분자식은 원자의 종류와 개수만 적는 표기여서 각이 적힐 자리가 없다.')

    x = item(d, 'M02974')                        # △ 모양 이름 하나로 각이 정해지지는 않는다
    sub(x, 'proof', '분자 모양이 정해지면', '전자쌍 자리 수와 비공유 전자쌍 수까지 정해지면')
    json.dump(d, open(p, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    print('  P2 — M02972 · M02973 · M02974')


def p3():
    p = S + '/t18p3_draft.json'
    d = json.load(open(p, encoding='utf-8'))

    x = item(d, 'M02975')                        # △ 탄소의 홀전자 넷은 전자점식 규약의 값이다
    sub(x, 'calc', '탄소 4', '전자점식에서 세면 탄소 4')

    x = item(d, 'M02977')                        # △ 계산 줄이 스스로 어긋나 보인다(1 + 1쌍 = 2)
    sub(x, 'calc', '수소 1 + 공유 1쌍 → 둘레 2', '수소 1 + 상대 1 → 공유 1쌍 → 둘레 2')

    x = item(d, 'M02983')                        # ㉧ '센다' 의 겹뜻을 '꼭짓점으로' 로 닫는다
    swap_choice(x, '모양 이름에도 비공유 전자쌍까지 세어 붙인다', '모양 이름은 비공유쌍 자리도 꼭짓점으로 센다')
    retort(x, '모양 이름은 비공유쌍 자리도 꼭짓점으로 센다', '꼭짓점은 원자만')
    note(x, '모양 이름은 비공유쌍 자리도 꼭짓점으로 센다',
         '비공유쌍 수는 이름을 가르는 데 쓰지만, 꼭짓점으로 세는 것은 원자가 놓인 자리뿐이다.')
    json.dump(d, open(p, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    print('  P3 — M02975 · M02977 · M02983')


if __name__ == '__main__':
    p2()
    p3()
    print('✅ 4차 조치 여섯 자리 — draftcheck → render_batch → patch_batch')
