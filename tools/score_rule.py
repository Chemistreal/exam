#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""**시험지에 인쇄된 배점 규칙**과 채점기가 쓰는 배점을 맞대어 본다.

왜 이 자가 있나
---------------
성적표 맨 위에 「원점수 152/180」이 적힌다. 그 수를 만드는 규칙이 두 곳에 있다.

    종이   시험지 1쪽 주의사항 11번 — "각 문제의 배점은 3점으로, 오답은 …"
    코드   final.html 의 `finalPenalty(exam)` — 시험 **그룹 이름**으로 판정한다

코드 쪽이 그룹 이름으로 가르기 때문에, 새 회차를 들일 때 그룹만 정하면 배점이
따라온다. 편하지만 **종이를 안 본다.** 2026-08-29 에 처음 맞대어 보니 51회차
가운데 20곳이 어긋나 있었고, 어긋난 방향이 양쪽 다였다.

    JMChC 14 · 산과염기 1   종이는 오답 −1 인데 코드는 무감점  → 점수가 **높게** 나간다
    동형(donghyung) 4      종이는 오답 0 인데 코드는 −1        → 점수가 **낮게** 나간다

⚠ 이 자는 **무엇이 옳은지 정하지 않는다.** 종이가 늘 옳은 것도 아니다 —
  선생님이 진단 목적으로 일부러 감점을 뺀 회차가 있을 수 있다(JMChC 를 그렇게
  두신 것으로 보인다). 정하는 것은 사람이고, 여기서 하는 일은 **어긋난 자리를
  숨기지 않는 것**뿐이다. 선생님이 보고 정한 것은 `score_rule.json` 에 적어
  두면 다시 빨간불이 나지 않는다.

⚠ 또 하나. `index.html`(단원평가 아홉 회차)은 **감점 개념 자체가 없다** —
  `analyze()` 가 `정답수 × 3` 만 센다. 같은 회차를 final.html 에서 채점하면
  오답 −1 이 붙어 **두 화면이 다른 점수**를 말한다. 그 목록도 같이 낸다.

⚠ 시험지 읽기는 `--scan` 때만 한다(pdftotext 가 필요하다). 읽은 결과는
  `tools/score_rule_paper.json` 에 적어 저장소에 넣는다. 평소 검사는 그 파일만
  본다 — CI 의 이 걸음에는 poppler 가 안 깔려 있고, 무엇보다 **무엇을 읽었는지가
  사람이 들여다볼 수 있는 파일로 남아야** 한다. 시험지를 새로 들이면 --scan 을
  다시 돌린다.

    python3 tools/score_rule.py           # 종이와 코드가 어떻게 다른가
    python3 tools/score_rule.py --scan    # 시험지 PDF 를 다시 읽는다 (pdftotext 필요)
    python3 tools/score_rule.py --check   # 새로 어긋난 자리가 생기면 빨간불
    python3 tools/score_rule.py --seal    # 지금 어긋난 자리를 사람이 정한 것으로 적는다
"""
import io
import json
import os
import re
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SEAL = os.path.join(ROOT, 'tools', 'score_rule.json')
PAPER = os.path.join(ROOT, 'tools', 'score_rule_paper.json')

# final.html · final-submit.html 의 finalPenalty() 와 **같은 규칙**이어야 한다.
# 저기를 고치면 여기도 고친다 — 안 그러면 이 자가 거짓말을 한다.
NOPEN_GROUPS = {'JMChC', '산과염기', '파이널', '화학1', '화학2'}

RX_RULE = re.compile(r'배점은[^\n]{0,90}')
RX_WRONG_MINUS = re.compile(r'오답[^,\n]{0,6}[-−–]\s*1\s*점|틀린\s*경우\s*[-−–]\s*1\s*점')
RX_WRONG_ZERO = re.compile(r'오답[^,\n]{0,6}0\s*점|틀린\s*경우\s*0\s*점')


def exams():
    return json.load(io.open(os.path.join(ROOT, 'exams.json'), encoding='utf-8'))


def code_penalty(ex):
    return 0 if ex.get('group') in NOPEN_GROUPS else 1


def read_pdf(eid):
    """시험지 1쪽에 인쇄된 규칙을 **PDF 에서 직접** 읽는다. --scan 때만 쓴다."""
    pdf = os.path.join(ROOT, eid + '-problem.pdf')
    if not os.path.exists(pdf):
        return None, ''
    try:
        out = subprocess.run(['pdftotext', '-f', '1', '-l', '4', pdf, '-'],
                             capture_output=True, timeout=40).stdout.decode('utf-8', 'replace')
    except Exception:
        return None, ''
    txt = re.sub(r'[ \t]+', ' ', out)
    m = RX_RULE.search(txt)
    said = (m.group(0) if m else '').strip()
    if not said:
        return None, ''
    if RX_WRONG_MINUS.search(said):
        return 1, said
    if RX_WRONG_ZERO.search(said):
        return 0, said
    return None, said


def scan():
    """시험지를 전부 다시 읽어 tools/score_rule_paper.json 에 적는다."""
    out = {}
    for ex in sorted(exams(), key=lambda e: e['id']):
        pen, said = read_pdf(ex['id'])
        if pen is None:
            continue
        out[ex['id']] = {'penalty': pen, 'said': said[:160]}
    json.dump({'설명': 'tools/score_rule.py --scan 이 시험지 PDF 1쪽에서 읽은 배점 규칙. '
                       '손으로 고치지 않는다. penalty 0=무감점, 1=오답 −1.',
               '읽은 것': out},
              io.open(PAPER, 'w', encoding='utf-8'),
              ensure_ascii=False, indent=1, sort_keys=True)
    io.open(PAPER, 'a', encoding='utf-8').write('\n')
    return out


def paper_table():
    """검사에 쓰는 값 — 저장소에 적힌 것만 본다(pdftotext 를 안 부른다)."""
    if not os.path.exists(PAPER):
        return None
    return json.load(io.open(PAPER, encoding='utf-8')).get('읽은 것', {})


def main():
    check = '--check' in sys.argv
    seal = '--seal' in sys.argv
    xs = exams()

    if '--scan' in sys.argv:
        got = scan()
        print('시험지 %d개에서 배점 규칙을 읽어 tools/score_rule_paper.json 에 적었다.' % len(got))

    paper = paper_table()
    if paper is None:
        print('시험지에서 읽은 표가 없다 — python3 tools/score_rule.py --scan 으로 만든다.')
        return 1 if check else 0

    rows, unknown = [], []
    for ex in sorted(xs, key=lambda e: e['id']):
        rec = paper.get(ex['id'])
        cp = code_penalty(ex)
        if not rec:
            unknown.append(ex['id'])
            continue
        rows.append({'id': ex['id'], 'group': ex.get('group', '?'),
                     'code': cp, 'paper': rec['penalty'], 'said': rec.get('said', '')})

    bad = [r for r in rows if r['code'] != r['paper']]
    lbl = {0: '무감점', 1: '오답 −1'}

    print('시험 %d개 · 시험지에서 배점을 읽은 것 %d개 · 못 읽은 것 %d개'
          % (len(xs), len(rows), len(unknown)))
    if bad:
        print('\n종이와 코드가 어긋난 회차 %d개' % len(bad))
        print('  %-24s %-8s %-9s %-9s' % ('회차', '그룹', '코드', '시험지'))
        for r in sorted(bad, key=lambda x: (x['group'], x['id'])):
            print('  %-24s %-8s %-9s %-9s' % (r['id'], r['group'], lbl[r['code']], lbl[r['paper']]))
        hi = [r['id'] for r in bad if r['code'] == 0 and r['paper'] == 1]
        lo = [r['id'] for r in bad if r['code'] == 1 and r['paper'] == 0]
        if hi:
            print('\n  점수가 **높게** 나가는 회차 %d개 (종이는 감점인데 코드는 무감점)' % len(hi))
        if lo:
            print('  점수가 **낮게** 나가는 회차 %d개 (종이는 무감점인데 코드는 감점)' % len(lo))
    else:
        print('\n종이와 코드가 모두 맞는다.')

    # index.html 은 감점 개념이 없다 — 같은 회차가 두 화면에서 다른 점수를 낸다
    idx = io.open(os.path.join(ROOT, 'index.html'), encoding='utf-8').read()
    i = idx.index('const EXAMS=[')
    idx_ids = set(re.findall(r'\{id:"([^"]+)",title:"', idx[i:i + 60000]))
    two_face = sorted(e['id'] for e in xs if e['id'] in idx_ids and code_penalty(e) == 1)
    if two_face:
        print('\n한 회차가 화면마다 다른 점수를 내는 곳 %d개' % len(two_face))
        print('  index.html 은 정답×3 만 세고(감점 없음), final.html 은 오답 −1 을 뺀다.')
        for x in two_face:
            print('  ' + x)

    if unknown:
        print('\n시험지에서 배점을 못 읽은 회차 %d개 — 모른다는 뜻이지 없다는 뜻이 아니다.' % len(unknown))
        print('  ' + ', '.join(unknown[:12]) + (' …' if len(unknown) > 12 else ''))

    now = {r['id']: [lbl[r['code']], lbl[r['paper']]] for r in bad}
    if seal:
        json.dump({'설명': '선생님이 보고 «이대로 둔다»고 정한 자리. 여기 적힌 회차는 '
                           '빨간불을 안 켜고, 새로 어긋나는 것만 막는다. '
                           '값은 [코드가 쓰는 배점, 시험지에 인쇄된 배점].',
                   '사람이 정한 자리': now},
                  io.open(SEAL, 'w', encoding='utf-8'),
                  ensure_ascii=False, indent=1, sort_keys=True)
        io.open(SEAL, 'a', encoding='utf-8').write('\n')
        print('\n지금 어긋난 %d곳을 tools/score_rule.json 에 적었다.' % len(now))
        return 0

    known = {}
    if os.path.exists(SEAL):
        known = json.load(io.open(SEAL, encoding='utf-8')).get('사람이 정한 자리', {})
    fresh = sorted(k for k in now if k not in known)
    if fresh:
        print('\n**새로** 어긋난 회차 %d개 — 사람이 아직 안 본 자리다:' % len(fresh))
        for k in fresh:
            print('  %-24s 코드 %s · 시험지 %s' % (k, now[k][0], now[k][1]))
        print('\n어느 쪽이 맞는지는 시험지를 낸 사람이 정한다.')
        print('그대로 두기로 정했으면 python3 tools/score_rule.py --seal 로 적는다.')
        return 1 if check else 0

    if now:
        print('\n어긋난 %d곳은 모두 사람이 보고 정한 자리다(tools/score_rule.json).' % len(now))
    return 0


if __name__ == '__main__':
    try:
        sys.exit(main())
    except BrokenPipeError:
        os._exit(0)
