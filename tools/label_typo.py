#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""개념·영역·유형 이름의 오타 후보를 뽑는다 (사람이 판단한다).

왜 어절 전체로 안 재나
----------------------
처음에는 자료의 모든 어절을 훑어 "한 번만 나온 어절이 여러 번 나온 어절과
한 글자만 다르면 오타" 로 잡으려 했다. 한국어는 조사·어미가 붙는 말이라
후보가 **2,014개** 나왔고 거의 전부 거짓이었다(가능하며 ← 가능하다,
가지도 ← 가지 …). 잘못 재는 자는 안 재느니만 못하다.

개념·영역·유형 이름은 **활용하지 않는 명사구**다. 거기만 보면 617종 가운데
후보가 14개로 줄고, 사람이 한눈에 판단할 수 있다.

실제로 이렇게 잡았다: `워자수`·`워자량`·`워자의구성입자` — 원자의 오타가
네 파일 열두 곳에 있었고, 성적표의 개념 목록에 그대로 찍히고 있었다.
개념 이름이 갈리면 "되풀이해서 막히는 개념" 집계에서도 따로 세어진다.

⚠ 자동으로 고치지 않는다. 후보의 대부분은 **둘 다 맞는 말**이다
(중합반응/중화반응 · 원자오비탈/분자오비탈 · 녹는점/끓는점).

선생님이 남은 열한 개를 실제 문항과 대조해 **전부 오타가 아니라고** 판정했다
(2026-08). 그러니 이 목록이 비지 않는 것이 정상이다 — 새로 뜬 이름만 보면 된다.

    실행:  python3 tools/label_typo.py
"""
import collections
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RARE_MAX = 6      # 이만큼 이하로 나온 이름만 후보
TIMES = 10        # 짝이 이만큼 이상 흔해야 후보


def labels():
    out = collections.Counter()
    with open(os.path.join(ROOT, 'exams.json'), encoding='utf-8') as fp:
        for exam in json.load(fp):
            for key in ('area', 'type'):
                for v in (exam.get(key) or []):
                    if isinstance(v, str) and v.strip():
                        out[v.strip()] += 1
    return out


CODE = re.compile(r'^[A-Za-z]{1,4}[-_ ]?\d')   # CH1-048 · GC 12 같은 코드


def one_off(a, b):
    """길이가 같고 딱 한 글자만 다르다."""
    return len(a) == len(b) and sum(1 for x, y in zip(a, b) if x != y) == 1


def is_name(t):
    """이름만 본다. 코드는 한 글자 차이가 당연해서 후보가 폭발한다 —
    DT 개념 코드로 재어 보니 202개가 나왔고 전부 거짓이었다."""
    return bool(t) and not CODE.match(t)


def main():
    lab = labels()
    names = list(lab)
    hits = []
    for a in names:
        if lab[a] > RARE_MAX or not is_name(a):
            continue
        for b in names:
            if a is not b and one_off(a, b) and lab[b] >= lab[a] * TIMES:
                hits.append((a, lab[a], b, lab[b]))
                break
    print('이름 %d종 · 오타 후보 %d개 (사람이 판단한다)' % (len(names), len(hits)))
    for a, na, b, nb in sorted(hits, key=lambda x: -x[3]):
        print('  %-16s %3d회   ←?   %-16s %4d회' % (a, na, b, nb))
    return 0


if __name__ == '__main__':
    sys.exit(main())
