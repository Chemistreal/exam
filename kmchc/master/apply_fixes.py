# -*- coding: utf-8 -*-
"""apply_fixes — 검토 에이전트가 돌려준 fixes 를 초안 JSON 에 옮겨 붙인다

  쓰임:  python3 apply_fixes.py <초안.json> <fixes.json> <출력.json>

  fixes 의 꼴(검토자 스키마와 같다)
    {"verdict": "...", "fixes": [{"id","field","rule","before","after"}, ...], "facts": [...]}

  ★왜 도구로 두는가★ — 검토 결과를 손으로 옮기면 세 가지가 샌다.
    ① before 가 문면에 없는데도 '고쳤다' 고 여기고 넘어간다(조용히 빗나간다).
    ② 선지를 고치면 ★해설 산문의 인용과 되받이 열쇠★ 가 옛 문면으로 남는다(규약 ⓖ).
    ③ 한 선지를 고치면 ★길이순위와 발문 겹침 셈이 함께 움직인다★(규약 ⓗ).
  이 파일은 ①과 ②를 기계로 막는다. ③은 lenplan·local_checks 가 잡는다.

  ★choices 를 고치면 딸린 자리를 함께 끈다★
    choices[k] 를 바꾸면 wrongs[].text · wmap[].text · prose 안의 인용 · calc 를 ★같은 문자열★
    로 함께 바꾼다. 되받이(wmap[].retort)와 오답 주석(wrongs[].note)은 ★뜻★ 이라 손대지 않는다 —
    바뀐 문면을 반박하지 못하면 사람이 다시 적어야 한다. 그 자리를 화면에 남긴다.
"""
import json
import re
import sys

TEXT_FIELDS = ('stem', 'proof', 'dev', 'calc', 'scenario', 'objective', 'lead', 'prose', 'diag',
               'skill', 'difficulty', 'track')


IDX = None


def apply_one(item, fx, log):
    f, before, after = fx['field'], fx['before'], fx['after']
    #  ★검토자는 'wrongs[2].note' 처럼 자리를 짚어 오기도 한다★ — 그 꼴도 받는다.
    #  선지를 갈면 딸린 자리가 함께 끌려가므로 대개 이미 고쳐져 있고, 그때는 조용히 넘긴다.
    m = re.match(r'(wrongs|wmap)\[(\d+)\]\.(text|note|retort)$', f)
    if m:
        arr, k, key = item[m.group(1)], int(m.group(2)), m.group(3)
        if k >= len(arr):
            log.append('  ❌ %s %s — 자리가 없다' % (item['id'], f))
            return 0
        if arr[k].get(key) == after:
            return 1                                   # 선지 치환이 이미 끌어갔다
        if before and arr[k].get(key) != before:
            log.append('  ❌ %s %s — before 가 다르다' % (item['id'], f))
            return 0
        arr[k][key] = after
        return 1
    if f.startswith('choices'):
        try:
            k = item['choices'].index(before)
        except ValueError:
            log.append('  ❌ %s %s — before 가 선지에 없다: %s' % (item['id'], f, before[:30]))
            return 0
        item['choices'][k] = after
        n = 1
        for w in item['wrongs']:
            if w['text'] == before:
                w['text'] = after
                n += 1
        for w in item['wmap']:
            if w['text'] == before:
                w['text'] = after
                n += 1
                log.append('  ⚠ %s 되받이를 다시 읽을 것 — 「%s」 ← %s'
                           % (item['id'], w['retort'], after[:26]))
        for g in ('prose', 'calc', 'proof'):
            if before in item[g]:
                item[g] = item[g].replace(before, after)
                n += 1
        return n
    if f in TEXT_FIELDS:
        if before not in item[f]:
            log.append('  ❌ %s %s — before 가 없다: %s' % (item['id'], f, before[:30]))
            return 0
        item[f] = item[f].replace(before, after)
        return 1
    if f == 'answer':
        item['answer'] = int(after)
        return 1
    log.append('  ❌ %s — 모르는 칸: %s' % (item['id'], f))
    return 0


def main():
    src, fxs, out = sys.argv[1:4]
    d = json.load(open(src, encoding='utf-8'))
    items = d['items'] if isinstance(d, dict) else d
    by = {x['id']: x for x in items}
    c = json.load(open(fxs, encoding='utf-8'))
    log, hit, miss = [], 0, 0
    for fx in c.get('fixes', []):
        it = by.get(fx['id'])
        if it is None:
            log.append('  ❌ 초안에 없는 id: %s' % fx['id'])
            miss += 1
            continue
        n = apply_one(it, fx, log)
        hit += n
        miss += (n == 0)
    json.dump({'items': items}, open(out, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    print('판정 %s · 고침 %d 건 → 자리 %d 곳 · 빗나감 %d'
          % (c.get('verdict', '?'), len(c.get('fixes', [])), hit, miss))
    for line in log:
        print(line)
    for f in c.get('facts', []):
        print('  ※ 사실 지적 — %s' % f)


if __name__ == '__main__':
    main()
