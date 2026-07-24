# 오답정리 동형문제 데이터

학생이 원문 해설을 확인한 뒤 같은 개념을 새 조건에서 다시 적용하도록, 시험별 문항에 검증된 재학습 문제를 한 개씩 연결합니다. 보고서 실행 중 GPT나 외부 API를 호출하지 않습니다.

현재 데이터는 저장소 안의 다른 시험 문항 중 장문 해설과 정답이 검증된 문항을 대상으로, 동일 PDF를 제외하고 유형·영역·개념 일치도가 가장 높은 문항을 선택합니다. 따라서 정답·화학식·단위·보기가 이미 문제지와 해설에서 교차검증된 자료입니다.

## 경로

```text
donghyung/<시험ID>.json
```

## 스키마

```json
{
  "schemaVersion": 2,
  "examId": "jmchc-1",
  "questions": {
    "11": {
      "concept": "평가 개념",
      "area": "평가 영역",
      "difficulty": "원문과 유사한 수준",
      "sourceExamId": "jmchc-2",
      "sourceQuestion": 13,
      "image": "crops/jmchc-2/13.png",
      "stem": "텍스트 대체 지문",
      "choices": ["보기 1", "보기 2", "보기 3", "보기 4"],
      "answer": 3,
      "explanationHtml": "검증된 단계별 해설",
      "misconceptions": {
        "1": "① 선택지 오개념",
        "2": "② 선택지 오개념",
        "4": "④ 선택지 오개념"
      },
      "learningPoint": "학습 포인트",
      "matchLevel": "exact_type",
      "verified": true
    }
  }
}
```

전체 41개 시험·2,400문항의 파일 존재 여부, 정답 범위, 해설, 연결 이미지 경로는 다음 명령으로 검사합니다.

```bash
python3 tools/build_wrongbook_assets.py --validate-only
```
