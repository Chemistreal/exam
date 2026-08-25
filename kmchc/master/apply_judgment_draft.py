# -*- coding: utf-8 -*-
"""apply_judgment_draft — 판정 에이전트의 edits 를 ★초안 JSON★ 에 붙인다

  쓰임:  python3 apply_judgment_draft.py <판정.json> <초안.json> [--write]

  ★왜 따로 두는가★ — apply_judgment.py 는 빌더(.py) 를 고친다. 그런데 P6 이후의 배치는
  ★초안 JSON 이 원본★ 이고 빌더는 render_batch 가 다시 찍어 낸다. 빌더만 고치면 다음
  render 에서 ★조치가 조용히 사라진다★. 그래서 초안에 붙이는 길을 따로 낸다.

  판정 에이전트는 ★은행의 필드 이름★ 으로 말한다(stem·choices·answer_proof·calc_check·
  solution·device). 초안의 이름은 다르다 — 그 사이를 여기서 잇는다.
    answer_proof → proof · calc_check → calc · device → dev
    solution     → ★prose · wrongs[].note · diag · lead 를 차례로 뒤진다★
                   (은행의 solution 은 이 넷을 이어 붙여 만든 것이다)
    choices      → choices · wrongs[].text · wmap[].text · prose 의 인용까지 함께
"""
import io
import json
import sys


def apply_choice(x, before, after):
    hit = 0
    for k, c in enumerate(x['choices']):
        if c == before:
            x['choices'][k] = after
            hit += 1
    for w in x['wrongs']:
        if w['text'] == before:
            w['text'] = after
            hit += 1
    for w in x['wmap']:
        if w['text'] == before:
            w['text'] = after
            hit += 1
    if before in x['prose']:
        x['prose'] = x['prose'].replace(before, after)
        hit += 1
    return hit


def apply_sol(x, before, after):
    for fld in ('prose', 'diag', 'lead'):
        if before in x[fld]:
            x[fld] = x[fld].replace(before, after)
            return 1
    for w in x['wrongs']:
        if before in w['note']:
            w['note'] = w['note'].replace(before, after)
            return 1
    for w in x['wmap']:
        if before in w['retort']:
            w['retort'] = w['retort'].replace(before, after)
            return 1
    return 0


MAP = {'answer_proof': 'proof', 'calc_check': 'calc', 'device': 'dev', 'stem': 'stem'}


def main():
    jf, df = sys.argv[1], sys.argv[2]
    write = '--write' in sys.argv
    j = json.load(io.open(jf, encoding='utf-8'))
    rows = j['judge'] if isinstance(j, dict) and 'judge' in j else (j['items'] if isinstance(j, dict) else j)
    d = json.load(io.open(df, encoding='utf-8'))
    by = {x['id']: x for x in d['items']}
    ok = miss = skip = 0
    for r in rows:
        mid = r['id']
        if mid not in by:
            continue
        if r['verdict'].startswith('오탐'):
            print('  · %s 오탐 — %s' % (mid, r['reason'][:70]))
            skip += 1
            continue
        x = by[mid]
        print('  %s 고친다 — %s' % (mid, r['reason'][:70]))
        for e in r['edits']:
            f, b, a = e['field'], e['before'], e['after']
            if f == 'choices':
                n = apply_choice(x, b, a)
            elif f == 'solution':
                n = apply_sol(x, b, a)
            else:
                fld = MAP.get(f, f)
                n = 0
                if b in x[fld]:
                    x[fld] = x[fld].replace(b, a)
                    n = 1
            if n:
                ok += 1
                print('     ✓ %-12s %s' % (f, a[:56]))
            else:
                miss += 1
                print('     ✗ %-12s 찾지 못했다 — %s' % (f, b[:56]))
    print('\n  붙은 고침 %d · 빗나감 %d · 오탐으로 넘긴 문항 %d' % (ok, miss, skip))
    if write and not miss:
        json.dump(d, io.open(df, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
        print('  ✅ 초안에 썼다')
    elif write:
        print('  ⛔ 빗나감이 있어 쓰지 않았다 — before 문면을 다시 볼 것')
    else:
        print('  ※ 쓰지 않았다 — 반영하려면 --write')


if __name__ == '__main__':
    main()
