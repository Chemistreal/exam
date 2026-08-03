#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""서비스워커 캐시 이름을 **껍데기 파일의 내용**에서 짓는다.

왜 필요한가
-----------
2026-08-03, 성적표 링크의 인원이 굳는 것을 고쳐 배포했다. 깃허브 페이지에는
새 `final.html` 이 올라갔고, 앱스크립트 창구도 새 숫자를 주고 있었다.
그런데 화면은 그대로였다.

서비스워커가 `VERSION = '2026.07.31'` 로 캐시를 잡고 있어서, 브라우저가
**옛 final.html 을 캐시에서 꺼내 쓰고 있었다.** 고쳐서 배포해도 아무한테도
안 간다 — 선생님에게도, 학부모에게도.

손으로 날짜를 올리는 규칙이었는데, 손으로 하는 규칙은 잊힌다. 잊혀도
아무 표시가 안 나서 **고친 줄 알고 지나간다.** 그게 제일 나쁘다.

그래서 껍데기 파일들의 내용으로 이름을 짓는다. 한 글자라도 바뀌면 이름이
바뀌고, 안 바뀌면 그대로다 — 잊을 자리가 없다.

    실행:  python3 tools/gen_sw_version.py            # 고쳐 쓴다
           python3 tools/gen_sw_version.py --check    # 어긋나면 빨간불
"""
import hashlib
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
SW = ROOT / "sw.js"

# sw.js 의 ASSETS 목록에서 읽어 온다. 손으로 두 곳에 적으면 언젠가 갈린다 —
# 새 화면을 캐시에 넣고 여기 안 적으면, 그 화면만 옛 판으로 남는다.
ASSET_RE = re.compile(r"const ASSETS\s*=\s*\[(.*?)\];", re.S)
VER_RE = re.compile(r"^const VERSION = '([^']*)';$", re.M)


def shell_files():
    m = ASSET_RE.search(SW.read_text(encoding="utf-8"))
    if not m:
        raise SystemExit("sw.js 에서 ASSETS 목록을 못 찾았습니다")
    out = []
    for raw in re.findall(r"'([^']+)'", m.group(1)):
        rel = raw.lstrip("./")
        if not rel or rel.endswith("/"):
            continue          # './' 는 index.html 과 같은 것을 가리킨다
        out.append(rel)
    return sorted(set(out))


def want_version():
    h = hashlib.sha256()
    missing = []
    for rel in shell_files():
        p = ROOT / rel
        if not p.exists():
            missing.append(rel)
            continue
        h.update(rel.encode("utf-8"))
        h.update(b"\0")
        h.update(p.read_bytes())
        h.update(b"\0")
    if missing:
        # 없는 파일은 sw.js 가 c.add() 실패를 삼키므로 설치는 깨지지 않는다.
        # 다만 목록에 적어 두고 안 만든 것이므로 알려는 준다.
        print("알림: ASSETS 에 있는데 없는 파일 — " + ", ".join(missing))
    return h.hexdigest()[:12]


def main():
    src = SW.read_text(encoding="utf-8")
    m = VER_RE.search(src)
    if not m:
        raise SystemExit("sw.js 에서 VERSION 줄을 못 찾았습니다")
    now, want = m.group(1), want_version()
    if now == want:
        print(f"PASS sw.js VERSION = {want} (껍데기 {len(shell_files())}개)")
        return 0
    if "--check" in sys.argv[1:]:
        print(
            "FAIL 서비스워커 캐시 이름이 껍데기 내용과 어긋납니다\n"
            f"       지금 {now} · 있어야 할 값 {want}\n"
            "\n"
            "     이대로 배포하면 **브라우저가 옛 화면을 캐시에서 꺼내 씁니다.**\n"
            "     고쳐서 올렸는데 아무한테도 안 갑니다 — 2026-08-03 에 실제로\n"
            "     그랬습니다(성적표 인원 고침이 하루 종일 안 보였다).\n"
            "\n"
            "     고치기:  python3 tools/gen_sw_version.py"
        )
        return 1
    SW.write_text(VER_RE.sub(f"const VERSION = '{want}';", src, count=1), encoding="utf-8")
    print(f"고침 sw.js VERSION {now} → {want}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
