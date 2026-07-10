#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DT 단원 표기 통일 패치 (같은 과목 내 드리프트 7건)
- appdata 디렉터리의 모든 round_*.json 을 훑어, (진술 + 현재 단원 + 개념코드)가
  아래 PLAN 과 일치하는 본 문항의 u(단원) 필드만 표준 단원으로 바꾼다.
- 진술/정답(a)/코드(c)/기타 필드는 절대 건드리지 않는다.
- 기본은 dry-run(미리보기). 실제 적용은 --apply.
- 과목 경계를 넘는 63건(화학I/화학II/일반화학 공통 개념)은 정상 설계이므로 대상 아님.

사용법:
  python3 unit_unify.py --appdata ./appdata            # 미리보기
  python3 unit_unify.py --appdata ./appdata --apply     # 실제 적용(백업 .bak 생성)

동점 3건은 표준을 권고로 넣었다(TIE 표시). 다른 단원으로 하고 싶으면
아래 PLAN 에서 'to' 값만 바꾸면 된다.
"""
import argparse, glob, json, os, sys

def norm(s):
    return ''.join((s or '').split())

# (code, 정규화 진술, from_unit) -> to_unit
# TIE = 동점이라 출제자 판단 사항(권고값 사용)
PLAN = [
    # 명확(진술 다수결): 원자·동위원소 개념을 원자 구조 단원으로 통일
    {"code": "CH1-009", "stmt": "중성자는 전하를 띠지 않는다.",              "from": "Ⅰ-1", "to": "Ⅱ-1", "tie": False},
    {"code": "CH1-037", "stmt": "동위원소는 화학적 성질이 서로 다르다.",     "from": "Ⅰ-3", "to": "Ⅱ-1", "tie": False},
    {"code": "CH1-037", "stmt": "동위원소는 중성자수가 서로 다르다.",        "from": "Ⅰ-3", "to": "Ⅱ-1", "tie": False},
    {"code": "CH1-037", "stmt": "동위원소는 양성자수가 서로 다르다.",        "from": "Ⅰ-3", "to": "Ⅱ-1", "tie": False},
    # 동점(권고): 개념상 홈으로
    {"code": "CH1-007", "stmt": "원자핵은 양성자와 중성자로 이루어진다.",    "from": "Ⅰ-1", "to": "Ⅱ-1", "tie": True},
    {"code": "CH1-059", "stmt": "H₂O에서 수소와 산소의 질량비는 8:1이다.",   "from": "부록", "to": "Ⅰ-4", "tie": True},
    {"code": "CH2-113", "stmt": "몰분율은 그 성분의 몰수를 전체 몰수로 나눈 값이다.", "from": "분압", "to": "농도", "tie": True},
]

def build_index():
    idx = {}
    for p in PLAN:
        idx[(p["code"], norm(p["stmt"]), p["from"])] = p
    return idx

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--appdata", required=True, help="round_*.json 이 있는 디렉터리")
    ap.add_argument("--apply", action="store_true", help="실제 파일 수정(미지정 시 미리보기)")
    args = ap.parse_args()

    files = sorted(glob.glob(os.path.join(args.appdata, "round_*.json")))
    if not files:
        print("round_*.json 을 찾지 못했습니다: " + args.appdata)
        sys.exit(1)

    idx = build_index()
    expected = len(PLAN)
    applied = []
    per_file_changes = {}

    for fp in files:
        try:
            data = json.load(open(fp, encoding="utf-8"))
        except Exception as e:
            print("건너뜀(파싱 실패): " + fp + " -> " + str(e))
            continue
        items = (data.get("jeongsi") or {}).get("items") or []
        changed = 0
        for it in items:
            key = (it.get("c"), norm(it.get("s")), it.get("u"))
            hit = idx.get(key)
            if hit:
                # assert: 정답/코드/진술은 그대로여야 한다(안전 확인)
                if it.get("u") != hit["from"]:
                    continue
                it["u"] = hit["to"]
                changed += 1
                applied.append({"file": os.path.basename(fp), "code": hit["code"],
                                "stmt": hit["stmt"], "from": hit["from"], "to": hit["to"],
                                "tie": hit["tie"]})
        if changed:
            per_file_changes[fp] = (data, changed)

    # 리포트
    print("=== 단원 통일 " + ("적용" if args.apply else "미리보기") + " ===")
    for a in applied:
        tag = " [TIE 권고]" if a["tie"] else ""
        print("  " + a["file"] + ": '" + a["from"] + "' -> '" + a["to"] + "'" + tag)
        print("       [" + a["code"] + "] " + a["stmt"][:44])

    n = len(applied)
    print("\n적용 대상 문항: " + str(n) + " (예상 " + str(expected) + ")")
    if n != expected:
        print("경고: 적용 수가 예상과 다릅니다. appdata 경로/버전을 확인하세요. (파일 미수정)")
        sys.exit(2)

    # em-dash 방어(변경한 값에 대시류가 섞이지 않았는지)
    bad = [a for a in applied if any(ch in (a["to"]) for ch in "\u2013\u2014\u2015")]
    if bad:
        print("경고: to 값에 대시류 문자가 있습니다. 중단.")
        sys.exit(3)

    if not args.apply:
        print("\n(미리보기) 실제로 바꾸려면 --apply 를 붙여 다시 실행하세요.")
        return

    # 적용: 백업 후 저장
    for fp, (data, changed) in per_file_changes.items():
        bak = fp + ".bak"
        if not os.path.exists(bak):
            with open(bak, "w", encoding="utf-8") as f:
                json.dump(json.load(open(fp, encoding="utf-8")), f, ensure_ascii=False, indent=1)
        with open(fp, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=1)
        print("저장: " + os.path.basename(fp) + " (" + str(changed) + "건, 백업 .bak)")
    print("\n완료. 배포 전 라운드 파일을 재확인하고 GitHub Pages 에 반영하세요.")

if __name__ == "__main__":
    main()
