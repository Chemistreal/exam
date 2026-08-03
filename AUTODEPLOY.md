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

---

# 열쇠가 만료됐을 때 (다시 로그인)

Actions 에 이렇게 뜨면 토큰이 죽은 것입니다.

```
Error retrieving access token: Error: invalid_grant
```

이때 **저장소에는 코드가 들어가 있지만 Apps Script 에는 안 올라갑니다.**
화면은 옛 코드로 계속 돕니다 — 2026-08-03 에 실제로 그랬습니다.

## 1. 다시 로그인 (2분)

Node.js 가 있는 컴퓨터에서:

```bash
npm i -g @google/clasp@2.4.2      # ⚠ 2.4.2 로 고정. 3.x 는 파일 모양이 다릅니다
clasp logout                      # 죽은 토큰을 먼저 지웁니다
clasp login
```

브라우저가 열리면 **시트를 소유한 구글 계정**으로 로그인 → 허용.

## 2. 파일 내용 복사

- Mac/리눅스: `cat ~/.clasprc.json`
- Windows: `type %USERPROFILE%\.clasprc.json`

**중괄호 `{` 부터 `}` 까지 통째로** 복사합니다(줄바꿈 포함, 앞뒤 공백 없이).

## 3. 시크릿 갈아 끼우기

저장소 → **Settings → Secrets and variables → Actions** →
`CLASPRC_JSON` 옆 **연필(Update)** → 붙여넣기 → **Update secret**

`GAS_SCRIPT_ID` 와 `GAS_DEPLOYMENT_ID` 는 **그대로 둡니다** — 안 바뀝니다.

## 4. 바로 확인

**Actions → Apps Script 자동 배포 → Run workflow** 를 눌러 손으로 한 번 돌립니다.

- 초록불이면 끝입니다. 웹앱 URL 은 그대로입니다.
- `코드 반영 (clasp push)` 에서 또 `invalid_grant` 면 → 1번을 **다른 계정으로**
  했을 가능성이 큽니다. 시트를 소유한 계정인지 확인하세요.
- `Apps Script API 사용 안 함` 이 뜨면 → 맨 위 1번(API 켜기)을 다시 봅니다.

## 왜 또 만료되나

가장 흔한 이유는 **OAuth 동의 화면이 '테스트' 상태**일 때입니다. 그러면 구글이
새로고침 토큰을 **7일마다** 만료시킵니다. 매주 이 짓을 하고 싶지 않다면
Google Cloud 콘솔에서 그 프로젝트의 게시 상태를 **'프로덕션'** 으로 올리면
됩니다(내부용이라 심사는 필요 없습니다).

그 밖에 계정 비밀번호를 바꿨거나, 같은 계정에서 토큰을 너무 많이 발급했을
때도 죽습니다.

## 죽은 것을 어떻게 알게 되나

배포는 `.gs` 가 바뀔 때만 돕니다. 그래서 열쇠가 죽어도 **다음에 `.gs` 를 고칠
때까지 몇 주라도 모릅니다.** 그래서 `앱 창구 점검`(매일 07:00 KST)에 열쇠
확인을 얹어 두었습니다 — 죽으면 그날 아침 깃허브가 메일을 보냅니다.

---

## 주의
- `CLASPRC_JSON`은 구글 계정 접근 토큰입니다. **GitHub 시크릿에만** 넣고 다른 곳에 붙여넣지 마세요.
- 시크릿을 등록하기 전까지 워크플로는 아무것도 하지 않고 조용히 건너뜁니다(오류 아님).
- 언젠가 구글이 토큰을 만료시키면 2번(`clasp login`)만 다시 하고 `CLASPRC_JSON`을 갱신하면 됩니다.
