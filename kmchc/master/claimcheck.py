# -*- coding: utf-8 -*-
"""claimcheck — ★조치 커밋이 이름을 부른 문항이 실제로 바뀌었는가★

■ 왜 만들었나 (T13 P15 3차)
  2차 조치 커밋의 메시지는 defender F2 를 받아 M02118 ③ 을 갈았다고 적었는데,
  그 커밋의 파일에서 ③ 은 한 글자도 바뀌지 않았다. 기록만 남고 조치는 없었다.
  ★그 상태로 세 검증자가 동시 0건을 냈다★ — 검증자는 문항 내용을 보지, 내가
  적은 조치가 실제로 들어갔는지는 보지 않기 때문이다.

  층5 순회는 '지금 파일이 옳은가' 만 답한다. 이 검사는 그 옆의 물음을 맡는다 —
  ★'내가 했다고 적은 일을 정말 했는가'.★

■ 쓰는 법
    python3 master/claimcheck.py            # HEAD 커밋을 본다
    python3 master/claimcheck.py <rev>      # 그 커밋을 본다
    python3 master/claimcheck.py <a> <b>    # a..b 구간의 커밋을 하나씩 본다

■ 무엇을 내놓나
  ㉠ ★이름만 불리고 바뀌지 않은 문항★ — 기록과 파일이 어긋난 자리. 손으로 볼 것.
     다만 근거로 끌어온 문항(예: 'M02114 는 까닭을 밀침으로 명시한다')은 바뀌지
     않는 것이 정상이라 ★오탐이 섞인다★. 검사가 답을 주지 않고 자리를 짚어 준다.
  ㉡ ★고쳐졌는데 이름이 불리지 않은 문항★ — 기록이 빠뜨린 자리. 이쪽은 오탐이
     거의 없어 더 무겁다.
     ▸ ★새로 들인 문항(생산 커밋)은 여기서 세지 않는다★ — 열 문항을 새로 들이는
       커밋마다 열 곳이 뜨면 검사가 잡음이 되어 아무도 보지 않게 된다.
"""
import json
import re
import subprocess
import sys

BANK = 'kmchc/master/master_bank.json'
ID_RE = re.compile(r'M\d{5}')
RANGE_RE = re.compile(r'M\d{5}\s*[~\-–]\s*M\d{5}')


def sh(*args):
    r = subprocess.run(args, capture_output=True, text=True)
    if r.returncode:
        raise SystemExit(f'⛔ 실패: {" ".join(args)}\n{r.stderr.strip()}')
    return r.stdout


def bank_at(rev):
    """rev 시점의 은행을 {id: 문항} 으로. 그 시점에 파일이 없으면 빈 것으로 본다."""
    r = subprocess.run(['git', 'show', f'{rev}:{BANK}'], capture_output=True, text=True)
    if r.returncode:
        return {}
    return {x['id']: x for x in json.loads(r.stdout)}


def check(rev):
    subj = sh('git', 'log', '-1', '--format=%s', rev).strip()
    msg = sh('git', 'log', '-1', '--format=%B', rev)
    short = sh('git', 'rev-parse', '--short', rev).strip()

    # ★범위 표기는 개별 지목이 아니다★ — 제목의 'M02121~M02130' 을 두 문항으로 읽으면
    # 조치 커밋마다 잡음 둘이 붙는다. 범위를 먼저 걷어내고 남은 것만 지목으로 센다.
    named = set(ID_RE.findall(RANGE_RE.sub(' ', msg)))
    if not named:
        return 0

    before, after = bank_at(f'{rev}^'), bank_at(rev)
    # ★새로 들어온 문항과 고쳐진 문항을 가른다★ — 생산 커밋은 열 문항을 새로 들이는데
    # 그것을 '이름이 없다' 고 짚으면 잡음만 커진다. 기록과 맞대어야 하는 것은 ★고쳐진★ 쪽이다.
    added = set(after) - set(before)
    edited = {i for i in set(before) & set(after) if before[i] != after[i]}

    ghost = sorted(named - added - edited)   # 이름만 불리고 바뀌지 않음
    silent = sorted(edited - named)          # 고쳐졌는데 이름이 없음

    if not ghost and not silent:
        return 0

    print(f'\n── {short} {subj}')
    if ghost:
        print(f'  ★이름만 불리고 바뀌지 않음 {len(ghost)}★ — 근거로 끌어온 문항이면 정상')
        print('     ' + ' '.join(ghost))
    if silent:
        print(f'  ★고쳐졌는데 이름이 없음 {len(silent)}★')
        print('     ' + ' '.join(silent))
    return len(ghost) + len(silent)


def main():
    a = sys.argv[1:]
    if len(a) >= 2:
        revs = sh('git', 'rev-list', '--reverse', f'{a[0]}..{a[1]}').split()
    else:
        revs = [a[0] if a else 'HEAD']

    print(f'═══ claimcheck · 커밋 {len(revs)}개 ═══')
    n = sum(check(r) for r in revs)
    print(f'\n{"✅ 어긋난 자리 없음" if not n else f"🔴 짚을 자리 {n}곳 — 손으로 볼 것"}')


if __name__ == '__main__':
    main()
