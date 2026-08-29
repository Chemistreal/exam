#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""회차마다 **성적표가 무엇을 말할 수 있고 무엇이 비는지** 한 판에 편다.

왜 이 자가 있나
---------------
성적표는 절이 스무 개 넘는다. 그런데 절마다 필요한 자료가 다르고, 없으면 그
절이 **조용히 빈칸으로 나가거나 통째로 빠진다.** 어느 회차가 어느 절을 못 채우는지
아무도 세고 있지 않았다 — 선생님이 학부모에게 보낸 뒤에야 알았다.

2026-08-29 실측(52회차 3,060문항):

    문항 줄기+보기      8회차 452문항   ← 동형문제를 **공급**할 수 있는 유일한 자리
    또래 선택 분포(q)   28회차          ← 「또래 선택 ① 2% ② 47%…」
    석차 모집단(hist)   40회차          ← 「연도누적 총석차 45/100」
    선택지별 오개념      12회차 135문항  ← 「왜 틀렸나」의 가장 정확한 근거
    문항별 해설         51회차          ← 「개념 보충」
    크롭(원문 그림)      8회차           ← 오답노트의 「원문 문제」

동형문제가 안 붙는 뿌리가 여기 있다. 줄기와 보기가 있는 문항이 452개뿐이라,
**모든 회차의 모든 동형문제가 그 452개 안에서만** 나온다. 그래서 단원평가끼리는
73~98% 가 붙는데 usnco-2026-natl-1 은 2%, KMChC 심화 두 회차는 0% 다
(tools/twin_cover.py).

⚠ 이 자는 **자료가 있는지**만 본다. 자료의 질(해설이 옳은지, 오개념이 맞는지)은
  사람이 본다. 재는 것과 검수하는 것은 다르다.

    python3 tools/report_data.py            # 회차별 표
    python3 tools/report_data.py --gaps     # 절별로 «못 채우는 회차» 목록
    python3 tools/report_data.py --check    # 채워져 있던 것이 사라지면 빨간불
    python3 tools/report_data.py --seal     # 지금 값을 바닥으로
"""
import collections
import io
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SEAL = os.path.join(ROOT, 'tools', 'report_data.json')

# 성적표의 절 → 그 절이 서려면 있어야 하는 것
NEEDS = [
    ('원문 문제(오답노트)', 'crops', '크롭 이미지'),
    ('동형문제 공급', 'stems', '줄기 + 보기 넷'),
    ('또래 선택 분포', 'q', '보기별 응답 수'),
    ('연도누적 총석차·백분위', 'hist', '점수 분포'),
    ('또래 정답률·신호등·깊이', 'rateOrQc', '문항별 정답자 수'),
    ('왜 틀렸나(선택지별)', 'misc4', '선택지별 오개념'),
    ('개념 보충', 'expl', '문항별 해설'),
    ('문제지 내려받기', 'pdf', '문제지 PDF'),
]


def scan():
    xs = json.load(io.open(os.path.join(ROOT, 'exams.json'), encoding='utf-8'))
    base = json.load(io.open(os.path.join(ROOT, 'cohort', 'baseline.json'),
                             encoding='utf-8'))['exams']
    out = []
    for e in xs:
        eid, nQ = e['id'], e['nQ']
        p = os.path.join(ROOT, 'answers', '%s.json' % eid)
        a = (json.load(io.open(p, encoding='utf-8')).get('questions', {})
             if os.path.exists(p) else {})
        b = base.get(eid) or {}
        out.append({
            'id': eid, 'nQ': nQ,
            'crops': nQ if e.get('crops') else 0,
            'stems': sum(1 for k in a if str(a[k].get('stem') or '').strip()
                         and len(a[k].get('choices') or []) >= 4),
            'q': nQ if b.get('q') else 0,
            'hist': nQ if b.get('hist') else 0,
            'rateOrQc': nQ if (e.get('rate') or b.get('qc')) else 0,
            'misc4': sum(1 for k in a if a[k].get('misconceptions')),
            'expl': sum(1 for k in a if str(a[k].get('explanation') or '').strip()
                        or str(a[k].get('explanationHtml') or '').strip()),
            'pdf': nQ if e.get('pdf') else 0,
        })
    return out


def main():
    check = '--check' in sys.argv
    seal = '--seal' in sys.argv
    gaps = '--gaps' in sys.argv
    rows = scan()
    tq = sum(r['nQ'] for r in rows)

    if gaps:
        for label, key, what in NEEDS:
            miss = [r['id'] for r in rows if r[key] == 0]
            part = [(r['id'], r[key], r['nQ']) for r in rows if 0 < r[key] < r['nQ']]
            print('\n■ %s  — 필요한 것: %s' % (label, what))
            print('   서는 회차 %d/%d · 문항 %d/%d'
                  % (sum(1 for r in rows if r[key]), len(rows),
                     sum(r[key] for r in rows), tq))
            if miss:
                print('   통째로 못 채우는 회차 %d개: %s'
                      % (len(miss), ', '.join(miss[:14]) + (' …' if len(miss) > 14 else '')))
            if part:
                print('   일부만 채운 회차 %d개: %s'
                      % (len(part), ', '.join('%s %d/%d' % x for x in part[:10])))
        return 0

    hdr = '%-24s %4s' % ('회차', '문항') + ''.join('%8s' % k[:7] for _, k, _ in NEEDS)
    print(hdr)
    for r in sorted(rows, key=lambda x: sum(x[k] for _, k, _ in NEEDS)):
        print('%-24s %4d' % (r['id'], r['nQ']) +
              ''.join('%8s' % (r[k] if r[k] else '·') for _, k, _ in NEEDS))
    print('\n합계 문항 %d' % tq)
    for label, key, _ in NEEDS:
        print('  %-24s %5d문항 (%3d%%) · %2d/%d회차'
              % (label, sum(r[key] for r in rows),
                 round(100 * sum(r[key] for r in rows) / tq),
                 sum(1 for r in rows if r[key]), len(rows)))

    now = {r['id']: {k: r[k] for _, k, _ in NEEDS} for r in rows}
    if seal:
        json.dump({'설명': '회차별로 성적표 절이 쓸 수 있는 자료의 문항 수. '
                           '이 수는 **늘기만 한다** — 줄면 빨간불이다.',
                   '바닥': now},
                  io.open(SEAL, 'w', encoding='utf-8'),
                  ensure_ascii=False, indent=1, sort_keys=True)
        io.open(SEAL, 'a', encoding='utf-8').write('\n')
        print('\n지금 값을 tools/report_data.json 에 바닥으로 적었다.')
        return 0

    if not os.path.exists(SEAL):
        print('\n바닥이 없다 — python3 tools/report_data.py --seal 로 적어 둔다.')
        return 1 if check else 0
    was = json.load(io.open(SEAL, encoding='utf-8')).get('바닥', {})
    down = []
    for eid, d in sorted(was.items()):
        cur = now.get(eid)
        if cur is None:
            down.append('%s: 회차가 통째로 사라졌다' % eid)
            continue
        for k, v in d.items():
            if cur.get(k, 0) < v:
                down.append('%s · %s: %d → %d' % (eid, k, v, cur.get(k, 0)))
    if down:
        print('\n**줄었다** %d곳 — 성적표가 말할 수 있던 것을 잃었다:' % len(down))
        for x in down[:24]:
            print('  ' + x)
        return 1 if check else 0
    print('\n성적표가 쓸 수 있는 자료가 줄지 않았다.')
    return 0


if __name__ == '__main__':
    try:
        sys.exit(main())
    except BrokenPipeError:
        os._exit(0)
