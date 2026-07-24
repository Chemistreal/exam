#!/usr/bin/env python3
"""Build and audit wrong-answer review assets for final.html.

The source PDFs in this repository use a consistent grey vector rectangle for
each "문제 N" label.  This script uses those vector rectangles rather than OCR
to locate question boundaries, renders one optimized PNG per question, extracts
verified solution HTML from the existing long-form solution pages, and maps
every question to a different solved question that tests the closest available
concept.

No external API or model call is used at report-render time.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import shutil
import sys
from collections import Counter, defaultdict
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable

import fitz
import numpy as np
from PIL import Image
from lxml import html


ROOT = Path(__file__).resolve().parents[1]
FINAL_HTML = ROOT / "final.html"
ANSWER_DIR = ROOT / "answers"
CROP_DIR = ROOT / "crops"
DONGHYUNG_DIR = ROOT / "donghyung"
REPORT_DIR = ROOT / "reports"

CIRCLED_TO_INT = {"①": 1, "②": 2, "③": 3, "④": 4, "⑤": 5}
INT_TO_CIRCLED = {v: k for k, v in CIRCLED_TO_INT.items()}


@dataclass(frozen=True)
class Header:
    page_index: int
    rect: fitz.Rect


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def read_exams() -> list[dict[str, Any]]:
    source = FINAL_HTML.read_text(encoding="utf-8")
    marker = "const FINAL_EXAMS="
    if marker not in source:
        raise RuntimeError("FINAL_EXAMS was not found in final.html")
    raw = source.split(marker, 1)[1].split(";\n", 1)[0]
    exams = json.loads(raw)
    if not isinstance(exams, list) or not exams:
        raise RuntimeError("FINAL_EXAMS is empty or malformed")
    return exams


def normalize(value: str | None) -> str:
    if not value:
        return ""
    return re.sub(r"[^0-9a-z가-힣]+", "", value.lower())


def tokens(value: str | None) -> set[str]:
    if not value:
        return set()
    return {
        normalize(token)
        for token in re.split(r"[\s,·()/\-→=]+", value)
        if normalize(token)
    }


DOMAIN_KEYWORDS = {
    "acid_base": (
        "산염기",
        "산과염기",
        "산의세기",
        "염의액성",
        "완충",
        "중화",
        "적정",
        "ph",
        "pka",
        "pkb",
        "ka",
        "kb",
        "주화학종",
        "다양성자산",
    ),
    "atomic": ("원자", "전자", "오비탈", "양자", "주기율", "이온화에너지"),
    "bonding": ("결합", "분자구조", "분자의모양", "극성", "루이스"),
    "stoichiometry": ("몰", "화학량론", "양적관계", "반응식", "원소분석"),
    "gas_solution": ("기체", "용액", "농도", "용해도", "삼투", "증기압"),
    "equilibrium": ("평형", "반응지수", "르샤틀리에"),
    "redox": ("산화환원", "전지", "전기분해", "산화수"),
    "thermo_kinetics": ("열화학", "엔탈피", "엔트로피", "깁스", "반응속도"),
}


def domain_family(*values: str | None) -> str:
    merged = normalize(" ".join(value or "" for value in values))
    for family, keywords in DOMAIN_KEYWORDS.items():
        if any(normalize(keyword) in merged for keyword in keywords):
            return family
    return ""


def inner_html(node: Any) -> str:
    if node is None:
        return ""
    parts: list[str] = []
    if node.text:
        parts.append(node.text)
    for child in node:
        parts.append(html.tostring(child, encoding="unicode", method="html"))
    return "".join(parts).strip()


def text_of(node: Any) -> str:
    if node is None:
        return ""
    return re.sub(r"\s+", " ", node.text_content()).strip()


def answer_number(text: str) -> int:
    for symbol, value in CIRCLED_TO_INT.items():
        if symbol in text:
            return value
    match = re.search(r"정답\s*([1-5])", text)
    return int(match.group(1)) if match else 0


def class_nodes(node: Any, tag: str, class_name: str) -> list[Any]:
    return node.xpath(
        f'.//{tag}[contains(concat(" ", normalize-space(@class), " "), '
        f'" {class_name} ")]'
    )


def parse_solution_page(path: Path) -> dict[int, dict[str, Any]]:
    document = html.fromstring(path.read_text(encoding="utf-8"))
    result: dict[int, dict[str, Any]] = {}
    for card in class_nodes(document, "div", "q"):
        qno = class_nodes(card, "span", "qno")
        if not qno:
            continue
        match = re.search(r"(\d+)", text_of(qno[0]))
        if not match:
            continue
        number = int(match.group(1))
        area_node = class_nodes(card, "*", "area")
        ans_node = class_nodes(card, "*", "ans")
        stem_node = class_nodes(card, "*", "stem")
        opts_node = class_nodes(card, "*", "opts")
        sol_node = class_nodes(card, "*", "sol")
        tip_node = class_nodes(card, "*", "tip")
        option_analyses: dict[str, str] = {}
        if sol_node:
            for paragraph in sol_node[0].xpath(".//p"):
                paragraph_text = text_of(paragraph)
                matches = list(re.finditer(r"[①②③④⑤]", paragraph_text))
                for idx, option_match in enumerate(matches):
                    end = (
                        matches[idx + 1].start()
                        if idx + 1 < len(matches)
                        else len(paragraph_text)
                    )
                    option = str(CIRCLED_TO_INT[option_match.group(0)])
                    analysis = paragraph_text[option_match.start() : end].strip()
                    if len(analysis) > 2:
                        option_analyses.setdefault(option, analysis)
        choices: list[str] = []
        choice_html: list[str] = []
        if opts_node:
            for option in opts_node[0].getchildren():
                choices.append(re.sub(r"^[①②③④⑤]\s*", "", text_of(option)))
                choice_html.append(
                    re.sub(
                        r"^[①②③④⑤]\s*",
                        "",
                        inner_html(option),
                    )
                )
        result[number] = {
            "areaLabel": text_of(area_node[0]) if area_node else "",
            "answer": answer_number(text_of(ans_node[0])) if ans_node else 0,
            "stem": text_of(stem_node[0]) if stem_node else "",
            "stemHtml": inner_html(stem_node[0]) if stem_node else "",
            "choices": choices,
            "choicesHtml": choice_html,
            "explanation": text_of(sol_node[0]) if sol_node else "",
            "explanationHtml": inner_html(sol_node[0]) if sol_node else "",
            "misconception": text_of(tip_node[0]) if tip_node else "",
            "optionAnalyses": option_analyses,
        }
    return result


def solution_catalog(
    exams: list[dict[str, Any]],
) -> tuple[
    dict[str, dict[int, dict[str, Any]]],
    dict[str, str],
    list[dict[str, Any]],
]:
    by_exam: dict[str, dict[int, dict[str, Any]]] = {}
    solution_files: dict[str, str] = {}
    exam_by_id = {exam["id"]: exam for exam in exams}

    for path in sorted(ROOT.glob("sol-final-*.html")):
        exam_id = path.stem.removeprefix("sol-final-")
        if exam_id not in exam_by_id:
            continue
        parsed = parse_solution_page(path)
        if len(parsed) >= exam_by_id[exam_id]["nQ"]:
            by_exam[exam_id] = parsed
            solution_files[exam_id] = path.name

    # Some menu entries intentionally point to the same PDF under two IDs.
    ids_by_pdf: dict[str, list[str]] = defaultdict(list)
    for exam in exams:
        ids_by_pdf[exam["pdf"]].append(exam["id"])
    for ids in ids_by_pdf.values():
        solved = next((item for item in ids if item in by_exam), None)
        if solved:
            for item in ids:
                if item not in by_exam:
                    by_exam[item] = by_exam[solved]
                    solution_files[item] = solution_files[solved]

    candidates: list[dict[str, Any]] = []
    for exam_id, questions in by_exam.items():
        exam = exam_by_id[exam_id]
        for number, solution in questions.items():
            if number > exam["nQ"]:
                continue
            key = int(exam.get("key", [0] * exam["nQ"])[number - 1] or 0)
            if key not in (1, 2, 3, 4):
                continue
            if number in set(exam.get("miss") or []):
                continue
            area = (exam.get("area") or [""] * exam["nQ"])[number - 1]
            qtype = (exam.get("type") or [""] * exam["nQ"])[number - 1]
            candidates.append(
                {
                    "examId": exam_id,
                    "examTitle": exam["title"],
                    "pdf": exam["pdf"],
                    "question": number,
                    "area": area,
                    "type": qtype,
                    **solution,
                    # FINAL_EXAMS is the canonical, verified answer source.
                    # Some legacy long-form pages omit the visible answer badge.
                    "answer": key,
                }
            )
    if not candidates:
        raise RuntimeError("No long-form solved questions were found")
    return by_exam, solution_files, candidates


def question_headers(document: fitz.Document, expected: int) -> list[Header]:
    headers: list[Header] = []
    for page_index, page in enumerate(document):
        for drawing in page.get_drawings():
            rect = drawing["rect"]
            fill = drawing.get("fill")
            if not fill:
                continue
            if not (
                60 < rect.width < 85
                and 15 < rect.height < 25
                and 60 < rect.x0 < 110
                and all(0.74 < channel < 0.85 for channel in fill)
            ):
                continue
            headers.append(Header(page_index=page_index, rect=fitz.Rect(rect)))
    headers.sort(key=lambda item: (item.page_index, item.rect.y0))
    if len(headers) < expected:
        raise RuntimeError(
            f"Only {len(headers)} question headers found; expected {expected}"
        )
    return headers[:expected]


def remove_red_answer_marker(
    image: Image.Image,
    clip: fitz.Rect,
    header: fitz.Rect,
    scale: float,
) -> tuple[Image.Image, bool]:
    rgb = np.asarray(image.convert("RGB")).copy()
    x0 = max(0, round((header.x1 - clip.x0 - 2) * scale))
    x1 = min(rgb.shape[1], round((header.x1 - clip.x0 + 42) * scale))
    y0 = max(0, round((header.y0 - clip.y0 - 5) * scale))
    y1 = min(rgb.shape[0], round((header.y1 - clip.y0 + 6) * scale))
    if x1 <= x0 or y1 <= y0:
        return image, False
    region = rgb[y0:y1, x0:x1]
    red = (
        (region[..., 0] > 130)
        & (region[..., 0] > region[..., 1] * 1.25)
        & (region[..., 0] > region[..., 2] * 1.25)
    )
    changed = bool(red.any())
    if changed:
        region[red] = 255
        rgb[y0:y1, x0:x1] = region
    return Image.fromarray(rgb, mode="RGB"), changed


def trim_bottom(image: Image.Image, padding: int = 20) -> Image.Image:
    rgb = np.asarray(image.convert("RGB"))
    ink = np.min(rgb, axis=2) < 249
    row_counts = ink.sum(axis=1)
    rows = np.where(row_counts >= 4)[0]
    if not len(rows):
        return image
    bottom = min(image.height, int(rows[-1]) + padding + 1)
    bottom = max(bottom, min(image.height, 120))
    return image.crop((0, 0, image.width, bottom))


def optimize_png(image: Image.Image, output: Path) -> dict[str, Any]:
    image = trim_bottom(image)
    if image.width > 960:
        height = round(image.height * 960 / image.width)
        image = image.resize((960, height), Image.Resampling.LANCZOS)
    rgb = np.asarray(image.convert("RGB"))
    nonwhite = np.min(rgb, axis=2) < 249
    chroma = np.max(rgb, axis=2) - np.min(rgb, axis=2)
    color_fraction = (
        float(((chroma > 16) & nonwhite).sum()) / max(1, int(nonwhite.sum()))
    )
    if color_fraction > 0.008:
        final = image.convert("P", palette=Image.Palette.ADAPTIVE, colors=64)
        color_mode = "palette"
    else:
        final = image.convert("L")
        color_mode = "grayscale"
    output.parent.mkdir(parents=True, exist_ok=True)
    temporary = output.with_name(f"{output.name}.{os.getpid()}.tmp")
    final.save(temporary, "PNG", optimize=True, compress_level=9)
    temporary.replace(output)
    payload = output.read_bytes()
    return {
        "width": final.width,
        "height": final.height,
        "bytes": len(payload),
        "sha256": hashlib.sha256(payload).hexdigest(),
        "colorMode": color_mode,
    }


def crop_exam(exam: dict[str, Any], force: bool = False) -> list[dict[str, Any]]:
    pdf_path = ROOT / exam["pdf"]
    if not pdf_path.exists():
        raise FileNotFoundError(pdf_path)
    document = fitz.open(pdf_path)
    headers = question_headers(document, exam["nQ"])
    results: list[dict[str, Any]] = []
    scale = 2.0
    matrix = fitz.Matrix(scale, scale)
    for index, header in enumerate(headers):
        number = index + 1
        next_header = headers[index + 1] if index + 1 < len(headers) else None
        page = document[header.page_index]
        x0 = max(0.0, min(header.rect.x0 - 10.0, 60.0))
        x1 = min(page.rect.width, page.rect.width - 58.0)
        y0 = max(0.0, header.rect.y0 - 8.0)
        if next_header and next_header.page_index == header.page_index:
            y1 = max(y0 + 45.0, next_header.rect.y0 - 8.0)
        else:
            y1 = min(page.rect.height - 65.0, 775.0)
        clip = fitz.Rect(x0, y0, x1, y1)
        output = CROP_DIR / exam["id"] / f"{number}.png"
        marker_removed = False
        if force or not output.exists():
            pixmap = page.get_pixmap(matrix=matrix, clip=clip, alpha=False)
            image = Image.frombytes("RGB", [pixmap.width, pixmap.height], pixmap.samples)
            image, marker_removed = remove_red_answer_marker(
                image, clip, header.rect, scale
            )
            info = optimize_png(image, output)
        else:
            with Image.open(output) as existing:
                width, height = existing.size
            payload = output.read_bytes()
            info = {
                "width": width,
                "height": height,
                "bytes": len(payload),
                "sha256": hashlib.sha256(payload).hexdigest(),
                "colorMode": "existing",
            }
        results.append(
            {
                "question": number,
                "path": output.relative_to(ROOT).as_posix(),
                "page": header.page_index + 1,
                "sourceBox": [
                    round(clip.x0, 2),
                    round(clip.y0, 2),
                    round(clip.x1, 2),
                    round(clip.y1, 2),
                ],
                "redAnswerMarkerRemoved": marker_removed,
                **info,
            }
        )
    document.close()
    return results


def candidate_score(
    source: dict[str, Any],
    candidate: dict[str, Any],
) -> tuple[int, str]:
    source_type = normalize(source.get("type"))
    source_area = normalize(source.get("area"))
    candidate_type = normalize(candidate.get("type"))
    candidate_area = normalize(candidate.get("area"))
    label = normalize(candidate.get("areaLabel"))
    score = 0
    level = "broad_area"
    if source_area and source_area == candidate_area:
        score += 80
        level = "exact_area"
    if source_type and candidate_type and source_type == candidate_type:
        score += 140
        level = "exact_type"
    if source_type and label and (source_type in label or label in source_type):
        score += 75
        if level == "broad_area":
            level = "solution_label"
    overlap = len(
        (tokens(source.get("type")) | tokens(source.get("area")))
        & (
            tokens(candidate.get("type"))
            | tokens(candidate.get("area"))
            | tokens(candidate.get("areaLabel"))
        )
    )
    score += overlap * 8
    source_family = domain_family(source.get("type"), source.get("area"))
    candidate_family = domain_family(
        candidate.get("type"),
        candidate.get("area"),
        candidate.get("areaLabel"),
    )
    if source_family and source_family == candidate_family:
        score += 40
        if level == "broad_area":
            level = "domain_family"
    return score, level


def source_question(exam: dict[str, Any], number: int) -> dict[str, Any]:
    area = (exam.get("area") or [""] * exam["nQ"])[number - 1]
    qtype = (exam.get("type") or [""] * exam["nQ"])[number - 1]
    return {
        "examId": exam["id"],
        "examTitle": exam["title"],
        "pdf": exam["pdf"],
        "question": number,
        "area": area,
        "type": qtype,
    }


def choose_analogue(
    source: dict[str, Any],
    candidates: list[dict[str, Any]],
    usage: Counter[tuple[str, int]],
) -> tuple[dict[str, Any], int, str]:
    scored: list[tuple[int, str, int, dict[str, Any]]] = []
    for candidate in candidates:
        if candidate["pdf"] == source["pdf"]:
            continue
        score, level = candidate_score(source, candidate)
        key = (candidate["examId"], candidate["question"])
        scored.append((score, level, usage[key], candidate))
    if not scored:
        raise RuntimeError(f"No analogue candidate for {source}")
    max_score = max(item[0] for item in scored)
    near = [item for item in scored if item[0] >= max_score - 8]
    near.sort(
        key=lambda item: (
            item[2],
            -item[0],
            item[3]["examId"],
            item[3]["question"],
        )
    )
    score, level, _, selected = near[0]
    usage[(selected["examId"], selected["question"])] += 1
    return selected, score, level


def misconception_map(
    answer: int,
    tip: str,
    option_analyses: dict[str, str],
    choice_count: int,
    explanation: str,
    choices: list[str],
) -> dict[str, str]:
    result: dict[str, str] = {}
    for option in range(1, min(5, max(4, choice_count)) + 1):
        if option == answer:
            continue
        specific = option_analyses.get(str(option), "")
        if specific:
            result[str(option)] = (
                f"{INT_TO_CIRCLED[option]} 선택지 검토: {specific}"
                + (f" 점검 기준: {tip}" if tip else "")
            )
        elif tip:
            result[str(option)] = (
                f"{INT_TO_CIRCLED[option]}을 선택했다면 다음 함정을 우선 "
                f"점검하세요. {tip}"
            )
        elif explanation:
            choice = choices[option - 1] if option <= len(choices) else ""
            result[str(option)] = (
                f"{INT_TO_CIRCLED[option]}"
                + (f" 보기({choice})" if choice else " 보기")
                + "를 선택했다면 각 조건의 참·거짓을 검증된 풀이와 다시 "
                f"대조하세요. {explanation}"
            )
    return result


def build_answer_files(
    exams: list[dict[str, Any]],
    solved: dict[str, dict[int, dict[str, Any]]],
    solution_files: dict[str, str],
) -> dict[str, Any]:
    ANSWER_DIR.mkdir(parents=True, exist_ok=True)
    exact = 0
    fallback = 0
    fallback_questions: list[dict[str, Any]] = []
    for exam in exams:
        questions: dict[str, Any] = {}
        solution_data = solved.get(exam["id"], {})
        miss = set(exam.get("miss") or [])
        for number in range(1, exam["nQ"] + 1):
            key = int((exam.get("key") or [0] * exam["nQ"])[number - 1] or 0)
            multi = [int(x) for x in (exam.get("multi") or {}).get(str(number), [])]
            area = (exam.get("area") or [""] * exam["nQ"])[number - 1]
            qtype = (exam.get("type") or [""] * exam["nQ"])[number - 1]
            verified = solution_data.get(number)
            if verified:
                exact += 1
                explanation = verified
                status = "verified_long_form"
            else:
                fallback += 1
                fallback_questions.append(
                    {
                        "examId": exam["id"],
                        "examTitle": exam["title"],
                        "question": number,
                        "available": "answer_key_and_concept_only",
                    }
                )
                explanation = {}
                status = "answer_key_and_concept_only"
            questions[str(number)] = {
                "answer": key,
                "acceptableAnswers": multi or ([key] if key else []),
                "excluded": number in miss,
                "concept": qtype or area,
                "area": area,
                "learningPoint": (
                    verified.get("areaLabel") if verified else (qtype or area)
                ),
                "explanation": explanation.get("explanation", ""),
                "explanationHtml": explanation.get("explanationHtml", ""),
                "misconception": explanation.get("misconception", ""),
                "sourceSolution": solution_files.get(exam["id"], ""),
                "verificationStatus": status,
            }
        payload = {
            "schemaVersion": 2,
            "examId": exam["id"],
            "examTitle": exam["title"],
            "generatedAt": utc_now(),
            "questions": questions,
        }
        (ANSWER_DIR / f"{exam['id']}.json").write_text(
            json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
    return {
        "exactLongForm": exact,
        "conceptFallback": fallback,
        "fallbackQuestions": fallback_questions,
    }


def build_donghyung_files(
    exams: list[dict[str, Any]],
    candidates: list[dict[str, Any]],
) -> dict[str, Any]:
    DONGHYUNG_DIR.mkdir(parents=True, exist_ok=True)
    usage: Counter[tuple[str, int]] = Counter()
    levels: Counter[str] = Counter()
    score_min = 10**9
    for exam in exams:
        questions: dict[str, Any] = {}
        for number in range(1, exam["nQ"] + 1):
            source = source_question(exam, number)
            target, score, level = choose_analogue(source, candidates, usage)
            levels[level] += 1
            score_min = min(score_min, score)
            questions[str(number)] = {
                "concept": source["type"] or source["area"],
                "area": source["area"],
                "difficulty": "원문과 유사한 화학올림피아드·중학생화학대회 수준",
                "sourceExamId": target["examId"],
                "sourceExamTitle": target["examTitle"],
                "sourceQuestion": target["question"],
                "image": f"crops/{target['examId']}/{target['question']}.png",
                "stem": target.get("stem", ""),
                "stemHtml": target.get("stemHtml", ""),
                "choices": target.get("choices", []),
                "choicesHtml": target.get("choicesHtml", []),
                "answer": target["answer"],
                "explanation": target.get("explanation", ""),
                "explanationHtml": target.get("explanationHtml", ""),
                "misconception": target.get("misconception", ""),
                "misconceptions": misconception_map(
                    target["answer"],
                    target.get("misconception", ""),
                    target.get("optionAnalyses", {}),
                    len(target.get("choices", [])),
                    target.get("explanation", ""),
                    target.get("choices", []),
                ),
                "learningPoint": target.get("areaLabel")
                or target.get("type")
                or target.get("area"),
                "matchLevel": level,
                "matchScore": score,
                "verified": True,
            }
        payload = {
            "schemaVersion": 2,
            "examId": exam["id"],
            "examTitle": exam["title"],
            "generatedAt": utc_now(),
            "strategy": (
                "다른 시험의 장문 해설 검증 완료 문항 중 동일 개념·영역을 "
                "우선 매칭한 재학습용 동형문제"
            ),
            "questions": questions,
        }
        (DONGHYUNG_DIR / f"{exam['id']}.json").write_text(
            json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
    return {
        "questions": sum(levels.values()),
        "matchLevels": dict(levels),
        "minimumMatchScore": score_min if levels else None,
        "uniqueTargets": len(usage),
        "maximumTargetReuse": max(usage.values()) if usage else 0,
    }


def validate_assets(exams: list[dict[str, Any]]) -> dict[str, Any]:
    problems: list[dict[str, Any]] = []
    crop_count = 0
    crop_bytes = 0
    answer_count = 0
    analogue_count = 0
    for exam in exams:
        for number in range(1, exam["nQ"] + 1):
            path = CROP_DIR / exam["id"] / f"{number}.png"
            if not path.exists():
                problems.append(
                    {
                        "examId": exam["id"],
                        "question": number,
                        "kind": "missing_crop",
                    }
                )
                continue
            try:
                with Image.open(path) as image:
                    width, height = image.size
                    image.verify()
                if width < 760 or height < 80:
                    problems.append(
                        {
                            "examId": exam["id"],
                            "question": number,
                            "kind": "invalid_crop_dimensions",
                            "width": width,
                            "height": height,
                        }
                    )
                crop_count += 1
                crop_bytes += path.stat().st_size
            except Exception as exc:
                problems.append(
                    {
                        "examId": exam["id"],
                        "question": number,
                        "kind": "unreadable_crop",
                        "message": str(exc),
                    }
                )
        answer_path = ANSWER_DIR / f"{exam['id']}.json"
        analogue_path = DONGHYUNG_DIR / f"{exam['id']}.json"
        for kind, path in (
            ("answers", answer_path),
            ("donghyung", analogue_path),
        ):
            if not path.exists():
                problems.append({"examId": exam["id"], "kind": f"missing_{kind}"})
                continue
            try:
                data = json.loads(path.read_text(encoding="utf-8"))
                questions = data.get("questions") or {}
                if len(questions) != exam["nQ"]:
                    problems.append(
                        {
                            "examId": exam["id"],
                            "kind": f"{kind}_question_count",
                            "expected": exam["nQ"],
                            "actual": len(questions),
                        }
                    )
                if kind == "answers":
                    answer_count += len(questions)
                else:
                    analogue_count += len(questions)
                    for number, question in questions.items():
                        target_image = ROOT / question.get("image", "")
                        if not target_image.exists():
                            problems.append(
                                {
                                    "examId": exam["id"],
                                    "question": int(number),
                                    "kind": "missing_analogue_crop",
                                    "path": question.get("image", ""),
                                }
                            )
                        answer = int(question.get("answer") or 0)
                        if answer not in (1, 2, 3, 4):
                            problems.append(
                                {
                                    "examId": exam["id"],
                                    "question": int(number),
                                    "kind": "invalid_analogue_answer",
                                    "answer": answer,
                                }
                            )
                        if not question.get("explanationHtml"):
                            problems.append(
                                {
                                    "examId": exam["id"],
                                    "question": int(number),
                                    "kind": "missing_analogue_explanation",
                                }
                            )
                        misconceptions = question.get("misconceptions") or {}
                        missing_options = [
                            option
                            for option in range(1, 5)
                            if option != answer and str(option) not in misconceptions
                        ]
                        if missing_options:
                            problems.append(
                                {
                                    "examId": exam["id"],
                                    "question": int(number),
                                    "kind": "missing_analogue_misconceptions",
                                    "options": missing_options,
                                }
                            )
            except Exception as exc:
                problems.append(
                    {
                        "examId": exam["id"],
                        "kind": f"invalid_{kind}_json",
                        "message": str(exc),
                    }
                )
    return {
        "examCount": len(exams),
        "expectedQuestionCount": sum(exam["nQ"] for exam in exams),
        "cropCount": crop_count,
        "cropBytes": crop_bytes,
        "answerCount": answer_count,
        "analogueCount": analogue_count,
        "problemCount": len(problems),
        "problems": problems,
    }


def write_report(payload: dict[str, Any]) -> None:
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    target = REPORT_DIR / "wrongbook-asset-audit.json"
    target.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--exams",
        help="Comma-separated exam IDs. Default: all FINAL_EXAMS.",
    )
    parser.add_argument("--skip-crops", action="store_true")
    parser.add_argument("--force-crops", action="store_true")
    parser.add_argument("--validate-only", action="store_true")
    parser.add_argument("--clean-generated", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    all_exams = read_exams()
    selected_ids = (
        {item.strip() for item in args.exams.split(",") if item.strip()}
        if args.exams
        else None
    )
    exams = (
        [exam for exam in all_exams if exam["id"] in selected_ids]
        if selected_ids
        else all_exams
    )
    if selected_ids:
        missing = selected_ids - {exam["id"] for exam in exams}
        if missing:
            raise RuntimeError(f"Unknown exam IDs: {sorted(missing)}")

    if args.clean_generated:
        for directory in (ANSWER_DIR, CROP_DIR, DONGHYUNG_DIR, REPORT_DIR):
            if directory.exists():
                for child in directory.iterdir():
                    if child.name.startswith("_") or child.name == "README.md":
                        continue
                    if child.is_dir():
                        shutil.rmtree(child)
                    else:
                        child.unlink()

    if args.validate_only:
        audit = {
            "schemaVersion": 1,
            "generatedAt": utc_now(),
            "validation": validate_assets(all_exams),
        }
        validation = audit["validation"]
        print(
            "validation "
            f"exams={validation['examCount']} "
            f"questions={validation['expectedQuestionCount']} "
            f"crops={validation['cropCount']} "
            f"answers={validation['answerCount']} "
            f"analogues={validation['analogueCount']} "
            f"problems={validation['problemCount']}"
        )
        return 1 if audit["validation"]["problemCount"] else 0

    crop_records: dict[str, list[dict[str, Any]]] = {}
    if not args.skip_crops:
        for index, exam in enumerate(exams, 1):
            crop_records[exam["id"]] = crop_exam(exam, force=args.force_crops)
            print(
                f"[crops {index:02d}/{len(exams):02d}] "
                f"{exam['id']} {len(crop_records[exam['id']])}/{exam['nQ']}",
                flush=True,
            )

    solved, solution_files, candidates = solution_catalog(all_exams)
    answer_stats = build_answer_files(all_exams, solved, solution_files)
    analogue_stats = build_donghyung_files(all_exams, candidates)
    validation = validate_assets(all_exams)
    audit = {
        "schemaVersion": 1,
        "generatedAt": utc_now(),
        "source": "final.html FINAL_EXAMS and repository problem/solution files",
        "solutionCandidateCount": len(candidates),
        "sourceExplanationCoverage": answer_stats,
        "analogueCoverage": analogue_stats,
        "cropBuild": {
            "examCountBuiltThisRun": len(crop_records),
            "questionCountBuiltThisRun": sum(
                len(items) for items in crop_records.values()
            ),
            "redAnswerMarkersRemoved": sum(
                int(item["redAnswerMarkerRemoved"])
                for items in crop_records.values()
                for item in items
            ),
        },
        "validation": validation,
    }
    write_report(audit)
    print(
        "audit "
        f"questions={validation['expectedQuestionCount']} "
        f"crops={validation['cropCount']} "
        f"answers={validation['answerCount']} "
        f"analogues={validation['analogueCount']} "
        f"problems={validation['problemCount']} "
        f"report={REPORT_DIR.relative_to(ROOT).as_posix()}/wrongbook-asset-audit.json"
    )
    return 1 if validation["problemCount"] else 0


if __name__ == "__main__":
    sys.exit(main())
