#!/usr/bin/env python3
"""`qmatrix-editor.html` 이 품고 있는 **유형 태그 표**를 exams.json 에서 다시 뽑는다.

Q-행렬 편집기는 시험의 `type` 태그를 125 개념에 이어 붙이는 자리다. 그런데
그 태그 목록이 화면 안에 통째로 박혀 있고, 다시 뽑아 주는 것이 없었다.

    화면에 박힌 것   시험 41개 · 문항 1860개 · 태그 599종
    지금 exams.json  시험 39개 · 문항 2310개 · 태그 744종

**태그 160종이 목록에 아예 없었다.** 선생님이 이을 수가 없고, 화면이 보여
주는 덮임 비율도 옛 분모(1860)로 셈한 값이었다.

여기서 하는 일.

  · `type` 을 세어 빈도순으로 다시 적는다
  · 태그마다 가장 많이 함께 쓰인 `area` 를 붙인다
  · **이미 이어 둔 개념 코드는 그대로 옮긴다.** 선생님이 검수한 값이다
  · 새 태그의 개념 코드는 **비워 둔다.** 지어내지 않는다 —
    화면에서 노란 칸으로 떠서 선생님이 잇는다

분모(문항 수·시험 수)도 같이 고친다. 두 자리에 손으로 적혀 있었다.

    python3 tools/gen_qmatrix_tags.py           # 어긋난 곳
    python3 tools/gen_qmatrix_tags.py --write   # 다시 적는다
    python3 tools/gen_qmatrix_tags.py --check   # 어긋나면 빨간불 (CI용)
"""
import collections
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PAGE = os.path.join(ROOT, 'qmatrix-editor.html')
ENTRY = re.compile(r"\{t:'((?:[^'\\]|\\.)*)',f:(\d+),a:'((?:[^'\\]|\\.)*)',c:'(\d*)'\}")


def esc(s):
    return s.replace('\\', '\\\\').replace("'", "\\'")


def build(src):
    """지금 exams.json 으로 만든 TAGS 배열 글자열과, 시험·문항 수."""
    exams = json.load(open(os.path.join(ROOT, 'exams.json'), encoding='utf-8'))
    freq = collections.Counter()
    area = collections.defaultdict(collections.Counter)
    for e in exams:
        for a, t in zip(e.get('area') or [], e.get('type') or []):
            freq[t] += 1
            area[t][a] += 1
    kept = {m.group(1): m.group(4) for m in ENTRY.finditer(src)}
    rows = []
    for t, f in sorted(freq.items(), key=lambda kv: (-kv[1], kv[0])):
        a = area[t].most_common(1)[0][0]
        rows.append("{t:'%s',f:%d,a:'%s',c:'%s'}" % (esc(t), f, esc(a), kept.get(t, '')))
    nq = sum(int(e['nQ']) for e in exams)
    return 'const TAGS=[' + ','.join(rows) + '];', len(exams), nq


def main():
    write = '--write' in sys.argv
    check = '--check' in sys.argv
    src = open(PAGE, encoding='utf-8').read()
    want, nex, nq = build(src)

    i = src.find('const TAGS=[')
    j = src.find('];', i)
    cur = src[i:j + 2]
    now = ENTRY.findall(cur)
    print('화면에 박힌 것   태그 %d종 · 문항 %d개' % (len(now), sum(int(f) for _, f, _, _ in now)))
    print('지금 exams.json  태그 %d종 · 문항 %d개 · 시험 %d개'
          % (want.count('{t:'), nq, nex))

    out = src[:i] + want + src[j + 2:]
    # 분모가 손으로 적혀 있는 두 자리
    out = re.sub(r'(final\.html )\d+(개 시험·)\d+(문항의)',
                 lambda m: '%s%d%s%d%s' % (m.group(1), nex, m.group(2), nq, m.group(3)), out)
    out = re.sub(r'(매핑 문항 \(/)\d+(\))',
                 lambda m: '%s%d%s' % (m.group(1), nq, m.group(2)), out)

    if out == src:
        print('\n유형 태그 표가 exams.json 과 맞는다.')
        return 0
    gone = [t for t, _, _, _ in now if ("{t:'%s'," % esc(t)) not in want]
    new = want.count("c:''}") - sum(1 for _, _, _, c in now if not c)
    print('\n다시 뽑아야 한다 — 새 태그 %d종, 사라진 태그 %d종'
          % (max(new, 0), len(gone)))
    if write:
        open(PAGE, 'w', encoding='utf-8').write(out)
        print('qmatrix-editor.html 에 다시 적었다 (이어 둔 개념 코드는 그대로 옮겼다)')
        return 0
    print('python3 tools/gen_qmatrix_tags.py --write 로 맞춘다.')
    return 1 if check else 0


if __name__ == '__main__':
    try:
        sys.exit(main())
    except BrokenPipeError:
        os._exit(0)
