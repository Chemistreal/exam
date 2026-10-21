# -*- coding: utf-8 -*-
"""fix_t18_r5 — T18 5차 조치 (P1·P3 는 △ 만, P2 는 defender 둘)

  ★5차 — P1 과 P3 가 세 게이팅 동시 0건에 닿았다★ (solver 10/10 · 차단 0 · defender 없음 · factchecker ✗0).
  이 은행에서 ★처음★ 이다. P2 만 defender 둘이 남았고, 둘 다 ★낱말의 겹뜻★ 이라는 같은 갈래다.

  ㉨ ★'퍼진다' 와 '입체 구조' 는 뜻이 둘이다★
     M02966① '공유 전자쌍이 비공유 전자쌍보다 더 퍼진다' — 공유 전자쌍은 두 핵에 걸쳐 있으니
       ★분포가 걸친 범위★ 로 읽으면 참이다. 이 문항이 재는 것은 ★중심 원자 곁에서 차지하는 폭★
       이므로 그 뜻으로 못 박는다.
     M02972① '굽은형은 꺾여 있으니 입체 구조의 분자이다' — 교과서가 '입체 구조' 를 3차원 기하
       구조 전반(직선형·굽은형까지)으로 흔히 쓴다. 그 관용에서는 참이다 → ★'한 평면에 못 놓인다'★
       로 겨냥을 옮긴다. 4차의 ㉦㉧(인식 동사·겹뜻)과 같은 갈래이고, ★이 갈래가 T18 에서 넷을 물었다★.

  △ 넷은 해설만 손댄다 — 셋을 지나며 두 번 되풀이된 자리다.
    · 등간격 2.5도(M02964) — 반올림에서 생긴 우연을 규칙으로 읽히게 둔다
    · '같은 정사면체'(M02963) — 기준 배열이라는 말을 빠뜨리면 107·104.5도와 부딪친다
    · '자리가 늘면 좁아져'(M02969) — 자리 2~4 라는 범위가 본문에만 빠져 있었다
    · 결합각의 값까지 곧바로(M02974) — 자리 4·비공유 2 라도 황화 수소는 92도다
"""
import json

S = '/tmp/claude-0/-home-user-exam/5f2ecfac-9847-5091-89ed-a121f3b6410f/scratchpad'


def item(d, mid):
    return [x for x in d['items'] if x['id'] == mid][0]


def swap_choice(x, old, new):
    s = json.dumps(x, ensure_ascii=False)
    if new in x['choices'] and old not in s:
        return
    assert old in s, '선지 문면을 찾지 못했다: %s' % old
    y = json.loads(s.replace(old, new))
    x.clear()
    x.update(y)


def sub(x, field, old, new):
    #  ★두 번 돌려도 되게★ — 앞 판이 P1 만 쓰고 P2 에서 죽은 적이 있다(파일마다 따로 쓰기 때문).
    if new in x[field] and old not in x[field]:
        return
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


def p1():
    p = S + '/t18p1_draft.json'
    d = json.load(open(p, encoding='utf-8'))
    x = item(d, 'M02963')
    sub(x, 'prose', '둘 다 네 쌍이니 배열은 같은 정사면체야', '둘 다 네 쌍이니 기준 배열은 같은 정사면체야')
    x = item(d, 'M02964')
    sub(x, 'calc', '109.5 - 107 = 2.5 → 107 - 104.5 = 2.5',
        '109.5 > 107 > 104.5 → 세 값은 외워 두고 간격은 규칙이 아님')
    json.dump(d, open(p, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    print('  P1 — M02963 · M02964 (△ 만)')


def p2():
    p = S + '/t18p2_draft.json'
    d = json.load(open(p, encoding='utf-8'))

    x = item(d, 'M02966')                                   # ㉨ '퍼진다' 의 겹뜻
    swap_choice(x, '공유 전자쌍이 비공유 전자쌍보다 더 퍼진다', '공유 전자쌍이 중심 곁을 더 넓게 차지한다')
    retort(x, '공유 전자쌍이 중심 곁을 더 넓게 차지한다', '비공유가 더 넓어')
    note(x, '공유 전자쌍이 중심 곁을 더 넓게 차지한다',
         '비공유 전자쌍은 핵 하나에만 매여 중심 곁을 더 넓게 차지하고, 그래서 더 세게 밀친다.')

    x = item(d, 'M02969')                                   # △ 자리 수 규칙의 범위를 본문에도
    sub(x, 'prose', '자리가 늘면 각은 좁아져', '자리가 둘에서 넷으로 늘면 각은 좁아져')

    x = item(d, 'M02972')                                   # ㉨ '입체 구조' 의 겹뜻
    swap_choice(x, '굽은형은 꺾여 있으니 입체 구조의 분자이다', '굽은형은 꺾여 있으니 한 평면에 못 놓인다')
    retort(x, '굽은형은 꺾여 있으니 한 평면에 못 놓인다', '원자 셋은 한 면')
    note(x, '굽은형은 꺾여 있으니 한 평면에 못 놓인다',
         '원자가 셋이면 어떻게 꺾여도 한 평면에 놓인다. 평면을 벗어나려면 원자가 넷 이상이어야 한다.')

    x = item(d, 'M02974')                                   # △ 각의 값까지 곧바로는 대표 분자에서만
    sub(x, 'proof', '모양 이름, 결합각, 모든 원자가 한 평면에 놓이는지',
        '모양 이름과 모든 원자가 한 평면에 놓이는지, 그리고 교과서가 외워 두라는 대표 결합각')
    json.dump(d, open(p, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    print('  P2 — M02966 · M02969 · M02972 · M02974')


def p3():
    p = S + '/t18p3_draft.json'
    d = json.load(open(p, encoding='utf-8'))
    x = item(d, 'M02982')
    sub(x, 'diag', '쌍을 세는 규약과 자리를 세는 규약을 갈라 두지 못한 것이다',
        '쌍을 세는 규약과 자리를 세는 규약을 갈라 두지 못한 것이다. 한 자리로 묶는 것은 배열을 정할 때만이다')
    x = item(d, 'M02984')
    sub(x, 'calc', '재어진 각은 120도보다 좁음', '재어진 각은 120도보다 아주 조금 좁음')
    json.dump(d, open(p, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    print('  P3 — M02982 · M02984 (△ 만)')


if __name__ == '__main__':
    p1()
    p2()
    p3()
    print('✅ 5차 조치 여덟 자리')
