# 오답정리 원문 문제 이미지

`final.html`의 성적진단서와 PDF 부록에서 틀린 문항만 다시 보여 주기 위한 원문 크롭입니다.

## 경로

```text
crops/<시험ID>/<문항번호>.png
```

예: `crops/jmchc-1/11.png`

`tools/build_wrongbook_assets.py`가 `FINAL_EXAMS`의 문제 PDF를 읽어 회색 `문제 N` 헤더를 기준으로 문항 경계를 찾고, 지문·보기·표·그림을 2배 해상도로 렌더링한 뒤 웹용 PNG로 최적화합니다. 원문에 정답 표시가 겹친 자료는 헤더 옆의 붉은 정답 표시 영역만 제거합니다.

```bash
python3 tools/build_wrongbook_assets.py --force-crops
python3 tools/build_wrongbook_assets.py --validate-only
```

이미지가 없거나 손상된 경우 화면은 멈추지 않고 준비 중 안내를 표시합니다. 전체 준비 상태는 `reports/wrongbook-asset-audit.json`에서 확인합니다.
