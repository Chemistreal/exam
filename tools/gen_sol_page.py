#!/usr/bin/env python3
"""`sol-final-<id>.html` 해설지를 `answers/<id>.json` 에서 만든다.

왜 필요한가
-----------
앱이 회차마다 `sol-final-<id>.html` 을 '해설지' 로 링크한다. 그런데 그 파일은
손으로 만들어져 있어서, `answers/<id>.json` 에 해설을 새로 써 넣어도 해설지는
옛날 그대로다 — 선생님이 내려받은 파일에는 아무것도 안 늘어난다.

이 생성기는 해설지를 **데이터에서** 만든다. 해설을 고치면 다시 돌리기만 하면
된다.

무엇을 싣고, 무엇을 안 싣는가
-----------------------------
문항 번호 · 정답 · 영역 · 개념 · 사고과정 · 짚어둘 점을 싣는다.
**문제 지문과 보기는 싣지 않는다.** 문제지는 이미 따로 있고(앱이 PDF 로
같이 내려받게 해 준다), 해설지에 다시 옮겨 적으면 같은 것을 한 번 더
퍼뜨리는 셈이다. 해설지는 문제지 옆에 두고 보는 문서다.

검토 상태를 숨기지 않는다
-------------------------
사람이 검수한 해설과 아직 검수 전인 해설을 같은 얼굴로 내보내면, 읽는 쪽은
구분할 방법이 없다. `verificationStatus` 가 `verified_*` 가 아닌 문항이 있으면
머리말에 그대로 적는다.

사용:
    python3 tools/gen_sol_page.py <시험id> [--write]
    python3 tools/gen_sol_page.py --check          # 전 회차가 데이터와 맞는지
"""

from __future__ import annotations

import html
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CIRC = {1: "①", 2: "②", 3: "③", 4: "④"}

CSS = """:root{--ink:#1a1a1a;--ink2:#4a463f;--teal:#0E5A4C;--ms:#C0603A;--line:#e6e2da;--bg:#faf8f4;--gold:#B08D57}
*{box-sizing:border-box}
body{margin:0;background:var(--bg);color:var(--ink);line-height:1.75;
 font-family:'Pretendard',-apple-system,BlinkMacSystemFont,'Apple SD Gothic Neo','Malgun Gothic',sans-serif}
header{padding:26px 20px 16px;border-bottom:1px solid var(--line);background:#fff}
.logo{font-size:11.5px;letter-spacing:.14em;color:var(--gold);font-weight:700}
h1{margin:6px 0 4px;font-size:23px;font-family:'Iropke Batang',serif}
.sub{color:var(--ink2);font-size:13.5px}
.warn{margin:12px 20px 0;padding:10px 13px;border:1px solid #E0C9A6;background:#FFF8EC;
 border-radius:8px;font-size:13px;color:#7a5a22}
main{max-width:860px;margin:0 auto;padding:16px 20px 60px}
table{border-collapse:collapse;width:100%;margin:14px 0 26px;font-size:13.5px;background:#fff}
th,td{border:1px solid var(--line);padding:6px 8px;text-align:center}
th{background:#f1eee7;font-weight:700}
.q{background:#fff;border:1px solid var(--line);border-radius:10px;padding:14px 16px;margin:12px 0}
.qh{display:flex;flex-wrap:wrap;gap:10px;align-items:center;margin-bottom:8px}
.qno{font-weight:700;color:var(--teal)}
.area{font-size:12.5px;color:var(--ink2);background:#f1eee7;border-radius:99px;padding:2px 9px}
.ans{margin-left:auto;font-weight:700;color:var(--ms)}
.sol{font-size:14.5px}
.tip{margin-top:9px;padding:9px 11px;border-left:3px solid var(--gold);background:#faf7f1;
 font-size:13.5px;color:var(--ink2)}
.rev{margin-top:9px;padding:9px 11px;border-left:3px solid var(--ms);background:#fdf3ef;
 font-size:13px;color:#8a3a1d}
@media print{body{background:#fff}.q{break-inside:avoid}}
"""


def build(exam_id: str) -> str:
    exams = {e["id"]: e for e in json.loads((ROOT / "exams.json").read_text(encoding="utf-8"))}
    exam = exams.get(exam_id)
    if not exam:
        raise SystemExit(f"exams.json 에 없는 시험: {exam_id}")
    data = json.loads((ROOT / "answers" / f"{exam_id}.json").read_text(encoding="utf-8"))
    q = data["questions"]

    unreviewed = [k for k in q if not str(q[k].get("verificationStatus", "")).startswith("verified")]
    has_exp = [k for k in q if str(q[k].get("explanation") or "").strip()]

    esc = html.escape
    out = ["<!DOCTYPE html><html lang=\"ko\"><head><meta charset=\"utf-8\">",
           "<meta name=\"viewport\" content=\"width=device-width,initial-scale=1\">",
           f"<title>{esc(exam['title'])} · 해설지</title><style>{CSS}</style></head><body>",
           "<header><div class=\"logo\">CHEMISTREAL · FINAL 해설지</div>",
           f"<h1>{esc(exam['title'])}</h1>",
           f"<div class=\"sub\">문항별 정답 · 영역 · 개념"
           f"{' · 사고과정 해설' if has_exp else ''} · {exam['nQ']}문항</div>",
           "<div class=\"sub\" style=\"margin-top:6px\">문제 지문은 문제지(PDF)에 있습니다 — "
           "성적표 화면에서 함께 내려받을 수 있습니다.</div></header>"]

    if unreviewed and has_exp:
        out.append(f"<div class=\"warn\"><b>검수 전 해설입니다.</b> {len(unreviewed)}문항의 사고과정이 "
                   "아직 선생님 검수를 거치지 않았습니다. 배포 전에 확인해 주세요.</div>")

    out.append("<main><h3>정답 · 영역 · 개념</h3><table><thead><tr>"
               "<th>문항</th><th>정답</th><th>영역</th><th>개념(유형)</th></tr></thead><tbody>")
    for k in sorted(q, key=int):
        r = q[k]
        out.append(f"<tr><td>{k}</td><td>{CIRC.get(int(r['answer']), r['answer'])}</td>"
                   f"<td>{esc(r.get('area',''))}</td><td>{esc(r.get('concept',''))}</td></tr>")
    out.append("</tbody></table>")

    if has_exp:
        out.append("<h3>문항별 사고과정</h3>")
        for k in sorted(q, key=int):
            r = q[k]
            body = str(r.get("explanationHtml") or "").strip()
            if not body:
                continue
            out.append("<div class=\"q\"><div class=\"qh\">"
                       f"<span class=\"qno\">문제 {k}</span>"
                       f"<span class=\"area\">{esc(r.get('concept',''))}</span>"
                       f"<span class=\"ans\">정답 {CIRC.get(int(r['answer']), r['answer'])}</span></div>"
                       f"<div class=\"sol\">{body}</div>")
            if r.get("reviewNote"):
                out.append(f"<div class=\"rev\"><b>확인 필요</b> {esc(r['reviewNote'])}</div>")
            out.append("</div>")

    out.append("</main></body></html>")
    return "\n".join(out) + "\n"


def main() -> int:
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    write = "--write" in sys.argv[1:]

    if "--check" in sys.argv[1:]:
        exams = json.loads((ROOT / "exams.json").read_text(encoding="utf-8"))
        stale = []
        for e in exams:
            page = ROOT / f"sol-final-{e['id']}.html"
            if not page.exists():
                stale.append(f"{e['id']}: 해설지 없음")
                continue
            # 이 생성기가 만든 페이지만 견준다(옛 수작업 해설지는 건드리지 않는다)
            cur = page.read_text(encoding="utf-8")
            if "CHEMISTREAL · FINAL 해설지</div>" not in cur or "정답 · 영역 · 개념</h3>" not in cur:
                continue
            if cur != build(e["id"]):
                stale.append(f"{e['id']}: 해설 데이터와 어긋난다")
        if stale:
            print("FAIL 해설지가 데이터와 어긋난다:")
            for s in stale:
                print("  " + s)
            return 1
        print("PASS 생성기가 만든 해설지가 모두 데이터와 일치")
        return 0

    if not args:
        print(__doc__)
        return 2
    page = build(args[0])
    target = ROOT / f"sol-final-{args[0]}.html"
    if write:
        target.write_text(page, encoding="utf-8")
        print(f"{target.name} 에 적었다 ({len(page)/1024:.1f}KB)")
        return 0
    print(page[:600] + "\n…")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except BrokenPipeError:
        sys.exit(0)
