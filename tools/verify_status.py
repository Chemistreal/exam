#!/usr/bin/env python3
"""해설을 **어디까지 사람이 봤는지** 세고, 뒤로 가지 않게 막는다.

왜 이 자가 있나
---------------
`answers/*.json` 의 문항마다 `verificationStatus` 가 붙어 있다. 네 단계다.

    verified_long_form            사람이 풀이를 끝까지 읽고 확인했다
    key_verified                  정답만 대조했다
    explained_from_problem_pdf    문제지 PDF 의 해설을 옮겨 적었다
    answer_key_and_concept_only   정답과 개념 한 줄만 있다

2026-08-11 에 처음 재어 보니 2,310문항 가운데 **1,620 · 240 · 223 · 127** 이었다.
그런데 이 숫자가 **아무 데도 안 적혀 있었고, 아무도 안 세고 있었다.**

세어 보니 덜 본 350문항이 흩어져 있지 않았다 — **여섯 회차 통째**다.

    donghyung-1   59 + 1     donghyung-2   60
    donghyung-3   53 + 7     donghyung-4   51 + 9
    kmchc-2024-2  60         kmchc-2025-1-simhwa  50

이게 중요하다. 흩어져 있으면 "언젠가 훑어야 할 일" 이지만, 회차 단위로 몰려
있으면 **한 회차씩 끝낼 수 있는 일**이다. 여섯 번이면 끝난다.

이 자가 막는 것
---------------
**뒤로 가는 것만** 막는다. 앞으로 가는 것(덜 본 것이 줄어드는 것)은 언제나
반긴다. `tools/verify_seal.json` 에 지금 값을 적어 두고, 덜 본 문항이 **늘면**
빨간불이다.

  · 새 회차를 들일 때 해설 없이 들어오면 그 자리에서 걸린다
  · 이미 본 문항의 상태가 조용히 내려가도 걸린다
  · 선생님이 한 회차를 끝내면 `--seal` 로 새 값을 적는다 (숫자가 준다)

⚠ 이 자는 **해설의 옳고 그름을 안 본다.** 화학 내용은 사람이 본다 —
  이 저장소의 규칙이다. 여기서 세는 것은 "사람이 봤다고 적혀 있는가" 뿐이다.
  적혀 있는 것과 실제로 본 것은 다르다. 그래서 이 자는 **재는 자**이지
  **검수하는 자**가 아니다.

    python3 tools/verify_status.py           # 지금 어디까지 봤나
    python3 tools/verify_status.py --check   # 덜 본 것이 늘면 빨간불
    python3 tools/verify_status.py --seal    # 지금 값을 새 기준으로 적는다
"""
import collections
import glob
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SEAL = os.path.join(ROOT, 'tools', 'verify_seal.json')

# 위에서 아래로 갈수록 덜 본 것이다.
TIERS = ['verified_long_form', 'key_verified',
         'explained_from_problem_pdf', 'answer_key_and_concept_only']
# 이 둘이 "아직 사람이 풀이를 안 읽은" 자리다.
THIN = {'explained_from_problem_pdf', 'answer_key_and_concept_only'}

LABEL = {
    'verified_long_form': '풀이까지 확인',
    'key_verified': '정답만 대조',
    'explained_from_problem_pdf': '문제지 해설을 옮김',
    'answer_key_and_concept_only': '정답·개념 한 줄',
}

RX = re.compile(r'"verificationStatus"\s*:\s*"(\w+)"')


def scan():
    """회차 → 단계별 문항 수."""
    out = {}
    for path in sorted(glob.glob(os.path.join(ROOT, 'answers', '*.json'))):
        name = os.path.basename(path)[:-5]
        c = collections.Counter(RX.findall(open(path, encoding='utf-8').read()))
        if c:
            out[name] = dict(c)
    return out


def thin_of(counts):
    return sum(v for k, v in counts.items() if k in THIN)


def main():
    check = '--check' in sys.argv
    seal = '--seal' in sys.argv
    cur = scan()

    total = collections.Counter()
    for c in cur.values():
        total.update(c)
    n = sum(total.values())

    print('문항 %d개 · 회차 %d개\n' % (n, len(cur)))
    for t in TIERS:
        v = total.get(t, 0)
        if v:
            print('  %-30s %5d  %4.1f%%   %s' % (t, v, v * 100.0 / n, LABEL[t]))

    thin = [(k, thin_of(v), sum(v.values())) for k, v in cur.items() if thin_of(v)]
    thin.sort(key=lambda x: -x[1])
    if thin:
        print('\n아직 풀이를 안 읽은 회차 %d개 · %d문항' % (len(thin), sum(x[1] for x in thin)))
        for k, t, tot in thin:
            print('  %4d/%-3d  %s' % (t, tot, k))
        print('\n흩어져 있지 않고 **회차 단위로 몰려 있다** — 한 회차씩 끝낼 수 있다.')

    if seal:
        json.dump({k: thin_of(v) for k, v in cur.items() if thin_of(v)},
                  open(SEAL, 'w', encoding='utf-8'), ensure_ascii=False,
                  indent=1, sort_keys=True)
        open(SEAL, 'a', encoding='utf-8').write('\n')
        print('\n지금 값을 tools/verify_seal.json 에 적었다.')
        return 0

    if not os.path.exists(SEAL):
        print('\n기준이 없다 — python3 tools/verify_status.py --seal 로 적어 둔다.')
        return 1 if check else 0

    was = json.load(open(SEAL, encoding='utf-8'))
    now = {k: thin_of(v) for k, v in cur.items() if thin_of(v)}
    worse = []
    for k, v in sorted(now.items()):
        if v > was.get(k, 0):
            worse.append((k, was.get(k, 0), v))
    better = [(k, was[k], now.get(k, 0)) for k in sorted(was) if now.get(k, 0) < was[k]]

    if better:
        print('\n줄었다 — 잘된 일이다:')
        for k, a, b in better:
            print('  %s  %d → %d' % (k, a, b))
        print('  python3 tools/verify_status.py --seal 로 새 기준을 적는다.')

    if worse:
        print('\n덜 본 문항이 **늘었다** %d곳:' % len(worse))
        for k, a, b in worse:
            print('  %-26s %d → %d' % (k, a, b))
        print('\n해설 없이 회차가 들어왔거나, 이미 본 문항의 상태가 내려갔다.')
        print('일부러 그런 것이면 --seal 로 새 기준을 적는다.')
        return 1 if check else 0

    if not better:
        print('\n덜 본 문항이 늘지 않았다.')
    return 0


if __name__ == '__main__':
    try:
        sys.exit(main())
    except BrokenPipeError:
        os._exit(0)
