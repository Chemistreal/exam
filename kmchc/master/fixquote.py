# -*- coding: utf-8 -*-
"""fixquote — 해설이 오답을 ★줄여 인용한 자리★ 를 문면 그대로로 되돌린다

  쓰임:  python3 fixquote.py <초안.json> [--write]

  ★왜 세우는가★ — 저작 에이전트는 한국어를 곱게 적으려고 '…정사면체형이다' 를
  '…정사면체형이라고 했어' 로 줄여 인용한다. 그런데 이 은행의 규약은 ★오답을 문면 그대로 인용★
  하는 것이다('…정사면체형이다라고 했어'). 어색해 보여도 그래야 ★선지를 갈 때 해설이 함께 끌려온다★
  (인용이 문면과 한 글자라도 다르면 STALE 검사가 눈멀고, 조치가 해설을 남겨 둔다).
  ▸ T18P11 이 열 문항 가운데 여섯에서 이렇게 줄여 인용했다 — 한 배치에 여섯이면 손으로 고칠 일이 아니다.
"""
import io
import json
import sys


def main():
    src = sys.argv[1]
    write = '--write' in sys.argv
    d = json.load(io.open(src, encoding='utf-8'))
    fixed = miss = 0
    for x in d['items']:
        for w in x['wrongs']:
            t = w['text']
            if t in x['prose']:
                continue
            done = False
            for cut in (1, 2):
                #  '…이다' → '…이라고' 처럼 끝 글자를 덜어 인용한 자리
                short = t[:-cut] + '라고'
                if short in x['prose']:
                    x['prose'] = x['prose'].replace(short, t + '라고')
                    fixed += 1
                    done = True
                    break
            if not done:
                miss += 1
                print('  ✗ %s — 인용을 찾지 못했다: 「%s」' % (x['id'], t[:26]))
    print('  되돌린 인용 %d · 못 찾은 것 %d' % (fixed, miss))
    if write and not miss:
        json.dump(d, io.open(src, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
        print('  ✅ 초안에 썼다')
    elif write:
        print('  ⛔ 못 찾은 것이 있어 쓰지 않았다')


if __name__ == '__main__':
    main()
