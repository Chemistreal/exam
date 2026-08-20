#!/usr/bin/env python3
"""USNCO 2026 National Part I를 기존 final 리포트 품질로 통합한다.

- final.html / final-submit.html 목록에 USNCO 그룹을 노출한다.
- 학생 제출 완료 뒤 축약 결과가 아니라 final.html 전체 진단 리포트로 이동한다.
- USNCO 문항 영역명을 기존 진단 엔진의 표준 영역으로 정규화한다.
- 기존 answers 데이터의 상세 해설은 절대 덮어쓰지 않고 정답·영역 메타데이터만 맞춘다.
- 회차별 제출 주소 목록/표에서도 USNCO를 별도 그룹으로 정확히 표시한다.

이 스크립트는 멱등적이다. 한 번 적용된 저장소에서 다시 실행해도 같은 결과가 난다.
"""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EXAM_ID = "usnco-2026-natl-1"

AREAS = [
    "몰과양적관계", "기체", "중화반응", "기체", "액체,용액", "액체,용액",
    "원소분석장치", "원소분석장치", "분자간인력", "액체,용액", "원소분석장치", "원소분석장치",
    "분자간인력", "상평형", "액체,용액", "상평형", "분자간인력", "고체",
    "화학평형", "열화학", "깁스자유에너지", "열화학", "깁스자유에너지", "깁스자유에너지",
    "반응속도", "반응속도", "반응속도", "반응속도", "반응속도", "반응속도",
    "산과염기", "화학평형", "화학평형", "중화반응", "용해평형", "용해평형",
    "산화환원", "전지", "전지", "전지", "전기분해", "전지",
    "주기율", "원자모형", "화학결합", "원자모형", "전지", "원자모형",
    "분자의모양", "분자의모양", "분자오비탈", "분자의모양", "분자의모양", "배위화학",
    "탄소화합물", "탄소화합물", "탄소화합물", "탄소화합물", "탄소화합물", "탄소화합물",
]


def replace_once(text: str, old: str, new: str, label: str) -> str:
    n = text.count(old)
    if n == 0:
        if new in text:
            return text
        raise SystemExit(f"{label}: 교체할 앵커를 찾지 못했다")
    if n != 1:
        raise SystemExit(f"{label}: 앵커가 {n}개라 안전하게 자동 수정할 수 없다")
    return text.replace(old, new, 1)


def find_object_span(text: str, needle: str) -> tuple[int, int]:
    at = text.index(needle)
    start = text.rfind("{", 0, at)
    if start < 0:
        raise SystemExit("USNCO 시험 객체 시작을 찾지 못했다")
    depth = 0
    in_str = False
    esc = False
    for i in range(start, len(text)):
        ch = text[i]
        if in_str:
            if esc:
                esc = False
            elif ch == "\\":
                esc = True
            elif ch == '"':
                in_str = False
            continue
        if ch == '"':
            in_str = True
        elif ch == "{":
            depth += 1
        elif ch == "}":
            depth -= 1
            if depth == 0:
                return start, i + 1
    raise SystemExit("USNCO 시험 객체 끝을 찾지 못했다")


def patch_exams() -> dict:
    path = ROOT / "exams.json"
    text = path.read_text(encoding="utf-8")
    start, end = find_object_span(text, f'"id":"{EXAM_ID}"' if f'"id":"{EXAM_ID}"' in text else f'"id": "{EXAM_ID}"')
    exam = json.loads(text[start:end])
    if len(exam.get("key") or []) != 60 or len(exam.get("type") or []) != 60:
        raise SystemExit("USNCO 정답/유형 데이터가 60문항이 아니다")
    if len(AREAS) != 60:
        raise SystemExit("표준 영역표가 60문항이 아니다")

    exam["group"] = "USNCO"
    exam["track"] = "National Part I"
    exam["source"] = "USNCO 2026 National Exam · Part I"
    exam["nQ"] = 60
    exam["mode"] = "auto"
    exam["cut"] = [0, 4, 9, 13, 18]
    exam["area"] = AREAS

    rendered = json.dumps(exam, ensure_ascii=False, indent=2)
    text = text[:start] + rendered + text[end:]
    json.loads(text)
    path.write_text(text, encoding="utf-8")
    return exam


def patch_pages() -> None:
    p = ROOT / "final-submit.html"
    s = p.read_text(encoding="utf-8")
    s = replace_once(
        s,
        "const GROUPS=[['JMChC','JMChC 모의고사'],['동형','기출 동형'],['산과염기','산·염기 집중'],['2026','KMChC 2026'],['2025','KMChC 2025'],['2024','KMChC 2024'],['이전','KMChC 이전 기출']];",
        "const GROUPS=[['JMChC','JMChC 모의고사'],['동형','기출 동형'],['산과염기','산·염기 집중'],['USNCO','USNCO National Exam'],['2026','KMChC 2026'],['2025','KMChC 2025'],['2024','KMChC 2024'],['이전','KMChC 이전 기출']];",
        "final-submit USNCO 그룹",
    )
    s = replace_once(
        s,
        "fetch(SHEET_ENDPOINT,{method:'POST',mode:'no-cors',headers:{'Content-Type':'text/plain;charset=utf-8'},body:JSON.stringify(payload)});",
        "fetch(SHEET_ENDPOINT,{method:'POST',mode:'no-cors',keepalive:true,headers:{'Content-Type':'text/plain;charset=utf-8'},body:JSON.stringify(payload)});",
        "final-submit keepalive",
    )
    s = replace_once(
        s,
        "  clearDraft(cur.id); // 제출 완료 → 임시저장 답안 삭제\n\n  showResult(nm,sch,cur,correct,total,pct,rs,wrong);",
        "  clearDraft(cur.id); // 제출 완료 → 임시저장 답안 삭제\n\n  // 다른 회차와 동일한 전체 진단 성적표 엔진으로 바로 이어 준다.\n  // 축약 showResult는 네트워크/내비게이션 예외 때만 남겨 두는 안전망이다.\n  const reportUrl=shareLink(cur,sel,nm);\n  try{ location.assign(reportUrl); return; }catch(e){}\n  showResult(nm,sch,cur,correct,total,pct,rs,wrong);",
        "final-submit 전체 성적표 이동",
    )
    p.write_text(s, encoding="utf-8")

    p = ROOT / "final.html"
    s = p.read_text(encoding="utf-8")
    s = replace_once(
        s,
        "const order=['JMChC','동형','산과염기','2026','2025','2024','이전'];",
        "const order=['JMChC','동형','산과염기','USNCO','2026','2025','2024','이전'];",
        "final USNCO 순서",
    )
    s = replace_once(
        s,
        "const GLAB={'JMChC':['JMChC 모의고사','60문항 · 영역·개념'],'동형':['기출동형 모의고사','영역·개념'],'산과염기':['산·염기 60제','영역·개념']};",
        "const GLAB={'JMChC':['JMChC 모의고사','60문항 · 영역·개념'],'동형':['기출동형 모의고사','영역·개념'],'산과염기':['산·염기 60제','영역·개념'],'USNCO':['USNCO National Exam','Part I · 60문항 · 2시간 · +3/−1']};",
        "final USNCO 라벨",
    )
    s = replace_once(
        s,
        "var order=['JMChC','동형','산과염기','2026','2025','2024','이전'];",
        "var order=['JMChC','동형','산과염기','USNCO','2026','2025','2024','이전'];",
        "제출주소 USNCO 순서",
    )
    s = replace_once(
        s,
        "var GLAB={'JMChC':'JMChC 모의고사','동형':'기출동형 모의고사','산과염기':'산·염기 60제'};",
        "var GLAB={'JMChC':'JMChC 모의고사','동형':'기출동형 모의고사','산과염기':'산·염기 60제','USNCO':'USNCO National Exam'};",
        "제출주소 USNCO 라벨",
    )
    p.write_text(s, encoding="utf-8")


def sync_answer_metadata(exam: dict) -> None:
    """기존 상세 해설을 보존하고, 채점/분류 메타데이터만 exams.json과 동기화한다."""
    path = ROOT / "answers" / f"{EXAM_ID}.json"
    if path.exists():
        out = json.loads(path.read_text(encoding="utf-8"))
    else:
        out = {
            "schemaVersion": 2,
            "examId": EXAM_ID,
            "examTitle": exam["title"],
            "generatedAt": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
            "questions": {},
        }
    out["schemaVersion"] = max(2, int(out.get("schemaVersion") or 0))
    out["examId"] = EXAM_ID
    out["examTitle"] = exam["title"]
    qs = out.setdefault("questions", {})

    for i in range(60):
        n = i + 1
        q = qs.setdefault(str(n), {})
        q["answer"] = int(exam["key"][i])
        q["acceptableAnswers"] = [int(exam["key"][i])]
        q["excluded"] = False
        q["concept"] = exam["type"][i]
        q["area"] = exam["area"][i]
        q["learningPoint"] = exam["type"][i]
        q.setdefault("explanation", "")
        q.setdefault("explanationHtml", "")
        q.setdefault("misconception", "")
        q.setdefault("sourceSolution", "")
        q.setdefault("verificationStatus", "verified_key_and_metadata")

    path.write_text(json.dumps(out, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def main() -> int:
    exam = patch_exams()
    patch_pages()
    sync_answer_metadata(exam)
    print("PASS USNCO 2026 National Part I 리포트 통합 패치 적용 · 기존 상세 해설 보존")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
