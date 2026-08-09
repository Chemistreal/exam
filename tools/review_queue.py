#!/usr/bin/env python3
"""사람이 검수할 것을 **급한 순서로** 줄 세운다.

"전부 검수" 는 아무도 안 한다. 문항이 2,310개다. 하루 스무 개씩이면 넉 달인데,
그 넉 달이 시작되지 않는 까닭은 **어디부터 볼지가 없어서**다.

내용의 옳고 그름은 기계가 판정하지 않는다(`docs/내용-400턴.md` 넷째 원칙).
여기서는 **줄만 세운다.** 무엇을 근거로 세우는지는 아래 그대로다.

  ① 공식 정답률이 낮다        열에 아홉이 틀린 문항은 설명이 얇으면 크게 새고,
                             실제로 그런 문항의 해설 중앙이 143자였다(0회차)
  ② 해설이 그 난이도에 비해 짧다   ①과 곱해서 본다
  ③ 오개념 한 줄이 얇거나 없다     오답 카드에서 학생이 실제로 읽는 줄이다
  ④ 같은 개념이 여러 회차에 나온다  한 번 고치면 여러 자리가 함께 낫는다

⚠ 이 점수는 **틀렸다는 뜻이 아니다.** "먼저 눈으로 볼 값어치가 크다" 는
  뜻뿐이다. 짧아서 좋은 해설이 실제로 있다 —
  "체심입방은 68%, 나머지 셋은 74% 다"(45자)면 그걸로 끝이다.

본 것은 다시 안 나오게 한다. `--done <시험id> <번호>` 로 표시하면 큐에서
빠지고, `tools/review_queue.json` 에 남는다. 지우는 것이 아니라 **봤다는
표시**라, 다음 사람이 같은 자리를 또 파지 않는다.

    python3 tools/review_queue.py                # 오늘 볼 스무 개
    python3 tools/review_queue.py --n 40         # 마흔 개
    python3 tools/review_queue.py --stats        # 얼마나 남았나 · 며칠 걸리나
    python3 tools/review_queue.py --write        # docs/검수대장.md 로 낸다
    python3 tools/review_queue.py --done hwol-2024 12
"""
import argparse
import collections
import glob
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SEEN = os.path.join(ROOT, 'tools', 'review_queue.json')
PER_DAY = 20


def load_exams():
    ex = json.load(open(os.path.join(ROOT, 'exams.json'), encoding='utf-8'))
    exs = ex if isinstance(ex, list) else (ex.get('exams') or list(ex.values()))
    return {e['id']: e for e in exs if isinstance(e, dict) and e.get('id')}


def load_items(eid):
    p = os.path.join(ROOT, 'answers', eid + '.json')
    if not os.path.exists(p):
        return []
    d = json.load(open(p, encoding='utf-8'))
    items = d if isinstance(d, list) else (d.get('items') or d.get('questions') or [])
    if isinstance(items, dict):
        items = list(items.values())
    return [it for it in items if isinstance(it, dict)]


def rate_of(exam, i):
    r = exam.get('rate')
    if not r:
        return None
    v = r.get(str(i)) if isinstance(r, dict) else (r[i - 1] if i - 1 < len(r) else None)
    try:
        return float(v)
    except (TypeError, ValueError):
        return None


def build():
    exams = load_exams()
    # ④ 같은 개념이 몇 회차에 걸쳐 나오는가
    spread = collections.defaultdict(set)
    rows = []
    for eid in sorted(exams):
        for i, it in enumerate(load_items(eid), 1):
            c = (it.get('concept') or '').strip()
            if c:
                spread[c].add(eid)
            rows.append((eid, i, it))

    out = []
    for eid, i, it in rows:
        e = exams[eid]
        expl = it.get('explanation') or ''
        om = it.get('misconception') or ''
        rate = rate_of(e, i)
        c = (it.get('concept') or '').strip()

        score = 0.0
        why = []
        if rate is not None:
            if rate < 30:
                score += 3.0
                why.append('정답률 %.0f%%' % rate)
            elif rate < 50:
                score += 1.5
                why.append('정답률 %.0f%%' % rate)
            # 어려운데 해설이 짧으면 곱해서 본다
            if rate < 50 and len(expl) < 160:
                score += 1.5
                why.append('어려운데 해설 %d자' % len(expl))
        if not om:
            score += 2.0
            why.append('오개념 한 줄 없음')
        elif len(om) < 30:
            score += 1.0
            why.append('오개념 한 줄 %d자' % len(om))
        # ⚠ 개념이 여러 회차에 걸쳐 있다는 것만으로는 검수할 까닭이 안 된다.
        #   처음엔 이것도 점수를 줬더니 1,448개 가운데 1,159개가 **그 이유 하나로**
        #   줄에 섰다. 그러면 줄을 세운 것이 아니라 전부를 다시 늘어놓은 것이다.
        #   확산은 **다른 이유가 이미 있을 때 우선순위를 올리는 것**으로만 쓴다.
        n = len(spread.get(c, ()))
        if n >= 4 and score > 0:
            score += 1.0
            why.append('%d회차에 걸친 개념' % n)
        if it.get('verificationStatus') in (None, '', 'unverified'):
            score += 1.0
            why.append('검수 표시 없음')
        if score > 0:
            out.append({'exam': eid, 'q': i, 'concept': c, 'score': round(score, 1),
                        'why': ' · '.join(why), 'expl': len(expl), 'om': len(om)})
    out.sort(key=lambda r: (-r['score'], r['exam'], r['q']))
    return out


def seen_load():
    if os.path.exists(SEEN):
        try:
            return json.load(open(SEEN, encoding='utf-8'))
        except ValueError:
            pass
    return {'설명': '사람이 눈으로 본 자리. 지운 것이 아니라 **봤다는 표시**다.',
            '본 것': []}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--n', type=int, default=PER_DAY)
    ap.add_argument('--stats', action='store_true')
    ap.add_argument('--write', action='store_true')
    ap.add_argument('--done', nargs=2, metavar=('시험id', '번호'))
    a = ap.parse_args()

    seen = seen_load()
    if a.done:
        key = '%s#%s' % (a.done[0], a.done[1])
        if key not in seen['본 것']:
            seen['본 것'].append(key)
            json.dump(seen, open(SEEN, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
        print('봤다고 적었다 · %s (모두 %d개)' % (key, len(seen['본 것'])))
        return 0

    q = [r for r in build() if '%s#%d' % (r['exam'], r['q']) not in set(seen['본 것'])]

    if a.stats:
        print('줄 세운 문항 %d개 · 본 것 %d개' % (len(q), len(seen['본 것'])))
        print('하루 %d개면 %d일' % (PER_DAY, (len(q) + PER_DAY - 1) // PER_DAY))
        band = collections.Counter('%.0f점대' % r['score'] for r in q)
        for k in sorted(band, reverse=True):
            print('  %-8s %5d개' % (k, band[k]))
        why = collections.Counter()
        for r in q:
            for w in r['why'].split(' · '):
                why[re.sub(r'\d+', 'N', w)] += 1
        print('\n왜 올라왔나')
        for k, v in why.most_common(8):
            print('  %-24s %5d' % (k, v))
        return 0

    if a.write:
        lines = ['# 검수 대장 — 사람이 먼저 볼 순서', '',
                 '`python3 tools/review_queue.py --write` 가 만든다. 손으로 고치지 않는다.', '',
                 '점수는 **틀렸다는 뜻이 아니다.** "먼저 눈으로 볼 값어치가 크다" 는 뜻이다.',
                 '본 자리는 `--done <시험id> <번호>` 로 표시하면 여기서 빠진다.', '',
                 '| | |', '|---|---|',
                 '| 줄 세운 문항 | %d개 |' % len(q),
                 '| 이미 본 것 | %d개 |' % len(seen['본 것']),
                 '| 하루 %d개면 | %d일 |' % (PER_DAY, (len(q) + PER_DAY - 1) // PER_DAY), '',
                 '## 앞 200개', '', '| 점수 | 회차 | 번호 | 개념 | 왜 |', '|---|---|---|---|---|']
        for r in q[:200]:
            lines.append('| %.1f | `%s` | %d | %s | %s |'
                         % (r['score'], r['exam'], r['q'], r['concept'] or '—', r['why']))
        lines.append('')
        p = os.path.join(ROOT, 'docs', '검수대장.md')
        open(p, 'w', encoding='utf-8').write('\n'.join(lines))
        print('적었다 · %s (%d개 중 앞 200개)' % (os.path.relpath(p, ROOT), len(q)))
        return 0

    print('오늘 볼 %d개 (남은 %d개)\n' % (min(a.n, len(q)), len(q)))
    print('%-5s %-22s %-4s %-16s %s' % ('점수', '회차', '번호', '개념', '왜'))
    for r in q[:a.n]:
        print('%-5.1f %-22s %-4d %-16s %s' % (r['score'], r['exam'], r['q'],
                                              (r['concept'] or '—')[:16], r['why']))
    return 0


if __name__ == '__main__':
    try:
        sys.exit(main())
    except BrokenPipeError:
        os._exit(0)
