#!/usr/bin/env python3
"""교사용 채점 결과 화면의 '다음 학생 채점' 동선을 항상 눈에 띄게 유지한다.

공유 성적표(#r=...)에는 선생님용 조작 버튼을 노출하지 않고,
교사용 직접 채점 화면에는 성적표 상단과 하단 모두 다음 학생 버튼을 둔다.
멱등적으로 실행할 수 있다.
"""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PATH = ROOT / "final.html"


def main() -> int:
    s = PATH.read_text(encoding="utf-8")

    # 기존 하단 버튼 문구를 교사용 목적이 분명하도록 복원한다.
    s = s.replace('onclick="nextStudent()">다음 학생 입력 ▶',
                  'onclick="nextStudent()">다음 학생 채점 ▶')

    # 긴 고급 성적표를 끝까지 스크롤하지 않아도 바로 다음 학생으로 넘어갈 수 있게
    # 결과 제목 바로 아래에도 교사용 전용 동선을 둔다. 공유 성적표에는 숨긴다.
    marker = 'class="toolbar teacher-next"'
    if marker not in s:
        anchor = '   <h2 class="serif" style="margin:6px 0 2px;font-size:20px">${esc(cur.title)} · 성적표</h2>\n'
        insert = anchor + "   ${window.__sharedReport?'':`<div class=\"toolbar teacher-next\" style=\"justify-content:flex-end;margin:10px 0 14px\"><button class=\"btn\" onclick=\"nextStudent()\">다음 학생 채점 ▶</button><button class=\"btn ghost sm\" onclick=\"openExam('${cur.id}')\">다시 채점</button></div>`}\n"
        n = s.count(anchor)
        if n < 1:
            raise SystemExit("성적표 제목 앵커를 찾지 못했다")
        s = s.replace(anchor, insert)

    PATH.write_text(s, encoding="utf-8")
    out = PATH.read_text(encoding="utf-8")
    if '다음 학생 채점 ▶' not in out or marker not in out:
        raise SystemExit("다음 학생 채점 버튼 복원 검증 실패")
    print("PASS 교사용 다음 학생 채점 버튼 · 상단/하단 복원")
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
