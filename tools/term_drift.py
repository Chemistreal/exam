#!/usr/bin/env python3
"""**본문**이 같은 말을 두 가지로 적고 있지 않은지 잰다.

`tools/type_norm.py` 는 유형 이름 744종을 본다 — 그건 **데이터**다.
여기서는 학생이 읽는 **글**을 본다. 둘은 고치는 방법이 다르다:
데이터는 한 벌로 맞추면 끝이고, 글은 선생님이 어느 쪽으로 갈지 정해야 한다.

처음 재었을 때(2026-08-09) 일곱 쌍이 **두 저장소 모두에서** 갈려 있었다.

    반응 속도 600 : 반응속도 694   (exam)   ·  174 : 173  (DT)
    이온화 에너지 290 : 이온화에너지 592
    몰 농도 19 : 몰농도 452

⚠ 이건 **오타가 아니다.** 국립국어원 원칙으로는 띄어 쓰고, 전문 용어는
  붙여 쓰는 것도 허용한다. 어느 쪽이 맞느냐가 아니라 **한 벌이냐**가 문제다.

**선생님 결정(2026-08-09): 지금대로 둔다.** 둘 다 맞는 표기이고, 2,000곳을
건드려 얻을 것보다 건드리다 깨질 것이 크다. 그래서 이 자는 **조용하다.**
그래도 지우지 않는 까닭은 하나다 — 나중에 마음이 바뀌면 `term_drift.json` 의
"고른 표기" 에 한 줄만 적으면 그때부터 반대쪽을 막는다. **세는 일은 계속한다.**

세는 규칙
---------
  · 화면에 박힌 글과 코드가 만들어 넣는 글을 **둘 다** 센다. 한쪽만 고치면
    화면에서는 한 벌인데 눌러 보면 갈라진다.
  · `<style>` 안은 안 센다(글이 아니다).
  · 한쪽이 아주 드물면(5% 미만) '거의 한 벌' 로 따로 표시한다 — 그런 자리는
    실수 몇 건이지 결정이 필요한 자리가 아니다.

    python3 tools/term_drift.py                 # 지금 상태
    python3 tools/term_drift.py --repo PATH     # 다른 저장소
    python3 tools/term_drift.py --write         # 지금 상태를 기록에 담는다
    python3 tools/term_drift.py --check         # 정해 둔 표기를 어기면 빨간불
"""
import argparse
import glob
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
NOTE = os.path.join(ROOT, 'tools', 'term_drift.json')

# ── 보는 짝 ────────────────────────────────────────────────────────
# 화학 용어 가운데 띄어쓰기가 갈리기 쉬운 것들. 늘릴 때는 **실제로 두 꼴이
# 다 쓰이는지** 먼저 세어 보고 넣는다 — 안 그러면 목록만 길어진다.
PAIRS = [
    ('원자 모형', '원자모형'),
    ('이온화 에너지', '이온화에너지'),
    ('전자 배치', '전자배치'),
    ('결합 에너지', '결합에너지'),
    ('반응 속도', '반응속도'),
    ('화학 평형', '화학평형'),
    ('몰 농도', '몰농도'),
    ('산화 환원', '산화환원'),
    ('산 염기', '산염기'),
    ('활성화 에너지', '활성화에너지'),
    ('끓는 점', '끓는점'),
    ('어는 점', '어는점'),
    ('반 감기', '반감기'),
    ('중화 반응', '중화반응'),
    ('전기 음성도', '전기음성도'),
]

# 한쪽이 이보다 드물면 '결정할 자리' 가 아니라 '실수 몇 건' 이다.
RARE = 0.05


def text_of(src):
    """글만 남긴다 — 스타일은 글이 아니다."""
    s = re.sub(r'<style[\s\S]*?</style>', '', src)
    return s


def measure(root):
    got = {}
    for a, b in PAIRS:
        got[(a, b)] = [0, 0]
    for p in sorted(glob.glob(os.path.join(root, '*.html'))):
        try:
            s = text_of(open(p, encoding='utf-8', errors='ignore').read())
        except OSError:
            continue
        for a, b in PAIRS:
            # 붙여 쓴 꼴은 띄어 쓴 꼴의 부분 문자열이 아니라 따로 세면 되지만,
            # 반대로 '반응속도' 는 '반응 속도' 안에 없다. 그냥 세면 맞다.
            got[(a, b)][0] += s.count(a)
            got[(a, b)][1] += s.count(b)
    return got


def verdict(x, y):
    if not x and not y:
        return '안 쓴다'
    if not x or not y:
        return '한 벌'
    lo = min(x, y) / (x + y)
    return '거의 한 벌' if lo < RARE else '갈렸다'


def report(got, name):
    print('%s' % name)
    print('%-16s %8s   %-16s %8s   %s' % ('띄어 쓴 것', '횟수', '붙여 쓴 것', '횟수', '판정'))
    split = 0
    for (a, b), (x, y) in got.items():
        v = verdict(x, y)
        if v == '갈렸다':
            split += 1
        if v != '안 쓴다':
            print('%-16s %8d   %-16s %8d   %s' % (a, x, b, y, v))
    print('\n갈린 짝 %d개 / 본 짝 %d개' % (split, len(PAIRS)))
    return split


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--repo', default=ROOT)
    ap.add_argument('--write', action='store_true')
    ap.add_argument('--check', action='store_true')
    a = ap.parse_args()

    got = measure(a.repo)
    split = report(got, os.path.basename(os.path.abspath(a.repo)))

    if a.write:
        json.dump({'설명': '지금 어떻게 적고 있는지. **정해진 표기가 아니다** — '
                           '선생님이 정하면 그때 여기에 고른 쪽을 적고, '
                           '`--check` 가 반대쪽을 막는다.',
                   '고른 표기': {},
                   '지금 세어 본 것': {'%s / %s' % (k[0], k[1]): v for k, v in got.items()}},
                  open(NOTE, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
        print('기록했다 · tools/term_drift.json')
        return 0

    if a.check:
        if not os.path.exists(NOTE):
            print('\n기록이 없다 — `--write` 로 먼저 담는다.')
            return 1
        note = json.load(open(NOTE, encoding='utf-8'))
        chosen = note.get('고른 표기') or {}
        if not chosen:
            # 선생님이 **지금대로 두기로 정했다**(2026-08-09). 정하지 않은 것이
            # 아니라 "통일하지 않기로" 정한 것이라, 여기서 조용한 것이 맞다.
            when = note.get('선생님이 정한 날') or ''
            print('\nPASS (%s · 갈린 짝 %d개는 그대로 둔다)'
                  % (when or '아직 고른 표기 없음', split))
            return 0
        bad = []
        for key, want in chosen.items():
            a_, b_ = [t.strip() for t in key.split('/')]
            x, y = got[(a_, b_)]
            other = y if want == a_ else x
            if other:
                bad.append('%s 로 정했는데 반대쪽이 %d번 남아 있다' % (want, other))
        if bad:
            print('\nFAIL')
            for t in bad:
                print('  ' + t)
            return 1
        print('\nPASS')
    return 0


if __name__ == '__main__':
    try:
        sys.exit(main())
    except BrokenPipeError:
        os._exit(0)
