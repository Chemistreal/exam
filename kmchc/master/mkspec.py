# -*- coding: utf-8 -*-
"""mkspec — 다음 배치의 ★저작 지시서(spec)★ 를 개념 대장에서 뽑아 짓는다

  쓰임:  python3 mkspec.py <테마> <접두사> <배치이름> <시작id> <자리열> <길이순위열> <나갈파일>
  보기:  python3 mkspec.py '분자의 구조' C18 T18P11 M03055 3142314233 3232323232 spec_t18p11.json

  ★왜 도구로 두는가★ — P6~P10 의 지시서를 손으로 다섯 벌 적었다. 같은 일을 세 번 하면
  같은 실수를 세 번 한다. 손으로 적을 때 두 번 샜다.
    ① ★소진한 각도를 다시 집었다★ — concepts.json 의 by 를 눈으로 훑다가 놓친다.
    ② 한 개념에서 각도를 몰아 뽑아 ★배치 안에서 겨냥이 겹쳤다★ — 개념을 돌아가며 집어야 한다.
  그래서 이 파일은 ★by 가 빈 각도만★ 집고, ★개념을 돌아가며★ 하나씩 집는다.

  나가는 꼴은 저작 에이전트가 그대로 읽는 지시서다
    {"batch": "T18P11", "items": [{"id","cid","idx","angle","t","stmt","values","note",
                                   "answer","rank"}, …]}
"""
import io
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
CJ = os.path.join(HERE, 'concepts.json')


def pick(theme, count):
    """★by 가 빈 각도만★ 을, ★개념을 돌아가며★ 하나씩 집는다."""
    cj = json.load(io.open(CJ, encoding='utf-8'))
    cs = cj[theme]
    free = {c['id']: [(k, a) for k, a in enumerate(c['angles']) if not a.get('by')] for c in cs}
    by_id = {c['id']: c for c in cs}
    out, guard = [], 0
    while len(out) < count and guard < count * 40:
        guard += 1
        for cid in sorted(free):
            if not free[cid]:
                continue
            k, a = free[cid].pop(0)
            out.append((by_id[cid], k, a))
            if len(out) == count:
                break
    if len(out) < count:
        raise SystemExit('미소진 각도가 %d 뿐이다 — %d 을 채울 수 없다' % (len(out), count))
    return out


def main():
    if len(sys.argv) < 8:
        print(__doc__)
        return
    theme, prefix, batch, start, col, ranks, out = sys.argv[1:8]
    count = len(col)
    assert len(ranks) == count, '자리열과 길이순위열의 길이가 다르다'
    base = int(start[1:])
    rows = []
    for i, (c, k, a) in enumerate(pick(theme, count)):
        rows.append({'id': 'M%05d' % (base + i), 'cid': c['id'], 'idx': k, 'angle': a['a'],
                     't': a.get('t', '지식'), 'stmt': c['stmt'], 'values': c.get('values', ''),
                     'note': c.get('note', ''),
                     'answer': int(col[i]) - 1, 'rank': int(ranks[i])})
    json.dump({'batch': batch, 'items': rows}, io.open(out, 'w', encoding='utf-8'),
              ensure_ascii=False, indent=1)
    print('✅ %s — %d제 (%s ~ %s)' % (out, count, rows[0]['id'], rows[-1]['id']))
    print('   자리 %s · 길이순위 %s' % (col, ranks))
    for r in rows:
        print('   %s  %s[%d] %s' % (r['id'], r['cid'], r['idx'], r['angle'][:52]))


if __name__ == '__main__':
    main()
