#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""대화 기록에서 **사람이 보낸 말만** 뽑아 낸다 — 이름은 가리고.

왜 필요한가
-----------
「하려다 만 것」을 찾을 때 가장 믿을 만한 재료는 **사람이 실제로 시킨 말**이다.
그런데 그 말은 153 MB 짜리 대화 기록 안에 도구 결과·시스템 알림과 뒤섞여 있어서
그대로는 못 읽는다.

⚠ **뽑아 낸 것을 저장소에 두지 않는다.** 사람이 보낸 말에는 학생 이름이 들어
  있다(실제로 그랬고, exam 쪽 name_guard 가 잡아냈다). 이 도구는 작업 폴더에만
  쓰고, 쓰기 전에 **두 저장소의 금지 명단을 합쳐** 이름을 ○○○ 로 가린다.
  명단이 저장소마다 다르므로 한쪽만 보면 새는 자리가 생긴다 — 실제로 DT 명단만
  썼을 때 다섯 가지가 남아 있었다.

    python3 tools/msg_extract.py <대화기록.jsonl> <나갈 파일.json>
"""
import importlib.util
import io
import json
import os
import sys

GUARDS = ('/home/user/dt/tools/name_guard.py', '/home/user/exam/tools/name_guard.py')


def banned():
    """두 저장소의 금지 명단을 합친다. 해시만 오간다 — 이름은 안 읽는다."""
    hashes, mod = set(), None
    for p in GUARDS:
        if not os.path.exists(p):
            continue
        spec = importlib.util.spec_from_file_location('ng', p)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        hashes |= set(mod.load().get('hashes') or [])
    return hashes, mod


def main():
    if len(sys.argv) < 3:
        print(__doc__)
        return 2
    src, dst = sys.argv[1], sys.argv[2]
    want, g = banned()
    if not want:
        print('금지 명단을 못 찾았다 — 이름을 못 가리므로 그만둔다')
        return 1
    out = []
    with io.open(src, encoding='utf-8', errors='ignore') as f:
        for i, line in enumerate(f, 1):
            if '"role":"user"' not in line and '"role": "user"' not in line:
                continue
            try:
                d = json.loads(line)
            except Exception:
                continue
            m = d.get('message') or {}
            if m.get('role') != 'user':
                continue
            c = m.get('content')
            if isinstance(c, list):
                t = ' '.join(x.get('text', '') for x in c
                             if isinstance(x, dict) and x.get('type') == 'text')
            else:
                t = str(c or '')
            t = t.strip()
            # 도구 결과·시스템 알림은 사람이 보낸 말이 아니다
            if not t or t.startswith('<'):
                continue
            if 'tool_use_id' in line and 'tool_result' in line:
                continue
            if t.startswith(('Caveat:', '[SYSTEM', 'This session is being continued')):
                continue
            out.append({'i': i, 't': t[:4000]})
    # 이름 가리기 — 가리기 전에는 아무 데도 안 쓴다
    hit = {c for m in out for c in g.candidates(m['t']) if g.h(c) in want}
    for m in out:
        for c in sorted(hit, key=len, reverse=True):
            m['t'] = m['t'].replace(c, '○○○')
    left = [c for m in out for c in g.candidates(m['t']) if g.h(c) in want]
    if left:
        print('가리기에 실패한 자리가 남았다 — 쓰지 않는다')
        return 1
    io.open(dst, 'w', encoding='utf-8').write(
        json.dumps(out, ensure_ascii=False, indent=1) + '\n')
    print('사람이 보낸 말 %d개 · 이름 %d가지를 가렸다 → %s' % (len(out), len(hit), dst))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
