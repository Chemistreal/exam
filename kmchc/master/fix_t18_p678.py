# -*- coding: utf-8 -*-
"""T18 P6·P7·P8 초안 손질 — draftcheck 가 짚은 자리를 초안에서 고친다

  ★셋 다 저작 규약을 몸에 익히지 못해 생긴 자리다★
    ㉠ P8 은 해설의 선지 번호를 ★아라비아 숫자★ 로 적고 wmap 열쇠를 줄여 적었다
       (열쇠는 선지 문면과 ★한 글자도 다르지 않아야★ 되받이가 붙는다).
    ㉡ P6 M03007 은 정답을 자리표와 다른 칸에 두었다 — 칸을 옮기면 ★해설의 번호도 함께★ 움직인다.
    ㉢ 발문과 낱말이 정답만 많이 겹치면(P6 M03013 · P7 M03022) 뜻을 몰라도 정답이 짚힌다.
       ★오답 하나에 같은 낱말을 심어 동률로 만드는 것이 문면을 덜 흔든다.★
"""
import json
import re
import sys

S = '/tmp/claude-0/-home-user-exam/5f2ecfac-9847-5091-89ed-a121f3b6410f/scratchpad/'
MK = '①②③④'


def load(f):
    return json.load(open(S + f, encoding='utf-8'))


def save(d, f):
    json.dump(d, open(S + f, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)


def item(d, mid):
    return [x for x in d['items'] if x['id'] == mid][0]


def retext(d, mid, old, new):
    """문항 블록 안의 같은 문면을 모두 갈아 끼운다(선지·오답·되받이 열쇠·해설 인용)."""
    xs = d['items']
    k = [i for i, x in enumerate(xs) if x['id'] == mid][0]
    s = json.dumps(xs[k], ensure_ascii=False)
    if new in s and old not in s:
        return
    assert old in s, '%s — 찾지 못했다: %s' % (mid, old)
    xs[k] = json.loads(s.replace(old, new))
    print('  %s ← %s (%d자)' % (mid, new, len(new)))


#  ── P6 ────────────────────────────────────────────────────────────────
p6 = load('t18p6_draft.json')

#  M03007 정답이 둘째 칸에 있었다 — 자리표는 셋째 칸이다. 둘째와 셋째를 맞바꾼다.
x = item(p6, 'M03007')
assert x['answer'] == 1
x['choices'][1], x['choices'][2] = x['choices'][2], x['choices'][1]
x['answer'] = 2
x['prose'] = (x['prose'].replace('— ②가 옳아', '— ③이 옳아')
              .replace('③은 공유 전자쌍이 넷이니', '②는 공유 전자쌍이 넷이니'))
x['diag'] = x['diag'].replace('③은 쌍 수를', '②는 쌍 수를')
x['calc'] = x['calc'].replace('· ③쌍의 수를', '· ②쌍의 수를')
print('  M03007 정답 칸 ② → ③ · 해설 번호도 함께 옮겼다 · %s' % [len(c) for c in x['choices']])

#  M03013 정답만 발문과 낱말이 둘 겹쳤다 — 정답에서 발문의 낱말을 뺀다
retext(p6, 'M03013', '가운데 원자를 정한 뒤에 모양을 적는다', '중심을 먼저 정한 뒤에 모양을 적는다')
save(p6, 't18p6_draft.json')

#  ── P7 ────────────────────────────────────────────────────────────────
p7 = load('t18p7_draft.json')
#  M03022 정답만 '자리·전자쌍' 둘을 겹쳤다 — 오답 ① 에 '전자쌍' 을 심어 동률로 만든다(22자 그대로)
retext(p7, 'M03022', '비공유가 늘어난 만큼 자리 수도 늘어난다', '비공유 전자쌍이 늘면 자리 수도 늘어난다')
save(p7, 't18p7_draft.json')

#  ── P8 ────────────────────────────────────────────────────────────────
p8 = load('t18p8_draft.json')
for x in p8['items']:
    a = x['answer']
    p = x['prose']
    #  ★해설의 선지 번호를 동그라미 숫자로★ — '2가 옳아' · "3은 '…'라고 했어" 꼴만 바꾼다
    p = re.sub(r'(?<![0-9.])([1-4])([이가] 옳아)', lambda m: MK[int(m.group(1)) - 1] + m.group(2), p)
    p = re.sub(r'(?<![0-9.])([1-4])([은는] [\'"])', lambda m: MK[int(m.group(1)) - 1] + m.group(2), p)
    x['prose'] = p
    #  ★되받이 열쇠는 선지 문면과 한 글자도 다르지 않아야 한다★ — 오답 차례대로 다시 박는다
    if [w['text'] for w in x['wmap']] != [w['text'] for w in x['wrongs']]:
        for w, src in zip(x['wmap'], x['wrongs']):
            w['text'] = src['text']
save(p8, 't18p8_draft.json')
print('  P8 — 해설 번호를 동그라미로, 되받이 열쇠를 선지 문면으로 다시 박았다')
