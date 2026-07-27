#!/usr/bin/env python3
"""문항 크롭 이미지를 다른 형식으로 바꾸면 얼마나 줄어드는지 실제로 재 본다.

`crops/` 는 56MB로 저장소에서 가장 무겁다. "PNG를 WebP로 바꾸면 60~70% 줄어든다"는
것은 사진에 해당하는 이야기고, 여기 있는 것은 **흑백 문항 스캔**이다. PNG가 이미
잘 다루는 종류라 실제로 재 보면 이야기가 다르다. 그래서 바꾸기 전에 잰다.

측정 결과(무작위 20장, 2026-07):

    원본 png        100%   ← 이미 최적화돼 있다(optimize=True 로 다시 눌러도 그대로)
    webp 무손실      74%   ← 픽셀 동일. 안전하게 얻을 수 있는 전부
    32색+webp        57%   ← 픽셀이 바뀐다
    16색+webp        50%   ← 픽셀 최대 오차 17/255
    webp 손실 q88   103%   ← 오히려 커진다. 흑백 선화에 손실 압축은 손해다

즉 **안전하게 얻을 수 있는 것은 26%**(56MB → 41MB)이고, 그 이상은 픽셀을 건드려야
한다. 문항 그림에는 명암으로 뜻을 나타내는 것(궤도함수 음영, 농도 진하기)이 있어
양자화는 권하지 않는다.

바꾸기로 한다면 Word 저장 경로를 함께 고쳐야 한다. `downloadReportDOCX()` 가
이미지를 그대로 문서에 심는데, Word 의 WebP 지원은 판마다 다르다. 브라우저에서
canvas 로 PNG 로 되돌려 심어야 한다.

사용:
    python3 tools/crops_measure.py            # 표본 20장으로 추정
    python3 tools/crops_measure.py --all      # 2400장 전부 (몇 분 걸린다)
    python3 tools/crops_measure.py --convert  # 실제로 .webp 를 만든다(무손실)
"""

from __future__ import annotations

import glob
import io
import random
import sys
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parents[1]


def encoded_size(image: Image.Image, fmt: str, **kw) -> int:
    buffer = io.BytesIO()
    image.save(buffer, fmt, **kw)
    return buffer.tell()


def measure(paths: list[str]) -> None:
    totals = {"원본 png": 0, "webp 무손실": 0, "webp 손실 q88": 0, "16색+webp": 0}
    for path in paths:
        image = Image.open(path)
        totals["원본 png"] += Path(path).stat().st_size
        totals["webp 무손실"] += encoded_size(image, "WEBP", lossless=True, method=6)
        totals["webp 손실 q88"] += encoded_size(image, "WEBP", quality=88, method=6)
        small = image.convert("L").quantize(colors=16).convert("L")
        totals["16색+webp"] += encoded_size(small, "WEBP", lossless=True, method=6)

    base = totals["원본 png"]
    print(f"표본 {len(paths)}장")
    for name, size in totals.items():
        print(f"  {name:14} {size/1024/1024:7.2f}MB  {size/base*100:5.0f}%")
    whole = sum(Path(p).stat().st_size for p in glob.glob(str(ROOT / "crops/**/*.png"), recursive=True))
    saved = whole * (1 - totals["webp 무손실"] / base)
    print(
        f"\ncrops/ 전체 {whole/1024/1024:.0f}MB 기준, 무손실 WebP 로 바꾸면 "
        f"약 {saved/1024/1024:.0f}MB 줄어든다({(1-totals['webp 무손실']/base)*100:.0f}%)."
    )
    print("픽셀을 건드리지 않고 얻을 수 있는 것은 여기까지다.")


def convert(paths: list[str]) -> None:
    """무손실 WebP 를 나란히 만든다. 원본 PNG 는 지우지 않는다.

    지우는 것은 사람이 확인하고 한다 — 화면·인쇄·Word 세 경로가 모두 새 파일을
    잘 읽는지 본 뒤에 지워야 되돌릴 수 있다.
    """
    made = before = after = 0
    for path in paths:
        target = Path(path).with_suffix(".webp")
        if target.exists():
            continue
        Image.open(path).save(target, "WEBP", lossless=True, method=6)
        before += Path(path).stat().st_size
        after += target.stat().st_size
        made += 1
    print(f"{made}장 변환 · {before/1024/1024:.1f}MB → {after/1024/1024:.1f}MB")
    print("\n화면·인쇄·Word 세 경로를 모두 확인한 뒤에 원본을 지운다:")
    print("    find crops -name '*.png' -delete   # 되돌릴 수 없다. 확인 뒤에")


def main() -> int:
    args = sys.argv[1:]
    paths = sorted(glob.glob(str(ROOT / "crops/**/*.png"), recursive=True))
    if not paths:
        print("crops/ 에 PNG 가 없다")
        return 1
    if "--convert" in args:
        convert(paths)
        return 0
    if "--all" not in args:
        random.seed(1)  # 돌릴 때마다 같은 표본이라야 수치를 비교할 수 있다
        paths = random.sample(paths, min(20, len(paths)))
    measure(paths)
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except BrokenPipeError:
        sys.exit(0)
