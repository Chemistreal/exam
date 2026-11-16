# -*- coding: utf-8 -*-
"""fixlib — 조치 회차에서 되풀이되는 손질을 한 자리에 모은다

  ★왜 세우는가★ — 회차마다 fix_t18_rN.py 를 새로 적으면서 같은 함정에 두 번 빠졌다.
    ㉠ 선지를 갈아 끼울 때 ★해설 산문의 되받이★ 를 놓쳤다(M02987 — factchecker 가 잡았다).
       swap 이 wmap 되받이와 오답 주석은 끌어가지만 ★산문의 '…라고 했어. ○○○' 한 마디★ 는
       옛 오답을 반박한 채 남는다. 그러면 해설과 단평이 서로 어긋난다.
    ㉡ 되받이에 한정을 넣다가 ★반박의 방향이 지워졌다★(M02979 — 오답을 승인하는 문장이 되었다).
       ★되받이는 열 자 안팎이라 한정을 넣으면 방향이 먼저 지워진다 — 방향을 지키고 한정은 산문에 둔다.★
  그래서 swap 은 ★산문 되받이까지 함께 받는다★. 넘기지 않으면 화면에 '다시 읽을 것' 으로 남긴다.
"""
import json


def swap(d, mid, old, new, retort=None, note=None, rebut=None, quiet=False):
    """선지를 갈아 끼우고 딸린 자리를 함께 끈다.

      old→new  : 문항 블록 안의 같은 문자열(선지·오답·되받이 열쇠·산문 인용)을 모두 바꾼다
      retort   : wmap 되받이(열 자 안팎 — ★방향을 지킨다★)
      note     : 오답 주석(여기에 한정을 적는다)
      rebut    : ★산문의 '…라고 했어.' 뒤 한 마디★ — 넘기지 않으면 경고를 찍는다
    """
    idx = {x['id']: i for i, x in enumerate(d['items'])}
    x = d['items'][idx[mid]]
    s = json.dumps(x, ensure_ascii=False)
    assert old in s, '%s — 선지 문면을 찾지 못했다: %s' % (mid, old)
    y = json.loads(s.replace(old, new))
    if retort:
        for w in y['wmap']:
            if w['text'] == new:
                w['retort'] = retort
    if note:
        for w in y['wrongs']:
            if w['text'] == new:
                w['note'] = note
    if rebut:
        #  ★인용은 따옴표가 있기도 없기도 하다★ — 배치마다 산문의 버릇이 다르다.
        for head in (new + "'라고 했어. ", new + '라고 했어. ',
                     new + "'라고 했어, ", new + '라고 했어, '):
            i = y['prose'].find(head)
            if i >= 0:
                break
        assert i >= 0, '%s — 산문에서 인용을 찾지 못했다' % mid
        j = i + len(head)
        k = y['prose'].find(' ', j)                       # 다음 마디의 시작
        end = y['prose'].find('. ', j)
        end = (end + 2) if end > 0 else (k if k > 0 else len(y['prose']))
        y['prose'] = y['prose'][:j] + rebut + ('' if rebut.endswith(' ') else ' ') + y['prose'][end:]
    elif not quiet:
        print('     ⚠ %s 산문의 되받이를 다시 읽을 것 — 옛 오답을 반박한 채 남아 있다' % mid)
    d['items'][idx[mid]] = y
    print('  %s ← %s (%d자)' % (mid, new, len(new)))
    return y


def sub(d, mid, field, old, new):
    idx = {x['id']: i for i, x in enumerate(d['items'])}
    x = d['items'][idx[mid]]
    if new in x[field] and old not in x[field]:
        return
    assert old in x[field], '%s %s — 찾지 못했다: %s' % (mid, field, old[:44])
    x[field] = x[field].replace(old, new)
