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

들어오는 자리는 셋이다.

    answers/_wip/<id>-<범위>.json    지문·선지·해설·오개념 통째로 (해설 PDF 를 옮긴 것)
    answers/_crop/<id>__c<n>.json    지문·선지·선지별 오답 (원문 크롭을 읽은 것)
    answers/_mis/<id>__m<n>.json     선지별 오답 해설만 (이미 지문이 있는 회차)
    answers/_thick/<id>__<범위>.json  얇은 해설을 증보한 것 — **덮어쓰는 유일한 갈래**

■ `_thick` 은 왜 규칙 하나의 예외인가

다른 갈래는 빈 자리를 채운다. `_thick` 은 **이미 있는 해설을 갈아 끼우는 것이
목적**이다 — 대상이 「정답률 50% 미만인데 해설이 150자도 안 되는」 문항이라,
채울 빈 자리가 아니라 「사고과정 … → ④」 한 줄이 앉아 있다.

그래서 이 갈래만 --overwrite 없이도 덮는다. 대신 두 가지를 막는다.

  · **짧아지면 거절한다.** 새 해설이 지금 것보다 짧으면 증보가 아니라 후퇴다.
  · **정답 키는 아예 못 들어온다.** answer·acceptableAnswers 는 FIELDS 에
    없으므로 지나갈 길이 없고, 여기서 한 번 더 막는다 — 이 회차들은 채점이
    끝나 성적이 이미 나갔다.
"""
import glob
import io
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# 통째로 채우는 갈래에서 옮길 자리. explanationHtml 은 여기서 만들지 않는다 —
# tools/gen_expl_html.py 가 글에서 꼴을 만든다(그 자가 유일한 생성자여야 한다).
FIELDS = ('stem', 'choices', 'explanation', 'misconception', 'misconceptions')
# 증보 갈래가 옮겨도 되는 자리. 지문·선지는 여기 없다 — 증보는 **해설을 두껍게
# 하는 일**이지 문제를 고치는 일이 아니다.
THICK_FIELDS = ('explanation', 'misconception', 'misconceptions', 'reviewNote')
# 어떤 갈래로도 답지의 정답 키를 건드리지 않는다.
NEVER = ('answer', 'acceptableAnswers')

# ── 들어올 때 한 번 다듬는다 ────────────────────────────────────────
# 시험지는 온도를 ℃(U+2103)로 인쇄한다. 크롭을 읽어 옮기면 그 글자가 그대로
# 따라 들어오는데, 저장소는 °C 로 모으기로 되어 있다(tools/dh_lint.py 가 잰다).
# 나갈 때 한꺼번에 훑는 것보다 **들어오는 문에서** 바꾸는 편이 낫다 —
# 한 번 들어오면 답지·해설 글·해설지 화면 셋으로 퍼지고, 그 뒤에는 어느 것이
# 원본인지 헷갈린다. (2026-09-05: 크롭에서 아홉 회차로 한꺼번에 새어 들어왔다.)
TIDY = {'\u2103': '°C', '\u2109': '°F'}


def tidy(v):
    """문자열이면 다듬고, 목록·표면 속까지 따라 들어간다."""
    if isinstance(v, str):
        for a, b in TIDY.items():
            v = v.replace(a, b)
        return v
    if isinstance(v, list):
        return [tidy(x) for x in v]
    if isinstance(v, dict):
        return {k: tidy(x) for k, x in v.items()}
    return v

# 성적표는 학부모와 학생이 함께 읽는다. 답지의 문장은 전부 「~다.」로 끝나는
# 평서체다(실측 186문항 전부). 집필 에이전트에게 「학생에게 말하듯」이라고
# 일렀더니 반말(「~어긋나.」 「~보여.」)로 써 온 회차가 있었다 — 한 회차만
# 어투가 다르면 그 회차만 다른 사람이 쓴 것처럼 읽힌다. 자료 쪽에서 막는다.
_TONE_BAD = re.compile(
    r'(?:[가-힣])(?:야|여|어|지|네|나|구나|까|래|자|요|잖아|거든|에요|예요)\s*[.!?]?\s*$')
_TONE_OK_TAIL = re.compile(r'(?:다|음|함|됨|임)\s*[.!?]?\s*$|[가-힣]\s*$')


def tone_bad(text):
    """마지막 문장이 평서체가 아니면 그 문장을 돌려준다."""
    t = str(text or '').strip()
    if not t:
        return None
    last = re.split(r'(?<=[.!?])\s+', t)[-1].strip()
    if not last:
        return None
    if _TONE_BAD.search(last) and not re.search(r'(?:하다|이다|한다|된다|없다|있다)\s*[.!?]?$', last):
        return last
    return None


def load(p):
    return json.load(io.open(p, encoding='utf-8'))


def accepted(q):
    """이 문항에서 맞는 것으로 인정하는 번호들."""
    acc = [n for n in (q.get('acceptableAnswers') or []) if n]
    if not acc and q.get('answer'):
        acc = [q['answer']]
    return set(int(n) for n in acc)


def mis_errors(q, n_choices=None):
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
    # 보기가 넷이라고 단정하지 않는다. 두 개짜리 문항이 실제로 있다
    # (kch1to2·kch1to2-b 45번 — 시험지 자체가 ①②만 인쇄돼 있다).
    # 넷으로 세면 없는 ③④에 설명이 없다고 되돌려 보내, 있는 설명까지 못 들어온다.
    if n_choices is None:
        n_choices = len(q.get('choices') or []) or 4
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
    for k, v in sorted(mis.items()):
        bad_line = tone_bad(v)
        if bad_line:
            broken.append('%s번 설명이 평서체가 아니다: 「…%s」' % (k, bad_line[-24:]))
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
    # 크롭에서 옮겨 적은 것(지문·선지·선지별 오답 해설)도 같은 문으로 들어온다.
    # 통째로 채우는 갈래에 넣는다 — stem·choices 가 함께 오기 때문이다.
    for p in sorted(glob.glob(os.path.join(ROOT, 'answers', '_crop', '*.json'))):
        eid = os.path.basename(p).split('__')[0]
        parts.setdefault(eid, {'full': [], 'mis': []})['full'].append(p)
    for p in sorted(glob.glob(os.path.join(ROOT, 'answers', '_mis', '*.json'))):
        eid = os.path.basename(p).split('__')[0]
        parts.setdefault(eid, {'full': [], 'mis': []})['mis'].append(p)
    for p in sorted(glob.glob(os.path.join(ROOT, 'answers', '_thick', '*.json'))):
        eid = os.path.basename(p).split('__')[0]
        parts.setdefault(eid, {'full': [], 'mis': [], 'thick': []}).setdefault('thick', []).append(p)

    if not parts:
        print('채울 조각이 없다 (answers/_wip · _crop · _mis · _thick 가 비어 있다)')
        return 0

    # ── --only 로 회차를 골라 넣는다 ────────────────────────────────
    # 왜 필요한가. 조각은 여러 회차가 **동시에** 쌓인다(집필이 병렬로 돈다).
    # 그런데 어떤 회차는 반박·수리가 끝났고 어떤 회차는 아직 초고다.
    # 이 문이 늘 «있는 것 전부» 를 넣으면, 검수를 안 지난 글이 검수를 지난
    # 글에 묻어 들어간다.
    # 한때 그것을 피하려고 **파일을 잠깐 딴 데로 옮겼다가** 돌려놓았는데,
    # 그 사이 수리하던 에이전트가 자기 파일을 못 찾았다(2026-09-05).
    # 파일을 움직이지 말고 **넣을 것을 고르는** 것이 맞다.
    only = None
    if '--only' in sys.argv:
        only = {x.strip() for x in sys.argv[sys.argv.index('--only') + 1].split(',')
                if x.strip()}
        skipped_eids = sorted(set(parts) - only)
        if skipped_eids:
            print('--only 로 %d회차만 넣는다. 미룬 회차: %s\n'
                  % (len(only & set(parts)), ', '.join(skipped_eids)))

    rc = 0
    for eid in sorted(parts):
        if only is not None and eid not in only:
            continue
        dest = os.path.join(ROOT, 'answers', '%s.json' % eid)
        if not os.path.exists(dest):
            print('[%s] 답지가 없다 — 건너뛴다' % eid)
            rc = 1
            continue
        doc = load(dest)
        qs = doc.get('questions') or {}
        filled = skipped = refused = thickened = 0
        notes = []

        # ── 증보 갈래: 있는 해설을 갈아 끼운다 ──────────────────────────
        for p in parts[eid].get('thick') or []:
            for k, v in load(p).items():
                q = qs.get(k)
                if q is None:
                    notes.append('%s번이 답지에 없다 (%s)' % (k, os.path.basename(p)))
                    rc = 1
                    continue
                for f in NEVER:
                    if f in v:
                        notes.append('%s번 증보가 정답 키(%s)를 담고 있다 — 통째로 거절' % (k, f))
                        rc = 1
                        v = None
                        break
                if v is None:
                    refused += 1
                    continue
                new = str(v.get('explanation') or '').strip()
                old = str(q.get('explanation') or '').strip()
                if new and len(new) < len(old):
                    notes.append('%s번 증보가 오히려 짧다(%d→%d자) — 거절'
                                 % (k, len(old), len(new)))
                    refused += 1
                    rc = 1
                    continue
                if v.get('misconceptions'):
                    probe = dict(q)
                    probe['misconceptions'] = v['misconceptions']
                    broken, _part = mis_errors(probe)
                    if broken:
                        notes.append('%s번 선지별 오답 거절 — %s' % (k, ' / '.join(broken)))
                        refused += 1
                        rc = 1
                        v = dict(v)
                        v.pop('misconceptions')
                for f in THICK_FIELDS:
                    if f not in v or not v[f]:
                        continue
                    bad_line = tone_bad(v[f]) if isinstance(v[f], str) else None
                    if bad_line:
                        notes.append('%s번 %s 가 평서체가 아니다: 「…%s」'
                                     % (k, f, bad_line[-24:]))
                        rc = 1
                        continue
                    if write:
                        q[f] = tidy(v[f])
                    thickened += 1

        for p in parts[eid]['full']:
            for k, v in load(p).items():
                q = qs.get(k)
                if q is None:
                    notes.append('%s번이 답지에 없다 (%s)' % (k, os.path.basename(p)))
                    rc = 1
                    continue
                # 선지별 오답 해설은 통째 갈래로 들어와도 같은 문을 지나야 한다.
                # 정답 번호가 섞인 표가 답지에 앉으면 성적표가 맞힌 학생에게
                # 「네가 고른 게 왜 틀렸나」를 보여 준다.
                if v.get('misconceptions'):
                    probe = dict(q)
                    probe['misconceptions'] = v['misconceptions']
                    broken, part = mis_errors(probe)
                    if broken or part:
                        refused += 1
                        notes.append('%s번 선지별 오답 거절 — %s'
                                     % (k, ' / '.join(broken + part)))
                        rc = 1
                        v = dict(v)
                        v.pop('misconceptions')
                for f in FIELDS:
                    if f not in v or not v[f]:
                        continue
                    if q.get(f) and not over:
                        skipped += 1
                        continue
                    q[f] = tidy(v[f])
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

        print('[%s] 채울 자리 %d · 갈아 끼운 자리 %d · 이미 있어 건너뛴 자리 %d · 거절 %d'
              % (eid, filled, thickened, skipped, refused))
        for n in notes[:20]:
            print('    ' + n)
        if write and (filled or thickened):
            io.open(dest, 'w', encoding='utf-8').write(
                json.dumps(doc, ensure_ascii=False, indent=1) + '\n')
            print('    → 썼다: answers/%s.json' % eid)

    if not write:
        print('\n(--write 를 붙이면 실제로 채운다)')
    return rc


if __name__ == '__main__':
    raise SystemExit(main())
