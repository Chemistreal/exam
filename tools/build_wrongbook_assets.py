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
from dataclasses import dataclass, replace
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
    pre_page: int | None = None      # 묶음 문두가 있으면 그 쪽 번호
    pre_rect: fitz.Rect | None = None
    pre_y1: float | None = None      # 묶음 문두 자료가 끝나는 자리(그 묶음의 첫 문항)
    stop_page: int | None = None     # **다음 딱지**(문항이든 묶음 문두든)의 쪽
    stop_y: float | None = None      # 그 딱지의 윗변. 여기서 잘라야 한다


# 문항 두 개가 한 자료를 나눠 쓰는 자리. 문제지에는 '문제 22-23' 같은 회색
# 딱지가 자료 위에 하나 더 붙는다. 그 딱지도 문항 딱지와 생김새가 같아서,
# 세어 보면 문항 수보다 상자가 많다.
#
# 예전 코드는 상자를 앞에서부터 nQ 개만 잘라 썼다. 그러면 묶음 딱지가 문항
# 하나를 밀어내, **그 뒤로 모든 크롭이 한 칸씩 어긋났다**. 오답 카드에 엉뚱한
# 문제가 실렸다는 뜻이다. 일곱 회차가 그랬다.
#
# 딱지에 적힌 범위는 글자를 읽어야 알 수 있는데, 이 문제지들은 글자가 자모로
# 흩어져 있어 텍스트로는 안 잡힌다. 그래서 사람이 한 번 읽어 여기 적어 둔다.
# 표에 없는 묶음 딱지가 나오면 멈춘다 — 새 회차가 조용히 어긋나지 않도록.
GROUPED = {
    'jmchc-1': [(37, 38), (50, 51)],
    'jmchc-2': [(36, 37), (49, 50)],
    'donghyung-1': [(46, 47)],
    'hwol-2015': [(46, 47)],
    'hwol-2012': [(22, 23)],
    'hwol-2011': [(55, 56)],
    'hwol-2010': [(55, 56), (57, 58)],
}

# 문제지에 **잘못 박힌 딱지**. 회색 상자인데 문항 딱지가 아니다.
#
# 넓이로 가려지지 않는다(폭이 보통 딱지와 같다). 딱지 글자를 읽어야 아는데
# 이 문제지들은 글자가 자모로 흩어져 텍스트로 안 잡힌다. 그래서 사람이 한 번
# 읽어 여기 적어 둔다. 값은 **상자 차례**(1부터)다.
#
# [지금은 비어 있다] hwol-2018 에 `[26]` 이 적혀 있었다 — 스물여섯째 상자에
# '문제 52' 라고 적혀 있어 26번부터 크롭이 한 칸씩 밀렸다. 그런데 그것은
# **문제지가 아니라 해설편**이었다. `kmchc-2018-problem.pdf` 로 실려 있던
# 파일은 앞 네 쪽이 표지·주의사항, 다섯째 쪽이 **정답표 전체**, 그 뒤가
# 정답률과 답이 붙은 해설이었다(2026-08-10 에 드러났다). 크롭 예순 장이
# 전부 그 해설 쪽에서 잘려 나와 **학생이 답을 보고 있었다.**
#
# 선생님이 진짜 문제지를 주셔서 갈아 끼웠다. 새 파일은 회색 상자가 예순
# 개이고 스물여섯째가 '문제 26', 예순째가 '문제 60' 이다(그림으로 뽑아
# 눈으로 읽었다). 그래서 이 줄은 지운다 — 옛 파일에만 있던 결함이다.
STRAY: dict[str, list[int]] = {}


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def read_exams() -> list[dict[str, Any]]:
    """시험 목록. **`exams.json` 이 원본이다.**

    [한 번 못 돌던 곳] 여기는 `final.html` 안의 `const FINAL_EXAMS=[…]` 를
    잘라 읽고 있었다. 그 자리는 진작에 `exams.json` 으로 옮겨 갔고
    (화면은 `let FINAL_EXAMS=[]` 로 두고 받아서 채운다), 그래서 이 자는
    **부를 때마다 그 자리에서 멈췄다** — 크롭을 다시 만들 길이 없었다.
    2026-08-10 에 답이 실린 문제지를 갈아 끼우면서 드러났다.

    화면 안에는 창구가 죽었을 때 쓰는 `const FALLBACK_EXAMS=[…]` 가 아직
    있다. `exams.json` 이 없을 때만 그것을 쓴다."""
    path = ROOT / "exams.json"
    if path.exists():
        exams = json.loads(path.read_text(encoding="utf-8"))
        if isinstance(exams, list) and exams:
            return exams
    source = FINAL_HTML.read_text(encoding="utf-8")
    marker = "const FALLBACK_EXAMS="
    if marker not in source:
        raise RuntimeError("exams.json 도 FALLBACK_EXAMS 도 없다")
    raw = source.split(marker, 1)[1].split(";\n", 1)[0]
    exams = json.loads(raw)
    if not isinstance(exams, list) or not exams:
        raise RuntimeError("시험 목록이 비어 있다")
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


def label_ink_ratio(document: fitz.Document, page_index: int, rect: fitz.Rect) -> float:
    """딱지 안 글자가 상자 너비의 몇 할을 차지하는가.

    '문제 22' 는 0.58 언저리, '문제 22-23' 은 0.82 위다. 글자를 못 읽어도
    묶음 딱지인지는 이 폭으로 갈린다.
    """
    clip = fitz.Rect(rect.x0 + 1, rect.y0 + 1, rect.x1 - 1, rect.y1 - 1)
    pixmap = document[page_index].get_pixmap(matrix=fitz.Matrix(4, 4), clip=clip, alpha=False)
    grey = np.frombuffer(pixmap.samples, dtype=np.uint8)
    grey = grey.reshape(pixmap.height, pixmap.width, 3).mean(axis=2)
    columns = np.where((grey < 110).any(axis=0))[0]
    if not len(columns):
        return 0.0
    return float(columns[-1] - columns[0] + 1) / pixmap.width


def question_headers(
    document: fitz.Document, expected: int, exam_id: str = ""
) -> list[Header]:
    boxes: list[tuple[int, fitz.Rect]] = []
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
            boxes.append((page_index, fitz.Rect(rect)))
    boxes.sort(key=lambda item: (item[0], item[1].y0))

    groups = list(GROUPED.get(exam_id, []))
    stray = set(STRAY.get(exam_id, []))
    headers: list[Header] = []
    seen: list[tuple[int, fitz.Rect]] = []   # 지나온 딱지 전부(묶음 문두 포함)
    order: list[int] = []                    # headers[i] 가 seen 의 몇 번째인가
    pending: tuple[int, fitz.Rect] | None = None   # 아직 문항에 안 붙인 묶음 문두
    spans: list[tuple[int, int, int, fitz.Rect]] = []   # (시작, 끝, 쪽, 상자)
    for page_index, rect in boxes:
        if len(headers) >= expected:
            break
        seen.append((page_index, rect))
        if len(seen) in stray:      # 잘못 박힌 딱지. 문항으로도 자료로도 안 센다
            continue
        if label_ink_ratio(document, page_index, rect) > 0.70:
            if not groups:
                raise RuntimeError(
                    f"{exam_id}: 표에 없는 묶음 문두를 만났다 (문항 {len(headers)+1} 앞). "
                    "GROUPED 에 범위를 적어야 크롭이 안 어긋난다"
                )
            start, end = groups.pop(0)
            if start != len(headers) + 1:
                raise RuntimeError(
                    f"{exam_id}: 묶음 문두가 {len(headers)+1}번 앞에 있는데 "
                    f"GROUPED 에는 {start}번으로 적혀 있다"
                )
            spans.append([start, end, page_index, rect, None])
            pending = spans[-1]
            continue
        number = len(headers) + 1
        if pending is not None:
            # 묶음 자료는 그 묶음의 **첫 문항** 앞에서 끝난다. 뒤엣것 앞에서
            # 끊으면 앞 문항이 통째로 딸려 들어온다.
            pending[4] = rect.y0 if pending[2] == page_index else None
            pending = None
        share = next((g for g in spans if g[0] <= number <= g[1]), None)
        headers.append(Header(
            page_index=page_index, rect=rect,
            pre_page=share[2] if share else None,
            pre_rect=share[3] if share else None,
            pre_y1=share[4] if share else None,
        ))
        order.append(len(seen) - 1)
    if len(headers) < expected:
        raise RuntimeError(
            f"Only {len(headers)} question headers found; expected {expected}"
        )
    if groups:
        raise RuntimeError(f"{exam_id}: GROUPED 에 적어 둔 묶음 {groups} 을 못 찾았다")
    # 딱지 셈이 맞는가. 문항 수 + 묶음 문두 + 잘못 박힌 딱지 = 지나온 상자 수.
    # 어긋나면 표에 없는 딱지가 새로 생긴 것이다 — 그것을 모르고 지나가면
    # 그 뒤 크롭이 통째로 한 칸씩 밀린다.
    want = expected + len(GROUPED.get(exam_id, [])) + len(stray)
    if len(seen) != want:
        raise RuntimeError(
            f"{exam_id}: 딱지 셈이 안 맞는다 — 지나온 상자 {len(seen)}, "
            f"기대 {want} (문항 {expected} + 묶음 {len(GROUPED.get(exam_id, []))} "
            f"+ 잘못 박힌 딱지 {len(stray)})")
    # 자를 자리는 **다음 딱지**가 정한다. 다음 '문항' 이 아니다 — 사이에 묶음
    # 문두가 끼면 그 자료가 앞 문항 크롭에 통째로 딸려 들어간다. jmchc-1 36번이
    # 그랬다: 제 문항 아래에 '문제 37-38' 의 표가 붙어 나왔다.
    tail = boxes[len(seen)] if len(boxes) > len(seen) else None
    for i, h in enumerate(headers):
        nxt = seen[order[i] + 1] if order[i] + 1 < len(seen) else tail
        headers[i] = replace(h, stop_page=nxt[0] if nxt else None,
                             stop_y=nxt[1].y0 if nxt else None)
    return headers


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


def stack_shared_stem(
    document: fitz.Document, header: Header, image: Image.Image,
    matrix: fitz.Matrix, scale: float,
) -> Image.Image:
    page = document[header.pre_page]
    x0 = max(0.0, min(header.pre_rect.x0 - 10.0, 60.0))
    x1 = min(page.rect.width, page.rect.width - 58.0)
    y0 = max(0.0, header.pre_rect.y0 - 8.0)
    if header.pre_y1 is not None:
        y1 = max(y0 + 45.0, header.pre_y1 - 8.0)
    else:
        y1 = min(page.rect.height - 65.0, 775.0)
    clip = fitz.Rect(x0, y0, x1, y1)
    pixmap = page.get_pixmap(matrix=matrix, clip=clip, alpha=False)
    top = Image.frombytes("RGB", [pixmap.width, pixmap.height], pixmap.samples)
    top, _ = remove_red_answer_marker(top, clip, header.pre_rect, scale)
    width = max(top.width, image.width)
    gap = 16
    out = Image.new("RGB", (width, top.height + gap + image.height), "white")
    out.paste(top, (0, 0))
    out.paste(image, (0, top.height + gap))
    return out


def stack_page_break(
    document: fitz.Document, header: Header, image: Image.Image,
    matrix: fitz.Matrix, scale: float,
) -> Image.Image:
    """쪽을 넘어가는 문항의 **뒷쪽 조각**을 이어 붙인다.

    ⚠ 예전에는 이 조각을 통째로 버렸다. 문항이 쪽 아래에서 시작해 선지가
      다음 쪽 머리에 있으면, 크롭에 **발문만 남고 ①②③④ 가 사라졌다.**
      화올 2019 58번이 그랬다 — 「d-전자 배치로 가장 적절하게 짝지어진
      것은?」까지만 있고 보기가 없었다. 그 상태로는 아무리 사람을 붙여도
      선지별 오답 해설을 쓸 수 없다. (2026-09-05)
    """
    out = image
    for page_no in range(header.page_index + 1, (header.stop_page or header.page_index) + 1):
        page = document[page_no]
        x0 = max(0.0, min(header.rect.x0 - 10.0, 60.0))
        x1 = min(page.rect.width, page.rect.width - 58.0)
        # 쪽 머리(「【KMChC 2019】」 같은 머리글) 아래부터 담는다. 머리글은
        # 쪽 맨 위 70pt 안에 앉는다.
        #
        # ⚠ 여기서 「첫 본문 덩이를 찾아 그 위부터」로 잡으려다 헛짚었다.
        #   선지가 **그림**(오비탈 화살표 같은 벡터)이면 get_text('blocks')
        #   에 안 잡혀서, 맨 아래 쪽번호가 첫 덩이로 걸리고 조각이 통째로
        #   날아갔다. 글자에 기대지 말고 고정 띠로 자른다.
        y0 = 72.0
        if page_no == header.stop_page and header.stop_y is not None:
            y1 = max(y0 + 20.0, header.stop_y - 8.0)
        else:
            y1 = min(page.rect.height - 65.0, 775.0)
        if y1 - y0 < 12.0:
            continue                    # 넘어온 것이 거의 없다
        clip = fitz.Rect(x0, y0, x1, y1)
        pixmap = page.get_pixmap(matrix=matrix, clip=clip, alpha=False)
        tail = Image.frombytes("RGB", [pixmap.width, pixmap.height], pixmap.samples)
        width = max(out.width, tail.width)
        gap = 10
        merged = Image.new("RGB", (width, out.height + gap + tail.height), "white")
        merged.paste(out, (0, 0))
        merged.paste(tail, (0, out.height + gap))
        out = merged
    return out


def crop_exam(exam: dict[str, Any], force: bool = False) -> list[dict[str, Any]]:
    pdf_path = ROOT / exam["pdf"]
    if not pdf_path.exists():
        raise FileNotFoundError(pdf_path)
    document = fitz.open(pdf_path)
    headers = question_headers(document, exam["nQ"], exam["id"])
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
        if header.stop_y is not None and header.stop_page == header.page_index:
            y1 = max(y0 + 45.0, header.stop_y - 8.0)
        elif header.stop_page is not None and header.stop_page != header.page_index:
            # 쪽을 넘어가는 문항. 이 쪽에 남은 **본문 끝까지**만 담는다 —
            # 쪽 바닥까지 끌면 빈 여백과 쪽번호가 따라온다.
            last = y0 + 45.0
            for b in page.get_text('blocks'):
                if b[3] > 780.0:
                    continue            # 쪽번호 줄
                if b[1] >= y0:
                    last = max(last, b[3])
            y1 = min(page.rect.height - 65.0, last + 10.0)
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
            if (header.stop_page is not None
                    and header.stop_page != header.page_index):
                # 문항이 쪽을 넘어간다 — 넘어간 조각까지 이어 붙인다.
                image = stack_page_break(document, header, image, matrix, scale)
            if header.pre_rect is not None:
                # 묶음 문두(둘이 나눠 쓰는 자료)를 문항 위에 얹는다. 안 얹으면
                # 뒷 문항은 "위 자료를 보고" 만 남고 자료가 없다.
                image = stack_shared_stem(document, header, image, matrix, scale)
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
        questions = {}
        # ⚠ **한 번 지워 버린 곳.** 이 자는 answers/<회차>.json 을 해설지에서
        #   다시 만든다. 그런데 그 파일에는 해설지에 없는 **손으로 쓴 오개념**
        #   한 줄이 문항마다 들어 있다. 2026-08-10 에 답 실린 문제지를 갈아
        #   끼우려고 크롭만 다시 만들었더니, 서른아홉 회차 2,310문항의 그
        #   한 줄이 통째로 빈 문자열이 됐다(커밋 전에 알아채고 되돌렸다).
        #   해설지에서 안 나오는 말은 **있던 것을 그대로 둔다**.
        kept = {}
        _prev = ANSWER_DIR / f"{exam['id']}.json"
        if _prev.exists():
            kept = (json.loads(_prev.read_text(encoding="utf-8")) or {}).get("questions", {})
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
            # 이미 적혀 있던 것 — 해설지에서 안 나오는 **손으로 쓴 말**은 지우지 않는다.
            had = kept.get(str(number), {})
            questions[str(number)] = {
                "answer": key,
                "acceptableAnswers": multi or ([key] if key else []),
                "excluded": number in miss,
                "concept": qtype or area,
                "area": area,
                "learningPoint": (
                    verified.get("areaLabel") if verified else (qtype or area)
                ),
                "explanation": explanation.get("explanation", "") or had.get("explanation", ""),
                "explanationHtml": (explanation.get("explanationHtml", "")
                                    or had.get("explanationHtml", "")),
                "misconception": (explanation.get("misconception", "")
                                  or had.get("misconception", "")),
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
