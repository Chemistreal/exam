#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""집필해 둔 조각을 답지(answers/<id>.json)에 채워 넣는다.

두 갈래가 여기로 온다.

    answers/_wip/<id>-<범위>.json   지문·선지·해설·오개념까지 통째로 (j0 되살리기)
    answers/_mis/<id>__m<n>.json    선지별 오답 해설만 (이미 지문이 있는 회차)

■ 규칙 하나: **이미 채워져 있는 자리는 건드리지 않는다.**

손으로 공들여 쓴 해설을 기계가 덮어쓰면 아무도 모른다. 채우는 것만 한다.
정말 덮어야 하면 --overwrite 를 손으로 붙인다.

■ 규칙 둘: 선지별 오답 해설은 **정답 번호를 담으면 안 된다.**

성적표는 학생이 고른 번호로 이 표를 찾아 「고른 ③이 왜 틀렸나」를 띄운다.
정답 번호가 표에 섞여 있으면, 맞힌 학생에게 «네가 고른 게 왜 틀렸나» 를 보여 준다.
집필 에이전트에게 「정답은 넣지 마라」 라고 말해 두는 것으로는 부족하다 —
말은 지켜지지 않을 수 있고, 지켜지지 않았을 때 화면에서야 드러난다. 여기서 막는다.

    python3 tools/answer_fill.py            # 무엇이 채워질지만 보여 준다
    python3 tools/answer_fill.py --write    # 채운다 (조각 파일은 지우지 않는다)
    python3 tools/answer_fill.py --check    # 답지 안의 선지별 오답 해설이 성한지만 본다
"""
import glob
import io
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# 통째로 채우는 갈래에서 옮길 자리. explanationHtml 은 여기서 만들지 않는다 —
# tools/gen_expl_html.py 가 글에서 꼴을 만든다(그 자가 유일한 생성자여야 한다).
FIELDS = ('stem', 'choices', 'explanation', 'misconception', 'misconceptions')


def load(p):
    return json.load(io.open(p, encoding='utf-8'))


def accepted(q):
    """이 문항에서 맞는 것으로 인정하는 번호들."""
    acc = [n for n in (q.get('acceptableAnswers') or []) if n]
    if not acc and q.get('answer'):
        acc = [q['answer']]
    return set(int(n) for n in acc)


def mis_errors(q, n_choices=4):
    """선지별 오답 해설이 성한지 본다.

    두 가지를 갈라 돌려준다 — (망가진 것, 아직 안 채운 것).

    · 망가진 것: 정답 번호가 섞였거나, 설명이 비었거나, 선지 범위 밖이다.
      이건 학생 화면에서 **틀린 말을 하게 되는** 결함이다. 막아야 한다.
    · 안 채운 것: 오답 셋 중 하나만 적혀 있다. 학생이 마침 그 하나를 골랐으면
      줄이 서고, 다른 것을 골랐으면 안 선다. 덜 준 것이지 틀린 말은 아니다.
      (실제로 126문항 중 110문항이 이 꼴이다 — 해설지 tip 이 짚은 함정 하나만
       옮겨 적었던 자리다. 결함으로 세면 예전 자료 전부가 빨간불이 된다.)
    """
    mis = q.get('misconceptions')
    if not mis:
        return [], []
    acc = accepted(q)
    broken = []
    bad = sorted(k for k in mis if int(k) in acc)
    if bad:
        broken.append('정답 번호가 섞여 있다: %s' % ', '.join(bad))
    for k, v in mis.items():
        if not str(v or '').strip():
            broken.append('%s번 설명이 비어 있다' % k)
        if not (1 <= int(k) <= n_choices):
            broken.append('선지 범위 밖: %s' % k)
    thin = []
    if acc:
        missing = [str(n) for n in range(1, n_choices + 1)
                   if n not in acc and str(n) not in mis]
        if missing:
            thin.append('오답 %s번에 설명이 없다' % ', '.join(missing))
    return broken, thin


def main():
    write = '--write' in sys.argv
    check = '--check' in sys.argv
    over = '--overwrite' in sys.argv

    if check:
        bad = thin = seen = 0
        for p in sorted(glob.glob(os.path.join(ROOT, 'answers', '*.json'))):
            qs = load(p).get('questions') or {}
            for k in sorted(qs, key=lambda x: int(x)):
                if not qs[k].get('misconceptions'):
                    continue
                seen += 1
                broken, part = mis_errors(qs[k])
                if broken:
                    bad += 1
                    print('[%s %s번] %s' % (os.path.basename(p)[:-5], k, ' / '.join(broken)))
                if part:
                    thin += 1
        print('\n선지별 오답 해설 %d문항 · 망가진 곳 %d · 오답 일부만 채운 곳 %d'
              % (seen, bad, thin))
        return 1 if bad else 0

    # 조각을 시험별로 모은다
    parts = {}
    for p in sorted(glob.glob(os.path.join(ROOT, 'answers', '_wip', '*.json'))):
        eid = os.path.basename(p).rsplit('-', 2)[0]
        parts.setdefault(eid, {'full': [], 'mis': []})['full'].append(p)
    for p in sorted(glob.glob(os.path.join(ROOT, 'answers', '_mis', '*.json'))):
        eid = os.path.basename(p).split('__')[0]
        parts.setdefault(eid, {'full': [], 'mis': []})['mis'].append(p)

    if not parts:
        print('채울 조각이 없다 (answers/_wip · answers/_mis 가 비어 있다)')
        return 0

    rc = 0
    for eid in sorted(parts):
        dest = os.path.join(ROOT, 'answers', '%s.json' % eid)
        if not os.path.exists(dest):
            print('[%s] 답지가 없다 — 건너뛴다' % eid)
            rc = 1
            continue
        doc = load(dest)
        qs = doc.get('questions') or {}
        filled = skipped = refused = 0
        notes = []

        for p in parts[eid]['full']:
            for k, v in load(p).items():
                q = qs.get(k)
                if q is None:
                    notes.append('%s번이 답지에 없다 (%s)' % (k, os.path.basename(p)))
                    rc = 1
                    continue
                for f in FIELDS:
                    if f not in v or not v[f]:
                        continue
                    if q.get(f) and not over:
                        skipped += 1
                        continue
                    q[f] = v[f]
                    filled += 1

        for p in parts[eid]['mis']:
            for k, v in load(p).items():
                q = qs.get(k)
                if q is None:
                    notes.append('%s번이 답지에 없다 (%s)' % (k, os.path.basename(p)))
                    rc = 1
                    continue
                if q.get('misconceptions') and not over:
                    skipped += 1
                    continue
                # 정답 번호가 섞여 들어오면 **그 문항은 통째로 거른다.**
                # 한 칸만 빼고 넣으면 «오답 하나에 설명이 없는» 문항이 된다.
                probe = dict(q)
                probe['misconceptions'] = v
                broken, part = mis_errors(probe)
                # 새로 집필한 것은 «오답 셋 다» 가 약속이다. 옛 자료의 한 칸짜리는
                # 그대로 두지만, 지금 들어오는 것은 덜 채운 것도 되돌려 보낸다.
                if broken or part:
                    refused += 1
                    notes.append('%s번 거절 — %s' % (k, ' / '.join(broken + part)))
                    rc = 1
                    continue
                q['misconceptions'] = v
                filled += 1

        print('[%s] 채울 자리 %d · 이미 있어 건너뛴 자리 %d · 거절 %d'
              % (eid, filled, skipped, refused))
        for n in notes[:20]:
            print('    ' + n)
        if write and filled:
            io.open(dest, 'w', encoding='utf-8').write(
                json.dumps(doc, ensure_ascii=False, indent=1) + '\n')
            print('    → 썼다: answers/%s.json' % eid)

    if not write:
        print('\n(--write 를 붙이면 실제로 채운다)')
    return rc


if __name__ == '__main__':
    raise SystemExit(main())
