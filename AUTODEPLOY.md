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

계정 비밀번호를 바꿨거나, 같은 계정에서 토큰을 너무 많이 발급했거나(한
클라이언트당 50개가 넘으면 오래된 것부터 조용히 죽습니다), 구글이 그냥
거둬 갔을 때 죽습니다.

`clasp login` 으로 만든 열쇠는 **clasp 자신의 OAuth 클라이언트**에 붙습니다.
그래서 언제 죽을지를 이쪽에서 정할 수 없고, 죽으면 위 1~4를 되풀이하는 수밖에
없습니다. 매번 하고 싶지 않다면 아래처럼 **내 이름의 클라이언트**로 갈아탑니다.

---

# 매주 만료되지 않게 (내 OAuth 클라이언트로 갈아타기)

토큰의 수명은 **그 토큰이 붙은 OAuth 클라이언트의 동의 화면 상태**가 정합니다.
동의 화면이 **'테스트'** 면 새로고침 토큰이 **7일**만 살고, **'프로덕션'** 이면
쓰는 동안 계속 삽니다.

⚠ 그런데 `clasp login`(위 절차)으로 만든 열쇠는 **clasp 의 클라이언트**에
붙습니다. 그래서 **내 구글 클라우드 프로젝트의 동의 화면을 프로덕션으로 올려도
그 열쇠에는 아무 영향이 없습니다.** 아래 절차로 **클라이언트부터 내 것으로**
바꿔야 '프로덕션' 이 뜻을 가집니다.

한 번만 하면 됩니다. 20분쯤 걸립니다.

구글 콘솔은 메뉴가 자주 바뀌고 계정마다 옛 화면·새 화면이 갈립니다.
**메뉴를 찾지 말고 주소로 바로 가세요.** 위에서부터 차례로 누르면 됩니다.

| 단계 | 주소 |
|---|---|
| ① 프로젝트 만들기 | https://console.cloud.google.com/projectcreate |
| ② Apps Script API 켜기 | https://console.cloud.google.com/apis/library/script.googleapis.com |
| ③ 동의 화면 → 프로덕션 | https://console.cloud.google.com/auth/audience |
| ④ 클라이언트 만들기 | https://console.cloud.google.com/auth/clients |

⚠ 어느 페이지든 **맨 위 파란 띠의 프로젝트 이름**이 ①에서 만든 것인지 먼저
보세요. 다른 프로젝트가 골라져 있으면 엉뚱한 곳에 만들어집니다.

## 1. 프로젝트 만들고 Apps Script API 켜기

1. https://console.cloud.google.com/projectcreate — **시트를 소유한 계정**으로.
   이름은 아무거나(예: `chemistreal-deploy`) → 만들기.
2. 만든 프로젝트가 골라진 상태에서
   https://console.cloud.google.com/apis/library/script.googleapis.com → **사용(Enable)**.

## 2. 동의 화면 만들고 **프로덕션으로 게시**

https://console.cloud.google.com/auth/audience
(옛 화면이면 **API 및 서비스 → OAuth 동의 화면**. 하는 일은 같습니다)

1. **시작하기 / 브랜딩** — 앱 이름은 아무거나, 사용자 지원 이메일·개발자
   연락처에 **본인 메일**을 넣습니다.
2. **대상(Audience)** — **외부(External)** 를 고릅니다.
   > 개인 Gmail 계정에는 '내부' 가 없습니다. 외부라도 쓰는 사람이 나 하나면
   > 문제되지 않습니다.
3. **데이터 액세스(범위)** — 아무것도 안 더해도 됩니다. clasp 가 로그인할 때
   필요한 범위를 그때 요청합니다.
4. ★ **대상(Audience) 화면의 '앱 게시' → `앱 게시하기`** 를 눌러
   게시 상태를 **테스트 → 프로덕션**으로 올립니다.
   - "확인이 필요할 수 있습니다" 안내가 떠도 **그대로 게시**하면 됩니다.
     심사를 안 받으면 로그인할 때 "확인되지 않은 앱" 경고가 한 번 뜨는데,
     **고급 → (앱 이름)(으)로 이동** 을 누르면 지나갑니다. 쓰는 사람이
     100명 미만이면 심사 없이 계속 쓸 수 있습니다.
   - **이 한 번의 클릭이 7일 만료를 없애는 자리입니다.**

## 3. 데스크톱 클라이언트 만들기

https://console.cloud.google.com/auth/clients

1. **+ 클라이언트 만들기** (파란 단추)
2. 애플리케이션 유형 **데스크톱 앱** ← ⚠ 웹 애플리케이션이 아닙니다.
   clasp 는 데스크톱 클라이언트만 받습니다.
3. 이름은 아무거나(`clasp` 등) → **만들기**
4. 뜨는 창이나 목록의 **다운로드 아이콘(↓) → JSON 다운로드** —
   파일 이름을 `creds.json` 으로 바꿔 둡니다.

다른 화면이 뜬다면:

- **"OAuth 동의 화면을 먼저 구성하세요"** → 2번을 아직 안 한 것입니다.
- 왼쪽 메뉴가 `개요 · 브랜딩 · 대상 · 클라이언트 · 데이터 액세스` 면 새 화면이고,
  맞게 온 것입니다.
- **옛 화면**이 뜨는 계정도 있습니다. 그때는 왼쪽 위 **☰ → API 및 서비스 →
  사용자 인증 정보 → + 사용자 인증 정보 만들기 → OAuth 클라이언트 ID**.
  하는 일은 똑같습니다.

## 4. 그 클라이언트로 로그인

```bash
clasp logout                        # 옛 열쇠를 먼저 지웁니다
clasp login --creds creds.json
```

브라우저에서 **시트를 소유한 계정**으로 로그인 → ("확인되지 않은 앱" 이 뜨면
**고급 → 이동**) → 허용.

⚠ `--creds` 로 로그인하면 열쇠가 `~/.clasprc.json` 이 **아니라 지금 폴더의
`.clasprc.json`** 에 생깁니다. 그 파일을 복사합니다.

- Mac/리눅스: `cat .clasprc.json`
- Windows(파워셸): `Get-Content .\.clasprc.json -Raw | Set-Clipboard`

## 5. 시크릿 갈아 끼우고 확인

`CLASPRC_JSON` 을 4번 내용으로 바꾸고, **Actions → Apps Script 자동 배포 →
Run workflow**. 초록불이면 끝입니다.

> 배포 워크플로는 이 파일을 `~/.clasprc.json` 과 `./.clasprc.json` **두 자리 모두**에
> 씁니다. `clasp login` 으로 만든 것이든 `--creds` 로 만든 것이든 그대로 됩니다.

## 6. 그래도 지켜야 하는 것

`creds.json` 과 `.clasprc.json` 은 **구글 계정 열쇠**입니다. 저장소에 커밋하지
말고, 시크릿 말고 다른 곳에 붙여넣지 마세요.

## 죽은 것을 어떻게 알게 되나

배포는 `.gs` 가 바뀔 때만 돕니다. 그래서 열쇠가 죽어도 **다음에 `.gs` 를 고칠
때까지 몇 주라도 모릅니다.** 그래서 `앱 창구 점검`(매일 07:00 KST)에 열쇠
확인을 얹어 두었습니다 — 죽으면 그날 아침 깃허브가 메일을 보냅니다.

---

## 주의
- `CLASPRC_JSON`은 구글 계정 접근 토큰입니다. **GitHub 시크릿에만** 넣고 다른 곳에 붙여넣지 마세요.
- 시크릿을 등록하기 전까지 워크플로는 아무것도 하지 않고 조용히 건너뜁니다(오류 아님).
- 언젠가 구글이 토큰을 만료시키면 2번(`clasp login`)만 다시 하고 `CLASPRC_JSON`을 갱신하면 됩니다.
