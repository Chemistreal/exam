#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""syncguard — ★로컬이 되돌아갔는지 먼저 재고, 되돌아갔으면 원격에 맞춘다★

■ 왜 세우는가
  이 세션에서 컨테이너가 ★하루에 네 번★ 4일 전 스냅샷으로 되돌아갔다. 되돌아가면
  `master_bank.json` 이 옛 상태가 되고 `build_t15_*.py` 가 사라지는데, ★로컬만 보면
  아무 이상이 없어 보인다★ — git status 도 깨끗하고 커밋 로그도 일관된다.
  그래서 되돌아간 줄 모르고 작업을 이어가면 ★없는 파일을 고치려 들거나, 이미 지나간
  은행 위에 배치를 다시 병합하게 된다.★

  ▸ ★로컬 상태가 일관되다는 것과 그것이 최신이라는 것은 다른 말이다.★
    원격이 앞서 있으면 그것은 되돌림이다 — 이 저장소에서는 원격만 앞설 수 있다
    (커밋할 때마다 바로 푸시하므로 로컬이 앞서는 것은 방금 커밋한 순간뿐이다).

■ 쓰는 법 — ★작업을 시작할 때 한 번, 되돌림이 의심되면 언제든★
      python3 syncguard.py          # 재기만 한다
      python3 syncguard.py --fix    # 되돌아갔으면 원격에 맞춘다
"""
import os
import subprocess
import sys

BRANCH = 'claude/handoff-file-usage-bsdh9w'
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ROOT = os.path.dirname(ROOT)          # kmchc/master → kmchc → 저장소 뿌리


def git(*a, check=True):
    r = subprocess.run(('git',) + a, cwd=ROOT, capture_output=True, text=True)
    if check and r.returncode:
        sys.exit('git %s 실패: %s' % (' '.join(a), r.stderr.strip()))
    return r.stdout.strip()


def bank_len():
    import json
    p = os.path.join(ROOT, 'kmchc', 'master', 'master_bank.json')
    if not os.path.exists(p):
        return None
    with open(p, encoding='utf-8') as f:
        d = json.load(f)
    it = d['items'] if isinstance(d, dict) else d
    return len(it), (it[-1]['id'] if it else '')


def main():
    fix = '--fix' in sys.argv
    git('fetch', 'origin', BRANCH, '-q')
    local = git('rev-parse', 'HEAD')
    remote = git('rev-parse', 'FETCH_HEAD')
    b = bank_len()

    if local == remote:
        print('✅ 로컬 = 원격 (%s)' % local[:7])
        if b:
            print('   은행 %d제 · 마지막 %s' % b)
        return

    # 로컬이 원격을 품고 있으면 = 방금 커밋했고 아직 안 밀었다
    ahead = git('rev-list', '--count', '%s..%s' % (remote, local), check=False)
    behind = git('rev-list', '--count', '%s..%s' % (local, remote), check=False)
    print('로컬 %s · 원격 %s — 앞선 커밋 %s · 뒤진 커밋 %s' %
          (local[:7], remote[:7], ahead or '?', behind or '?'))
    if b:
        print('   지금 은행 %d제 · 마지막 %s' % b)

    if ahead and ahead != '0' and (not behind or behind == '0'):
        print('⚠ 아직 푸시하지 않은 커밋이 있다 — 되돌림이 아니다. `git push` 할 것.')
        return

    print('🔴 ★되돌림으로 보인다★ — 원격이 앞서 있고 로컬에 그 커밋이 없다.')
    if not fix:
        print('   맞추려면: python3 syncguard.py --fix')
        return
    git('reset', '--hard', 'FETCH_HEAD')
    b2 = bank_len()
    print('✅ 원격에 맞췄다 — %s' % git('rev-parse', '--short', 'HEAD'))
    if b2:
        print('   은행 %d제 · 마지막 %s' % b2)
    print('   ※ untracked 파일은 reset 이 지우지 않으므로 그대로 남아 있다.')


if __name__ == '__main__':
    main()
