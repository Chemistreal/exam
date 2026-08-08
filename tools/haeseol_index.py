#!/usr/bin/env python3
"""해설 목차(`index_haeseol.html`)가 실제 회차와 맞는지 본다.

이 장은 손으로 카드를 붙여 온 목차다. 회차를 새로 넣어도 여기까지 오는
길이 없어서, 넣은 회차의 해설지가 목차에 안 뜬 채로 있었다 — 화올
2009·2010·2011·2012 넷이 그랬다.

카드에는 '삭제 34' · '전원 47 · 50 · 60' 처럼 **전원정답 문항**을 적어 둔다.
그것도 손으로 적어 온 것이라 넷이 빠져 있었고, jmchc-9 는 50번이 빠져
있었다(채점은 50번도 전원정답으로 친다).

여기서 보는 것.

  ① 카드가 거는 해설지가 실제로 있는가
  ② 카드에 적힌 전원정답 문항이 채점 자료(exams.json)와 같은가
  ③ 화올·JMChC 회차 가운데 카드가 없는 것이 있는가

  이 목차는 두 갈래만 싣는다(KMChC 화올 · JMChC 모의고사). 산과염기 60제 ·
  기출동형 · 심화 회차는 일부러 안 싣는 것이라 여기서 따지지 않는다.

    python3 tools/haeseol_index.py           # 어긋난 곳
    python3 tools/haeseol_index.py --check   # 어긋나면 빨간불 (CI용)
"""
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PAGE = os.path.join(ROOT, 'index_haeseol.html')

# 이 목차가 싣는 갈래
FAMILY = ('hwol-', 'jmchc-')


def allc(e):
    """전원정답인 문항 번호. miss · voided · 보기 넷을 다 인정한 multi 를 합친다."""
    out = set(e.get('miss') or []) | set(e.get('voided') or [])
    for k, v in (e.get('multi') or {}).items():
        if len(v) >= 4:
            out.add(int(k))
    return sorted(out)


def main():
    check = '--check' in sys.argv
    src = open(PAGE, encoding='utf-8').read()
    exams = {e['id']: e for e in json.load(
        open(os.path.join(ROOT, 'exams.json'), encoding='utf-8'))}
    bad, seen = [], []

    for m in re.finditer(r'href="sol-final-([^"]+)\.html"[^>]*>(.*?)</a>', src, re.S):
        eid, body = m.group(1), m.group(2)
        seen.append(eid)
        if not os.path.exists(os.path.join(ROOT, 'sol-final-%s.html' % eid)):
            bad.append('%s: 거는 해설지가 없다' % eid)
            continue
        ex = exams.get(eid)
        if not ex:
            bad.append('%s: exams.json 에 없는 회차다' % eid)
            continue
        sp = re.findall(r'<span class="sp">(?:삭제|전원)\s*([\d·, ]+)</span>', body)
        listed = sorted(int(x) for x in re.findall(r'\d+', sp[0])) if sp else []
        real = allc(ex)
        if listed != real:
            bad.append('%s: 전원정답 표기 %s ≠ 채점 자료 %s' % (eid, listed, real))

    for eid in exams:
        if eid.startswith(FAMILY) and eid not in seen:
            bad.append('%s: 목차에 카드가 없다' % eid)

    print('목차의 카드 %d개' % len(seen))
    if bad:
        print('\n어긋난 곳 %d:' % len(bad))
        for b in bad:
            print('  ' + b)
        print('\nexams.json 이 채점의 근거다. 목차를 그쪽에 맞춘다.')
        return 1 if check else 0

    print('목차가 실제 회차와 맞는다.')
    return 0


if __name__ == '__main__':
    try:
        sys.exit(main())
    except BrokenPipeError:
        os._exit(0)
