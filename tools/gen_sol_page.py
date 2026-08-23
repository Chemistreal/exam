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
/* 놋쇠 원색(--gold #B08D57)은 흰 종이 위에서 3.09:1 이라 글자로는 못 쓴다.
   해설지의 갈래 표식은 옥색이다(tools/theme.py 의 '갈래별 표식'). */
.logo{font-size:11.5px;letter-spacing:.14em;color:var(--teal);font-weight:700}
h1{margin:6px 0 4px;font-size:23px;font-family:'Iropke Batang',serif}
.sub{color:var(--ink2);font-size:13.5px}
/* 돌아가는 길. 강의 페이지와 같은 모양으로 둔다 — 학부모가 두 화면을
   오가므로 같은 자리에 같은 것이 있어야 헷갈리지 않는다. */
.back{display:inline-block;margin-top:12px;color:var(--teal);text-decoration:none;font-size:14px;font-weight:600;padding:6px 0}
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
/* 해설 본문이 실제로 입는 옷 — 답지(answers)의 explanationHtml 이
   <h4>·.step·.k(정답 근거)·.x(오답 표시) 를 쓰는데 여기 옷이 없으면
   해설지에서만 맨몸으로 나간다(final.html 은 제 옷이 따로 있다). */
.sol h4{margin:12px 0 5px;color:var(--teal);font-size:13.5px;letter-spacing:.02em}
.sol p.step{margin:6px 0;white-space:pre-wrap}
.sol .k{color:var(--teal);font-weight:700}
.sol .x{color:var(--ms);font-weight:700}
.tip{margin-top:9px;padding:9px 11px;border-left:3px solid var(--gold);background:#faf7f1;
 font-size:13.5px;color:var(--ink2)}
.rev{margin-top:9px;padding:9px 11px;border-left:3px solid var(--ms);background:#fdf3ef;
 font-size:13px;color:#8a3a1d}
/* 정답표 → 그 문항 해설로 건너뛰는 길. 표가 세로 2,000px 를 넘는 회차가
   많아 표에서 해설까지 손가락으로 미는 거리가 너무 멀었다. */
td a.jump{color:var(--teal);text-decoration:none;font-weight:700}
td a.jump:hover{text-decoration:underline}
.q{scroll-margin-top:14px}
.q:target{border-color:var(--teal);box-shadow:0 0 0 2px rgba(14,90,76,.18)}
@media print{body{background:#fff}.q{break-inside:avoid}.warn{display:none}}
"""


def all_exams() -> list:
    """exams.json 과 곁방 두 채(student-finals · teacher-exams)를 한데 본다.

    학생별 파이널은 목록·수·되돌림 검사를 흔들지 않으려고 exams.json 밖에 산다.
    그래도 **제 해설이 있는 회차**(선생님이 한글로 새로 낸 변형본·실전세트)는
    해설지가 있어야 한다 — 성적표가 그 링크를 건다.
    """
    out = json.loads((ROOT / "exams.json").read_text(encoding="utf-8"))
    for side in ("student-finals.json", "teacher-exams.json"):
        p = ROOT / side
        if not p.exists():
            continue
        doc = json.loads(p.read_text(encoding="utf-8"))
        for e in doc.get("exams", []):
            # 원본 회차의 크롭을 빌려 쓰는 파생 회차는 제 해설지가 없다
            if e.get("srcmap"):
                continue
            if (ROOT / "answers" / f"{e['id']}.json").exists():
                out.append(e)
    return out


def build(exam_id: str) -> str:
    exams = {e["id"]: e for e in all_exams()}
    exam = exams.get(exam_id)
    if not exam:
        raise SystemExit(f"어느 회차 목록에도 없는 시험: {exam_id}")
    data = json.loads((ROOT / "answers" / f"{exam_id}.json").read_text(encoding="utf-8"))
    q = data["questions"]

    # ── 삭제된 문항의 '정답' 은 ⓪ 이 아니라 '전원정답' 이다 ──────────────
    # 정답 칸이 `정답 0` 으로 찍히는 자리가 넷 있었다(2009 51 · 2010 38·42 ·
    # 2018 34). 학생에게 0 은 아무 뜻이 아니다. 더 나쁜 것은 그 반대쪽이다 —
    # 2019 23·42 와 kmchc-2025 38·41 은 폐기 문항인데 `정답 ①` 이라고 적혀
    # 있었다. 무엇을 골라도 맞는 문항을 하나만 맞는 것처럼 보여 준 셈이다.
    # 채점 규칙(final.html allc)과 같은 기준으로 여기서도 '전원정답' 이라 적는다.
    allc = set(exam.get("miss") or []) | set(exam.get("voided") or [])
    for qq, v in (exam.get("multi") or {}).items():
        if len(v) >= 4:
            allc.add(int(qq))
    for i, kk in enumerate(exam.get("key") or [], 1):
        if kk in (0, "", None, "X", "x"):
            allc.add(i)

    # ── 복수정답 문항은 «어느 것을 인정하는지» 를 적는다 ────────────────
    # 여태 해설지는 대표 답 하나만 적었다. hwol-2018 27번은 ①·② 를 다 인정하는데
    # 「정답 ①」 이라고만 적혀 있었다 — ② 를 쓴 학생은 맞게 채점되고도 해설지에서
    # 다른 답을 본다. 점수는 맞으니 아무도 안 걸린다.
    # 채점이 인정하는 답을 그대로 적는다(선생님 결정 2026-08-17). 열한 문항이다.
    multi = {}
    for qq, v in (exam.get("multi") or {}).items():
        n = int(qq)
        if n not in allc and len(v or []) >= 2:
            multi[n] = sorted(int(x) for x in v)

    def ansOf(num, r):
        n = int(num)
        if n in allc:
            return "전원정답"
        if n in multi:
            return "·".join(CIRC.get(x, str(x)) for x in multi[n]) + " 복수정답"
        return CIRC.get(int(r["answer"]), r["answer"])

    unreviewed = [k for k in q if not str(q[k].get("verificationStatus", "")).startswith("verified")]
    has_exp = [k for k in q if str(q[k].get("explanation") or "").strip()]

    esc = html.escape
    source_files = [
        (exam.get("pdf"), "공식 문제 PDF ↓"),
        (exam.get("answerPdf"), "공식 정답 PDF ↓"),
        (exam.get("bookPdf"), "문제편·해설편 PDF ↓"),
    ]
    source_files = [(path, label) for path, label in source_files if path]
    # 내려받기 단추 옷은 단추가 있을 때만 낸다.
    asset_css = """
.source-assets{max-width:860px;margin:14px auto 0;padding:0 20px;display:flex;gap:8px;flex-wrap:wrap}
.source-assets a{display:inline-flex;align-items:center;padding:8px 11px;border:1px solid var(--line);
 border-radius:8px;background:#fff;color:var(--teal);font-size:13px;font-weight:700;text-decoration:none}
.source-assets a:hover{border-color:var(--teal)}
""" if exam.get("answerPdf") or exam.get("bookPdf") else ""

    # ⚠ 절 나눔 해설의 옷은 **늘** 낸다. 예전에는 위 단추 옷과 한 덩이로 묶여
    #   `answerPdf 나 bookPdf 가 있을 때만` 나갔다 — 둘은 아무 상관이 없는데도.
    #   해설은 절 나눔으로 썼는데 그 회차에 딸린 PDF 가 없으면, 해설지가 옷을
    #   못 입고 나가면서도 파일은 멀쩡히 만들어지고 검사도 다 지나간다.
    #   지금은 안 걸리지만(그런 회차가 없다) 다음에 한 회차만 그렇게 되면
    #   아무도 모르게 무너진다. 걸릴 일을 남겨 두지 않는다.
    sol_css = """
.sol-part{margin:13px 0}.sol-part h4{margin:0 0 5px;color:var(--teal);font-size:13.5px;letter-spacing:.02em}
.sol-part p{margin:5px 0;white-space:pre-wrap}
.answer-confirm{margin:14px 0 0;padding-top:9px;border-top:1px dashed var(--line);color:var(--teal)}
"""
    extra_css = asset_css + sol_css
    out = ["<!DOCTYPE html><html lang=\"ko\"><head><meta charset=\"utf-8\">",
           "<meta name=\"viewport\" content=\"width=device-width,initial-scale=1\">",
           f"<title>{esc(exam['title'])} · 해설지</title><style>{CSS}{extra_css}</style></head><body>",
           "<header><div class=\"logo\">CHEMISTREAL · FINAL 해설지</div>",
           f"<h1>{esc(exam['title'])}</h1>",
           f"<div class=\"sub\">문항별 정답 · 영역 · 개념"
           f"{' · 사고과정 해설' if has_exp else ''} · {exam['nQ']}문항</div>",
           "<div class=\"sub\" style=\"margin-top:6px\">문제 지문은 문제지(PDF)에 있습니다 — "
           "성적표 화면에서 함께 내려받을 수 있습니다.</div>"
           # ⚠ 돌아가는 길이 없었다. 학부모가 성적표에서 '해설지' 를 누르면
           #   11,000자짜리 이 화면이 열리는데 **화면 안에 나가는 문이 없다.**
           #   휴대폰 뒤로 가기를 눌러도 되지만, 길이 안 보이면 거기서 끝난다.
           #   강의 페이지(lec-*)는 진작 `‹ 성적표로` 를 달고 있었다 — 같은
           #   규칙을 여기에도 준다(2026-08-10, 학부모 눈으로 훑다 찾음).
           #   ?from= 이 실려 오면 아래 조각이 '‹ 성적표로' 로 바꾼다.
           "<a class=\"back\" href=\"final.html\">‹ 파이널로</a></header>"]

    if exam.get("answerPdf") or exam.get("bookPdf"):
        links = "".join(
            f'<a href="{esc(path)}" download>{label}</a>' for path, label in source_files
        )
        out.append(f'<nav class="source-assets" aria-label="시험 자료 직접 다운로드">{links}</nav>')

    # ⚠ 이 띠는 학생·학부모도 읽는다 — 「배포 전에 확인해 주세요」 는 선생님께
    #   하는 말이라 받는 쪽을 헷갈리게 한다(내가 받은 게 배포 전 문서인가?).
    #   읽는 사람이 할 일이 있는 말만 적고, 인쇄물에는 싣지 않는다(@media print).
    if unreviewed and has_exp:
        out.append(f"<div class=\"warn\"><b>해설 업데이트 안내</b> · {len(unreviewed)}문항의 사고과정은 "
                   "선생님 검토에 따라 표현이 다듬어질 수 있습니다. 정답·채점 기준은 확정입니다.</div>")

    # 사고과정 카드가 실제로 서는 문항 — 정답표에서 그 카드로 건너뛰게 한다.
    # 정답표가 세로 2,000px 를 넘는 회차가 많아, 표에서 본 문항의 해설을
    # 찾으려면 수십 화면을 밀어야 했다. 표의 문항 번호가 곧 문이 된다.
    carded = {k for k in q if str(q[k].get("explanationHtml") or "").strip()}
    out.append("<main><h3>정답 · 영역 · 개념</h3><table><thead><tr>"
               "<th scope=\"col\">문항</th><th scope=\"col\">정답</th>"
               "<th scope=\"col\">영역</th><th scope=\"col\">개념(유형)</th></tr></thead><tbody>")
    for k in sorted(q, key=int):
        r = q[k]
        cell = f'<a class="jump" href="#q{k}">{k}</a>' if k in carded else k
        out.append(f"<tr><td>{cell}</td><td>{ansOf(k, r)}</td>"
                   f"<td>{esc(r.get('area',''))}</td><td>{esc(r.get('concept',''))}</td></tr>")
    out.append("</tbody></table>")

    if has_exp:
        out.append("<h3>문항별 사고과정</h3>")
        for k in sorted(q, key=int):
            r = q[k]
            body = str(r.get("explanationHtml") or "").strip()
            if not body:
                continue
            out.append(f"<div class=\"q\" id=\"q{k}\"><div class=\"qh\">"
                       f"<span class=\"qno\">문제 {k}</span>"
                       f"<span class=\"area\">{esc(r.get('concept',''))}</span>"
                       # '정답 전원정답'·'정답 ①·④ 복수정답' 은 말이 겹친다 —
                       # 그 두 가지는 그 자체로 답 자리다
                       f"<span class=\"ans\">{ansOf(k, r) if (int(k) in allc or int(k) in multi) else '정답 ' + str(ansOf(k, r))}</span></div>"
                       f"<div class=\"sol\">{body}</div>")
            if r.get("reviewNote"):
                out.append(f"<div class=\"rev\"><b>확인 필요</b> {esc(r['reviewNote'])}</div>")
            out.append("</div>")

    # 성적표에서 왔으면 성적표로 돌려보낸다(lec-*.html 과 같은 규칙).
    # 주소를 **받기만** 하고 믿지는 않는다 — 같은 곳의 final.html 이고
    # 성적표(#r=)일 때만 쓴다. 남이 심어 둔 주소로 내보내지 않는다.
    out.append("""<script data-lec-back>
(function(){function ok(raw){if(!raw)return null;try{var u=new URL(raw,location.href);
if(u.origin!==location.origin)return null;if(!/(^|\\/)final\\.html$/.test(u.pathname))return null;
if(!/[#&]r=/.test(u.hash))return null;return u.href;}catch(e){return null;}}
try{var a=document.querySelector('a.back');if(!a)return;
var to=ok(new URL(location.href).searchParams.get('from'));if(!to)return;
a.href=to;a.textContent='\\u2039 \\uc131\\uc801\\ud45c\\ub85c';}catch(e){}})();
</script>""")
    out.append("</main></body></html>")
    return "\n".join(out) + "\n"


def themed(page: str, exam_id: str) -> str:
    """생성한 글에도 **같은 옷**을 입힌다.

    안 입히면 이 생성기가 만드는 글과 저장소에 있는 글이 영영 어긋난다 —
    `tools/theme.py` 는 파일에 옷을 입히고, 여기는 그걸 모른 채 옛 모양을
    만들어 내기 때문이다. 한쪽만 알고 있으면 검사는 매번 빨간불이다.
    """
    sys.path.insert(0, str(ROOT / "tools"))
    import theme
    return theme.apply(page, theme.plan(f"sol-final-{exam_id}.html", page)) or page


def main() -> int:
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    write = "--write" in sys.argv[1:]

    if "--check" in sys.argv[1:]:
        exams = all_exams()
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
            if cur != themed(build(e["id"]), e["id"]):
                stale.append(f"{e['id']}: 해설 데이터와 어긋난다")
        # 반대쪽도 본다 — exams.json 에 없는 회차의 해설지가 남아 있으면
        # 성적표 어디에서도 못 고르는데 파일 목록에는 뜬다. 실제로 넷이
        # 그랬고, 그 가운데 '화올 2020' 은 2019 회차의 정답을 2020 이라는
        # 이름으로 보여 주고 있었다. 없는 회차의 정답표만큼 나쁜 것은 없다.
        ids = {e["id"] for e in exams}
        for page in sorted(ROOT.glob("sol-final-*.html")):
            eid = page.name[len("sol-final-"):-len(".html")]
            if eid not in ids:
                stale.append(f"{eid}: 어느 회차 목록에도 없는 해설지다 "
                             f"({page.name}) — 지우거나 회차를 넣어라")
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
    page = themed(build(args[0]), args[0])
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
