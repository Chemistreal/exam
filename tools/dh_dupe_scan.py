#!/usr/bin/env python3
"""서로 같은 문항이 된 쌍을 찾는다. 한 시험 안에서도, 시험끼리도 본다.

**시험 안(기본).** 파트를 나눠 병렬로 집필하면 집필자끼리 상대 파트를 볼 수
없어서, 같은 개념이 두 파트에 배정됐을 때 사실상 같은 문항이 나온다. 실제로
donghyung-3 에서 2번과 31번(등전자 이온 반지름 순서), 28번과 39번(콕으로 연결한
두 용기 혼합)이 그렇게 겹쳤다. 병합 직후·검수 전에 한 번 돌린다.

**시험끼리(`--cross`).** 시험도 서로를 못 보고 집필된다. 한 개념에 교과서적으로
정해진 문항이 하나뿐이면 여러 시험이 같은 것을 쓴다. donghyung-4 23번과
jmchc-7 37번이 둘 다 꼭짓점·면심·체심에서 AB₃C를 세는 문항이었다. 오답노트는
시험별로 열리므로 시험 안 중복보다는 덜 급하지만, 수치까지 같은 것은 고친다.

지문의 문자 3-그램 자카드 유사도로 재고, 시험 안 검사에서는 concept 이 같은
쌍을 유사도와 무관하게 함께 보여 준다. 화학 문항은 숫자·물질명이 달라도 묻는
구조가 같으면 3-그램이 많이 겹친다.

다만 재는 것은 지문의 **겉모양**이다. "…에 대한 설명으로 옳은 것은?" 처럼
상투구를 공유하면 내용이 전혀 달라도 0.4~0.5가 나온다. 최종 판단은 사람이 한다.

**집필 중에 쓰려면 `--draft`.** 병합하기 전의 파트 JSON을 완료분 전체와 대조한다.
집필자가 스스로 돌려 보고 고치는 것이 검수자가 찾아 주는 것보다 훨씬 싸다.

사용:
    python3 tools/dh_dupe_scan.py <examId> [임계값]        # 한 시험 안
    python3 tools/dh_dupe_scan.py --cross [임계값]         # 재집필 완료분 전체 대조
    python3 tools/dh_dupe_scan.py --draft <파트.json> [임계값]  # 집필 중인 파트를 완료분과 대조
"""

from __future__ import annotations

import collections
import glob
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

# 수치·기호는 문항마다 당연히 다르므로 지우고 문장 뼈대만 비교한다.
NOISE = re.compile(r"[0-9.,()\[\]{}·×→⇌=<>+\-/％%\s]+")

# 이보다 많은 문항에 나오는 3-그램은 상투구로 보고 후보를 좁히는 데 쓰지 않는다.
# (유사도 계산에는 그대로 들어간다. 후보를 추리는 용도로만 무시한다.)
COMMON = 60


def trigrams(text: str) -> set[str]:
    flat = NOISE.sub("", text)
    return {flat[i : i + 3] for i in range(len(flat) - 2)}


def load(exam_id: str) -> dict:
    path = ROOT / "donghyung" / f"{exam_id}.json"
    return json.loads(path.read_text(encoding="utf-8"))


def authored_exams() -> list[str]:
    out = []
    for path in sorted(glob.glob(str(ROOT / "donghyung" / "*.json"))):
        data = json.loads(Path(path).read_text(encoding="utf-8"))
        if data.get("strategy") == "original-authored":
            out.append(data["examId"])
    return out


def scan_one(exam_id: str, threshold: float) -> None:
    questions = load(exam_id)["questions"]
    grams = {k: trigrams(v.get("stem", "")) for k, v in questions.items()}

    hits = []
    keys = sorted(questions, key=int)
    for i, a in enumerate(keys):
        for b in keys[i + 1 :]:
            union = grams[a] | grams[b]
            if not union:
                continue
            score = len(grams[a] & grams[b]) / len(union)
            same_concept = questions[a].get("concept") == questions[b].get("concept")
            if score >= threshold or same_concept:
                hits.append((score, a, b, same_concept))

    hits.sort(reverse=True)
    print(f"[{exam_id}] 검사 쌍 {len(keys) * (len(keys) - 1) // 2}개 · 후보 {len(hits)}개")
    for score, a, b, same_concept in hits:
        mark = "개념동일" if same_concept else "        "
        print(f"  {a:>2}–{b:<2} 유사도 {score:.2f} {mark}")
        for key in (a, b):
            head = questions[key].get("stem", "").splitlines()[0][:58]
            print(f"      {key:>2}[{questions[key].get('concept','')}] {head}")


def scan_cross(threshold: float) -> None:
    """모든 재집필본을 서로 대조한다.

    1700문항을 전부 짝지으면 150만 쌍이라 느리다. 흔한 3-그램은 후보를 좁히는 데
    쓰지 않고, 드문 3-그램을 하나라도 공유하는 쌍만 실제로 계산한다.
    """
    grams: dict[tuple[str, str], set[str]] = {}
    stems: dict[tuple[str, str], str] = {}
    concepts: dict[tuple[str, str], str] = {}
    for exam_id in authored_exams():
        for number, question in load(exam_id)["questions"].items():
            key = (exam_id, number)
            stem = question.get("stem", "")
            grams[key] = trigrams(stem)
            stems[key] = stem
            concepts[key] = question.get("concept", "")

    index: dict[str, list[tuple[str, str]]] = collections.defaultdict(list)
    for key, gs in grams.items():
        for gram in gs:
            index[gram].append(key)

    candidates: set[tuple] = set()
    for gram, keys in index.items():
        if len(keys) > COMMON:
            continue
        for i, a in enumerate(keys):
            for b in keys[i + 1 :]:
                if a[0] != b[0]:  # 시험 안 중복은 기본 모드가 본다
                    candidates.add((a, b) if a < b else (b, a))

    hits = []
    for a, b in candidates:
        union = grams[a] | grams[b]
        if not union:
            continue
        score = len(grams[a] & grams[b]) / len(union)
        if score >= threshold:
            hits.append((score, a, b))

    hits.sort(reverse=True)
    print(f"문항 {len(grams)}개 · 실제 비교 {len(candidates)}쌍 · 유사도 {threshold} 이상 {len(hits)}건")
    for score, a, b in hits:
        print(f"  {score:.2f}  {a[0]} {a[1]}  ↔  {b[0]} {b[1]}")
        for key in (a, b):
            print(f"      [{concepts[key]}] {stems[key].splitlines()[0][:66]}")


def scan_draft(path: str, threshold: float) -> None:
    """아직 병합하지 않은 파트 JSON을 재집필 완료분 전체와 대조한다."""
    draft = json.loads(Path(path).read_text(encoding="utf-8"))
    draft = draft.get("questions", draft)
    mine = {k: (trigrams(v.get("stem", "")), v.get("stem", "")) for k, v in draft.items()}

    # `<examId>.part1.json` 처럼 이름을 지으므로 앞부분이 시험 id 다. 이미 병합된
    # 자기 자신과 대조하면 전부 1.00 이 나오므로 뺀다.
    own = Path(path).name.split(".part")[0]

    hits = []
    for exam_id in authored_exams():
        if exam_id == own:
            continue
        for number, question in load(exam_id)["questions"].items():
            other = trigrams(question.get("stem", ""))
            for key, (gs, stem) in mine.items():
                union = gs | other
                if not union:
                    continue
                score = len(gs & other) / len(union)
                if score >= threshold:
                    hits.append((score, key, stem, exam_id, number, question.get("stem", "")))

    hits.sort(reverse=True)
    print(f"초안 {len(mine)}문항 · 완료분 대조 · 유사도 {threshold} 이상 {len(hits)}건")
    for score, key, stem, exam_id, number, other_stem in hits:
        print(f"  {score:.2f}  초안 {key}  ↔  {exam_id} {number}")
        print(f"      초안: {stem.splitlines()[0][:66]}")
        print(f"      기존: {other_stem.splitlines()[0][:66]}")
    if not hits:
        print("  겹치는 문항 없음. 다만 이 검사는 지문의 겉모양만 본다.")
        print("  수치와 소재가 같아도 문장을 다르게 쓰면 걸리지 않으므로,")
        print("  같은 개념을 다룬 기존 문항이 있는지는 직접 읽어 확인해야 한다.")


def main() -> None:
    args = sys.argv[1:]
    if not args:
        print(__doc__)
        raise SystemExit(1)
    if args[0] == "--cross":
        scan_cross(float(args[1]) if len(args) > 1 else 0.45)
    elif args[0] == "--draft":
        if len(args) < 2:
            print(__doc__)
            raise SystemExit(1)
        scan_draft(args[1], float(args[2]) if len(args) > 2 else 0.40)
    else:
        scan_one(args[0], float(args[1]) if len(args) > 1 else 0.30)


if __name__ == "__main__":
    try:
        main()
    except BrokenPipeError:  # `| head` 로 잘라 볼 때 역추적을 남기지 않는다
        pass
