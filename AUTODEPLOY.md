# Apps Script 자동배포 설정 (최초 1회, 컴퓨터 필요)

설정을 마치면 **AppsScript-Code.gs가 main에 머지될 때마다 자동으로 Apps Script에 반영되고
같은 URL로 재배포**됩니다. 더 이상 코드를 복붙하거나 "배포 관리 → 새 버전"을 누를 일이 없습니다.

## 1. Apps Script API 켜기 (1분)
1. https://script.google.com/home/usersettings 접속
2. **Google Apps Script API** 를 **사용** 으로 변경

## 2. 컴퓨터에서 clasp 로그인 (5분)
Node.js가 설치된 컴퓨터에서:

```bash
npm i -g @google/clasp@2.4.2
clasp login
```

브라우저가 열리면 **시트를 소유한 구글 계정**으로 로그인 → 허용.
로그인이 끝나면 인증 파일이 생깁니다:

- Mac/리눅스: `~/.clasprc.json`
- Windows: `C:\Users\<사용자>\.clasprc.json`

이 파일을 열어 **내용 전체를 복사**해 둡니다.

## 3. GitHub 시크릿 3개 등록 (3분)
GitHub 저장소 → **Settings → Secrets and variables → Actions → New repository secret**

| 시크릿 이름 | 값 | 어디서 찾나 |
|---|---|---|
| `CLASPRC_JSON` | 2번에서 복사한 파일 내용 전체 | `~/.clasprc.json` |
| `GAS_SCRIPT_ID` | 스크립트 ID | Apps Script 편집기 → ⚙ 프로젝트 설정 → **스크립트 ID** |
| `GAS_DEPLOYMENT_ID` | 배포 ID (`AKfycb...`) | Apps Script 편집기 → 배포 → **배포 관리** → 현재 웹앱 배포의 **배포 ID** |

## 4. 끝. 확인 방법
- 이후 AppsScript-Code.gs가 main에 머지되면 **Actions 탭**에 "Apps Script 자동 배포"가 돌고,
  성공하면 시트 쪽 코드가 이미 최신입니다 (URL 변화 없음).
- 수동으로 돌려보려면: Actions 탭 → Apps Script 자동 배포 → **Run workflow**

## 주의
- `CLASPRC_JSON`은 구글 계정 접근 토큰입니다. **GitHub 시크릿에만** 넣고 다른 곳에 붙여넣지 마세요.
- 시크릿을 등록하기 전까지 워크플로는 아무것도 하지 않고 조용히 건너뜁니다(오류 아님).
- 언젠가 구글이 토큰을 만료시키면 2번(`clasp login`)만 다시 하고 `CLASPRC_JSON`을 갱신하면 됩니다.
