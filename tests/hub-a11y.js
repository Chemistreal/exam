/* ============================================================
   허브를 **눈 말고 다른 것으로** 쓸 수 있는가
   ------------------------------------------------------------
   허브 검사는 833개였는데, 이름에 `aria`·`tabindex`·낭독·화살표·색약이 든
   것이 **하나도 없었다.** 833개가 전부 동작과 자료를 본다 — 누가 무엇을
   읽어 오고, 어떤 숫자가 찍히고, 캐시가 두 번 안 나가는지. **화면을 쓰는
   방법은 아무도 안 보고 있었다.**

   안 보고 있었으니 새고 있었다. 재어 보니 둘이다(2026-08-09).

       탭 12개 가운데 tabindex 를 가진 것      0개
       aria-live · role=status                0개 · 0개

   ① **탭 줄이 화살표를 안 받았다.** `role="tablist"` 를 쓰면 좌우 화살표로
      옮기고 고르지 않은 탭은 탭 순서에서 빠지는 것이 약속이다(ARIA APG).
      둘 다 없어서, 탭 줄 하나를 지나가는 데 Tab 을 열두 번 눌러야 했다.
      숫자 단축키(1~9·0·-·=)가 있어 손 빠른 사람은 안 겪는다. 낭독기를 쓰는
      사람은 늘 겪는다.

   ② **바뀌는 숫자를 낭독기가 몰랐다.** 대시보드 카드는 '불러오는 중' 으로
      떴다가 창구가 대답하면 숫자로 바뀐다. 알리는 자리가 없어서, 낭독기는
      처음에 읽은 말 그대로였다.

   ⚠ 화살표는 **초점만 옮긴다.** 옮기는 족족 여는 방식을 먼저 해 봤는데 두
     군데서 망가졌다 — 수입 탭은 들어가면 코드 칸으로 초점을 가져가 그다음
     화살표가 안 먹었고, 앱 탭 다섯은 지나가기만 해도 iframe 이 다 붙었다.
     그래서 **눌러야 열린다**(manual activation).

   여기서 지키는 것:
   - 줄마다 탭 순서에 서는 탭이 **하나씩**이다 (둘째 줄도 키보드로 닿는다)
   - 좌우 화살표가 줄 안에서 돌고, Home·End 가 끝으로 간다
   - 화살표는 **고른 탭을 바꾸지 않는다**
   - 낭독기만 읽는 알림 칸이 있고, 같은 말은 되풀이하지 않는다
   - **못 불러왔다는 말은 반드시 들린다**

   실행:
       node tests/hub-a11y.js
   ============================================================ */
'use strict';
require('./_watchdog.js')(240);
const seal = require('./_seal.js');
const noSheet = require('./_nosheet.js');
/* 포트를 그 자리에서 받고, 서버가 **대답할 때까지** 기다린다.
   고정 포트를 박아 두면 검사 두 벌이 겹칠 때 뒤엣것이 빈 화면을 보고
   "그게 화면에 없다" 고 말한다 — tests/_serve.js 머리말. */
const { serve } = require('./_serve.js');
const path = require('path');

const PLAYWRIGHT = process.env.PLAYWRIGHT_MODULE || 'playwright';
const CHROMIUM = process.env.CHROMIUM_PATH || undefined;
/* 번호를 안 박는다(0 이면 빈 포트를 받는다). `PORT` 를 준 자리는 그대로 쓴다.
   **서버를 띄운 뒤 실제로 받은 번호로 채운다** — 아래 `serve()` 바로 다음. */
let PORT = Number(process.env.PORT || 0);
const ROOT = path.join(__dirname, '..');

let fail = 0;
const chk = (n, got, want) => {
  const ok = JSON.stringify(got) === JSON.stringify(want);
  console.log((ok ? '  PASS  ' : '  FAIL  ') + n +
    (ok ? '' : `  → ${JSON.stringify(got)} (기대 ${JSON.stringify(want)})`));
  if (!ok) fail++;
};

let chromium;
try { ({ chromium } = require(PLAYWRIGHT)); }
catch (e) {
  if (process.env.REQUIRE_BROWSER) {
    console.log('실패: playwright 를 찾지 못했다 (REQUIRE_BROWSER 가 켜져 있다)');
    process.exit(1);
  }
  console.log('건너뜀: playwright 를 찾지 못했다'); process.exit(0);
}

(async () => {
  const srv = await serve(ROOT, { port: PORT });
  PORT = srv.port;

  const browser = seal(await chromium.launch(
    Object.assign({ args: ['--no-sandbox'] }, CHROMIUM ? { executablePath: CHROMIUM } : {})));
  /* ⚠ **시트를 막고 시작한다.** 안 막으면 검사가 학원의 진짜 시트를 읽고,
     채점하는 검사는 **거기에 줄을 쓴다.** 2026-08-12 에 실제로 그랬다 —
     이 검사가 판을 돌 때마다 «무응답점검·분류점검·자료링크점검» 같은 이름이
     선생님 시트에 쌓이고 있었다(POST 를 세어서 확인했다).
     `tests/_nosheet.js` 머리말이 처음부터 이르던 일이다. */
  await noSheet(browser);
  const ctx = await browser.newContext({
    viewport: { width: 1280, height: 900 }, serviceWorkers: 'block' });
  const p = await ctx.newPage();
  const errs = [];
  p.on('pageerror', e => errs.push(String(e)));
  await p.addInitScript(() => {
    try { localStorage.setItem('chemistreal:gate', String(Date.now())); } catch (e) {}
  });
  /* 창구는 안 부른다 — 여기서 보는 것은 자료가 아니라 **쓰는 방법**이다.
     _seal 이 이미 구글로 나가는 길을 끊었고, 대답이 없어도 탭 줄은 선다. */
  await p.route('**/DT/**', r => r.fulfill({
    status: 200, contentType: 'text/html; charset=utf-8',
    body: '<!doctype html><meta charset="utf-8">' }));

  try {
    await p.goto(`http://localhost:${PORT}/hub.html`, { waitUntil: 'domcontentloaded' });
    await p.waitForFunction(() => typeof say === 'function' && typeof rovingTabs === 'function',
      null, { timeout: 20000 });
    await p.waitForFunction(
      () => document.querySelectorAll('[role="tab"]').length > 0, null, { timeout: 10000 });

    console.log('── 탭 줄이 키보드를 받는가 ──');
    const t0 = await p.evaluate(() => ({
      줄: document.querySelectorAll('nav[role="tablist"]').length,
      탭: document.querySelectorAll('[role="tab"]').length,
      /* 줄마다 탭 순서에 서는 탭이 하나씩이어야 한다. 하나도 없으면 그 줄은
         키보드로 아예 못 닿고, 전부 서 있으면 Tab 을 열두 번 눌러야 한다. */
      줄별탭순서: [...document.querySelectorAll('nav[role="tablist"]')]
        .map(n => [...n.querySelectorAll('[role="tab"]')].filter(b => b.tabIndex === 0).length),
      /* 한 바퀴 도는 데 몇 곳을 지나는가 */
      초점자리: [...document.querySelectorAll(
        'a[href],button:not([disabled]),input:not([disabled]),select,textarea,[tabindex]')]
        .filter(e => e.tabIndex >= 0 && e.getBoundingClientRect().width > 0).length,
    }));
    console.log(`  tablist ${t0.줄}줄 · 탭 ${t0.탭}개 · 줄마다 탭 순서에 선 것 ${JSON.stringify(t0.줄별탭순서)}`);
    chk('tablist 가 둘이다', t0.줄, 2);
    chk('줄마다 탭 순서에 서는 탭이 하나씩이다', t0.줄별탭순서, [1, 1]);

    /* ── 화살표가 줄 안에서 돈다 ────────────────────────────────────── */
    const step = async (from, keys) => {
      await p.focus('#' + from);
      for (const k of keys) {
        const was = await p.evaluate(() => document.activeElement.id);
        await p.keyboard.press(k);
        /* 기대하는 **값**을 기다리면 검사가 스스로 답을 맞춰 준다. '달라졌다'
           까지만 기다린다 — 안 달라지는 경우(Home 에서 Home)도 있으니 짧게 끊는다. */
        await p.waitForFunction(w => document.activeElement.id !== w, was, { timeout: 1500 })
          .catch(() => {});
      }
      return p.evaluate(() => ({
        초점: document.activeElement.id,
        고른탭: [...document.querySelectorAll('[role="tab"][aria-selected="true"]')].map(x => x.id),
      }));
    };
    const r1 = await step('t-dash', ['ArrowRight']);
    chk('오른쪽 화살표가 옆 탭으로 옮긴다', r1.초점, 't-stu');
    chk('화살표는 고른 탭을 바꾸지 않는다', r1.고른탭, ['t-dash']);

    const r2 = await step('t-dash', ['ArrowLeft']);
    chk('왼쪽 화살표는 줄 끝으로 돈다', r2.초점, 't-inc');

    const r3 = await step('t-dash', ['End']);
    chk('End 가 줄 끝으로 간다', r3.초점, 't-inc');
    const r4 = await step('t-inc', ['Home']);
    chk('Home 이 줄 처음으로 간다', r4.초점, 't-dash');
    const r5 = await step('t-inc', ['ArrowRight']);
    chk('끝에서 한 번 더 누르면 처음으로 돈다', r5.초점, 't-dash');

    /* 둘째 줄(앱 화면)은 첫째 줄과 **따로** 돈다. 넘나들면 '보기' 와 '작업'
       두 줄이 한 줄처럼 읽힌다. */
    const r6 = await step('t-exam', ['ArrowRight']);
    chk('둘째 줄도 화살표를 받는다', r6.초점, 't-dt');
    const r7 = await step('t-exam', ['ArrowLeft']);
    chk('둘째 줄이 첫째 줄로 넘어가지 않는다', r7.초점, 't-km');

    /* 화살표로 옮기면 탭 순서에 서는 자리도 따라와야 한다 — 안 그러면
       Tab 으로 나갔다 돌아올 때 엉뚱한 탭으로 온다. */
    await p.focus('#t-dash');
    await p.waitForFunction(() => document.activeElement.id === 't-dash', null, { timeout: 2000 });
    await p.keyboard.press('ArrowRight');
    await p.waitForFunction(() => document.activeElement.id !== 't-dash', null, { timeout: 2000 });
    const r8 = await p.evaluate(() => [...document.querySelectorAll('nav[role="tablist"]')][0]
      .querySelectorAll('[role="tab"]')[1].tabIndex);
    chk('탭 순서에 서는 자리가 초점을 따라온다', r8, 0);

    /* 눌러야 열린다 — Enter 는 브라우저가 click 으로 바꿔 준다. */
    await p.focus('#t-stu');
    await p.keyboard.press('Enter');
    await p.waitForFunction(
      () => document.querySelector('[role="tab"][aria-selected="true"]').id !== 't-dash',
      null, { timeout: 4000 }).catch(() => {});
    const r9 = await p.evaluate(() =>
      [...document.querySelectorAll('[role="tab"][aria-selected="true"]')].map(x => x.id));
    chk('Enter 로 열린다', r9, ['t-stu']);

    console.log('\n── 창이 초점을 가두고, 닫으면 돌려주는가 ──');
    /* `showModal()` 로 열면 가두는 것까지는 브라우저가 한다. 그런데 **닫을
       때**는 아무 데도 안 돌려준다 — 재어 보니 닫은 뒤 초점이 <body> 로
       흩어졌다. 키보드로 쓰는 사람은 학생 카드를 닫을 때마다 화면 맨 위에서
       Tab 을 다시 눌러 내려와야 한다. 한 반을 훑는 상담 주간이면 스무 번이다. */
    await p.focus('#t-stu');
    const 열기전 = await p.evaluate(() => document.activeElement.id);
    await p.evaluate(() => openPal());
    await p.waitForFunction(() => document.getElementById('pal').open, null, { timeout: 4000 });
    const 여는중 = await p.evaluate(() => ({
      초점: document.activeElement.id,
      갇힘: document.getElementById('pal').matches(':modal'),
    }));
    await p.keyboard.press('Escape');
    await p.waitForFunction(() => !document.getElementById('pal').open, null, { timeout: 4000 });
    const 닫은뒤 = await p.evaluate(() => document.activeElement.id);
    console.log(`  ${열기전} → ${여는중.초점} → ${닫은뒤}`);
    chk('창이 초점을 가둔다', 여는중.갇힘, true);
    chk('창을 열면 안쪽으로 초점이 간다', 여는중.초점, 'palIn');
    chk('닫으면 열었던 자리로 돌아온다', 닫은뒤, 열기전);
    /* 네 창이 다 `showModal()` 이어야 한다. `show()` 는 안 가둔다 — 뒤 화면으로
       Tab 이 새어 나가고, 낭독기는 창 밖 글까지 읽는다. */
    const 여는법 = await p.evaluate(() => {
      const src = [...document.querySelectorAll('script')].map(s => s.textContent).join('\n');
      return { 안가두는열기: (src.match(/\.show\(\)/g) || []).length };
    });
    chk('안 가두는 방식으로 여는 창이 없다', 여는법.안가두는열기, 0);

    console.log('\n── 낭독기에게 알리는가 ──');
    const live = await p.evaluate(() => {
      const e = document.getElementById('sr');
      if (!e) return null;
      const b = e.getBoundingClientRect();
      return { role: e.getAttribute('role'), live: e.getAttribute('aria-live'),
               atomic: e.getAttribute('aria-atomic'),
               보임: b.width > 2 || b.height > 2,
               숨김방식: getComputedStyle(e).display };
    });
    chk('알림 칸이 있다', !!live, true);
    chk('role=status 다', live && live.role, 'status');
    chk('공손하게 알린다(polite)', live && live.live, 'polite');
    chk('한 덩어리로 읽는다(atomic)', live && live.atomic, 'true');
    chk('화면에는 안 보인다', live && live.보임, false);
    /* display:none 으로 숨기면 낭독기도 같이 못 읽는다 — 1px 로 잘라야 한다. */
    chk('낭독기가 못 읽게 숨기지 않았다', live && live.숨김방식 !== 'none', true);

    /* ⚠ 이 칸은 **나만 쓰는 것이 아니다.** 창구가 실패할 때마다 화면이 다시
       그려지며 같은 안내를 또 밀어 넣는다(renderDash 안의 catch). 조용해지길
       기다려도, 되살려 놔도 다음 그리기에서 또 온다 — 두 방법 다 깨졌다.

       그래서 **한 순간을 재지 않는다.** 칸이 거쳐 간 말을 모두 적어 두고,
       내가 넣은 말이 그중에 있는지 · 같은 말이 두 번 적혔는지를 본다.
       끼어드는 말이 있어도 흔들리지 않는다. */
    await p.evaluate(() => {
      window.__saidLog = [];
      const el = document.getElementById('sr');
      new MutationObserver(() => {
        const t = el.textContent;
        if (t && window.__saidLog[window.__saidLog.length - 1] !== t) window.__saidLog.push(t);
      }).observe(el, { childList: true, characterData: true, subtree: true });
    });
    const 거쳐간말 = async (fn) => {
      await p.evaluate(fn);
      await p.waitForTimeout(160);
      return p.evaluate(() => window.__saidLog.slice());
    };

    const L1 = await 거쳐간말(() => say('첫 말'));
    chk('말을 적는다', L1.includes('첫 말'), true);
    /* 같은 말을 되풀이하면 낭독기가 쉬지 않고 떠들어 급한 말이 묻힌다.
       ⚠ 거르는 것은 **연달아 같은 말**이지 '한 번이라도 한 말' 이 아니다.
         처음에는 두 번을 따로 불러 세었는데, 그 사이에 화면이 실패 안내를
         끼워 넣으면 두 번째가 **제대로** 다시 말한다 — 검사가 다섯 번에 세 번
         깨졌다. 틀린 것을 묻고 있었던 것이다.
         끼어들 틈이 없게 **한 번에 두 번** 부른다. */
    const L2 = await 거쳐간말(() => { say('되풀이 말'); say('되풀이 말'); });
    chk('연달아 같은 말은 한 번만 적는다',
        L2.filter(x => x === '되풀이 말').length, 1);
    const L3 = await 거쳐간말(() => { say('앞말'); say('뒷말'); });
    chk('다른 말은 적는다', L3.includes('뒷말'), true);
    /* 못 불러왔다는 말은 반드시 들려야 한다. 눈으로 보는 사람에게는 붉은 칸이
       뜨지만, 낭독기는 화면 아무 데나 새로 생긴 글을 저절로 읽지 않는다. */
    const L4 = await 거쳐간말(() => note('dashNote', '시트를 못 불러왔습니다', true));
    chk('실패는 반드시 들린다', L4.includes('시트를 못 불러왔습니다'), true);
    /* 성공은 조용해도 된다 — 눈앞에 이미 결과가 있다. */
    const L5 = await 거쳐간말(() => note('dashNote', '그냥 안내입니다', false));
    chk('보통 안내까지 떠들지는 않는다', L5.includes('그냥 안내입니다'), false);

    console.log('\n── 색·모양으로만 말하는 자리가 없는가 ──');
    /* 자료 표의 '있다/없다' 점은 색약인 눈을 위해 **모양**으로도 갈라 두었다
       (채움 · 반채움 · 빈칸). 그런데 낭독기에게는 모양도 색도 안 보인다 —
       `<i>` 에 title 만 붙어 있어서 그 칸이 통째로 아무 말도 안 했다. */
    await p.evaluate(() => show('mat'));
    await p.waitForFunction(
      () => document.querySelectorAll('.dots').length > 0, null, { timeout: 10000 });
    const dots = await p.evaluate(() => {
      const d = [...document.querySelectorAll('.dots')];
      return {
        칸: d.length,
        이름없는칸: d.filter(x => !x.getAttribute('aria-label')).length,
        보기: d.length ? d[0].getAttribute('aria-label') : '',
        속점가려짐: d.length
          ? [...d[0].querySelectorAll('i')].every(i => i.getAttribute('aria-hidden') === 'true')
          : false,
      };
    });
    console.log(`  점 칸 ${dots.칸}개 · 첫 칸이 하는 말: "${dots.보기}"`);
    /* 칸이 아예 안 그려졌으면 아래 둘은 늘 통과다 — 안 재고 지나가는 것을 막는다. */
    chk('자료 탭에 점 칸이 실제로 그려졌다', dots.칸 > 0, true);
    chk('점 칸이 전부 말을 한다', dots.이름없는칸, 0);
    chk('점 하나하나는 낭독기에서 가린다', dots.속점가려짐, true);
    /* 반 표의 상태는 색 말고 **글자**로도 적혀 있어야 한다(미응시·재시 대기·통과·아직). */
    const tags = await p.evaluate(() => {
      const src = [...document.querySelectorAll('script')].map(s => s.textContent).join('\n');
      return /CLS_LABEL\[st\]/.test(src);
    });
    chk('반 표의 상태에 글자 이름이 붙는다', tags, true);

    console.log('\n── 창구가 죽었을 때 정직하게 말하는가 ──');
    /* 여태는 DT 명단이 실패했을 때만 알렸고, 그 문구가 "나머지 숫자는
       정상입니다" 였다. 창구를 다 끊고 재어 보니 다섯이 함께 죽는데 **하나만
       대고, 그러고는 나머지가 멀쩡하다고 했다** — 미응시·미완료 칸도 '—' 인데
       정상이라고 한 것이다. 못 믿을 자를 옆에 두면 진짜 경고도 안 읽힌다. */
    const dead = await p.evaluate(() => {
      dashDead('반 명단', '연결 실패');
      dashDead('통과', '연결 실패');
      return (document.getElementById('dashNote') || {}).innerText || '';
    });
    console.log('  ' + dead.replace(/\s+/g, ' ').trim());
    chk('죽은 창구를 하나도 빠뜨리지 않고 댄다',
        dead.includes('반 명단') && dead.includes('통과'), true);
    chk('멀쩡하다고 거짓말하지 않는다', /나머지 숫자는 정상/.test(dead), false);
    /* 받침을 보고 조사를 고른다 — "DT 통과을" 이 실제로 화면에 떴다. */
    chk('조사가 맞다', /통과를/.test(dead), true);
    /* ⚠ 이 화면은 창구를 막아 둔 채 열었으므로 미완료·미응시도 이미 죽어
       있다. 둘만 되살리고 "치웠나" 를 물으면 검사가 틀린 것을 묻는 셈이다 —
       처음에 그렇게 짰다가 걸렸다. **살아 있는 것이 하나도 없을 때** 치우는지
       본다. 하나라도 남아 있으면 그 이름은 계속 떠 있어야 한다. */
    const 남음 = await p.evaluate(() => {
      dashAlive('반 명단');
      return (document.getElementById('dashNote') || {}).innerText || '';
    });
    chk('하나 살아나도 나머지는 계속 뜬다',
        !남음.includes('반 명단') && 남음.includes('통과'), true);
    const back = await p.evaluate(() => {
      ['재시 대기', '시험 미응시', '통과'].forEach(n => dashAlive(n));
      return (document.getElementById('dashNote') || {}).innerText || '';
    });
    chk('다 살아나면 경고를 치운다', back.trim(), '');

    console.log('\n── 빈 자리·잘린 자리가 다음 할 일을 말하는가 ──');
    /* "없습니다" 로 끝나면 선생님은 다음에 뭘 해야 할지 모른다. 셋 다 다른
       할 일로 이어진다 — 시트와 맞추기 · DT 명단 관리 · 걸러 보기 풀기. */
    const 빈말 = await p.evaluate(() => {
      const src = [...document.querySelectorAll('script')].map(s => s.textContent).join('\n');
      return {
        명단없음: /명단이 비어 있습니다 — .*연결 상태/.test(src),
        반없음: /반 명단이 비어 있습니다 — .*명단 관리/.test(src),
        회차없음: /아직 채점한 회차가 없습니다 — /.test(src),
        기록없음: /파이널 채점 기록이 없습니다 — /.test(src),
        거른뒤없음: /이 조건에 맞는 학생이 없습니다 — /.test(src),
      };
    });
    chk('빈 상태가 다음 할 일까지 말한다', 빈말,
        { 명단없음: true, 반없음: true, 회차없음: true, 기록없음: true, 거른뒤없음: true });

    /* 40줄에서 자르는데 자른 줄을 안 알리면 "두 명뿐이네" 가 된다. */
    const cap = await p.evaluate(() => {
      const many = Array.from({ length: 45 }, (_, i) => ({ name: 'ㄱ' + i }));
      const few = Array.from({ length: 40 }, (_, i) => ({ name: 'ㄱ' + i }));
      return { 넘칠때: capNote(many), 안넘칠때: capNote(few) };
    });
    chk('40줄을 넘기면 잘랐다고 알린다',
        /45명/.test(cap.넘칠때) && /학생<\/b> 탭/.test(cap.넘칠때), true);
    chk('안 넘치면 조용하다', cap.안넘칠때, '');

    console.log('\n── 화면에 적어 둔 약속을 지키는가 ──');
    /* 반 탭 안내문에 "이름을 누르면 그 학생 카드가 열립니다" 라고 적혀 있는데
       재어 보니 **안 열렸다.** 열리는 것은 오른쪽 끝의 '카드' 단추뿐이었다 —
       학생 탭·회차 창에서는 줄을 누르면 열리는데 반 탭만 달랐다.
       적어 놓고 안 지키는 약속은 없느니만 못하다. */
    const 약속 = await p.evaluate(() => {
      const hint = (document.querySelector('#p-cls .hint') || {}).textContent || '';
      const src = [...document.querySelectorAll('script')].map(s => s.textContent).join('\n');
      return {
        적어둠: /이름을 누르면 그 학생 카드가 열립니다/.test(hint),
        이름이누르는자리: /class="nm asname" data-clsrow=/.test(src),
        처리기가받는다: /closest\('\.mini\[data-clsact\],\[data-clsrow\]'\)/.test(src),
      };
    });
    chk('반 탭이 그 약속을 적어 두고 있다', 약속.적어둠, true);
    chk('이름이 실제로 누르는 자리다', 약속.이름이누르는자리, true);
    chk('누르면 카드가 열리는 자리로 이어진다', 약속.처리기가받는다, true);

    console.log('\n── 팔레트가 하루 일을 찾아 주는가 ──');
    /* 팔레트로 하루 일 스무 가지를 찾아 보니 **넷을 못 찾았다**(2026-08-09):
       상담 · 미응시 · 통과 · 수업 문자. 학생·반·회차·자료·화면은 다 드는데
       **할 일**은 하나도 안 들어 있었다 — 정작 매일 하는 쪽이다. */
    const pal = await p.evaluate(async () => {
      const 찾을것 = ['미응시', '재시', '통과', '상담', '수업 문자',
                      '개념', '합쳐야', '대시보드', '자료', '수입'];
      const out = {};
      for (const q of 찾을것) {
        if (!document.getElementById('pal').open) openPal();
        const inp = document.getElementById('palIn');
        inp.value = q; inp.dispatchEvent(new Event('input'));
        await new Promise(r => setTimeout(r, 90));
        out[q] = document.querySelectorAll('#palList .row').length;
      }
      const d = document.getElementById('pal'); if (d.open) d.close();
      return out;
    });
    const 못찾음 = Object.entries(pal).filter(([, v]) => v === 0).map(([k]) => k);
    console.log('  ' + Object.entries(pal).map(([k, v]) => k + ':' + v).join(' · '));
    chk('하루 일을 다 찾아 준다', 못찾음, []);
    /* ⚠ 이름을 팔레트에 **베껴 쓰면** 한쪽만 고쳐져 없는 자리를 가리킨다.
       대시보드의 할 일 칸(JUMPS)을 그대로 든다. */
    const 베낌 = await p.evaluate(() => {
      const src = [...document.querySelectorAll('script')].map(s => s.textContent).join('\n');
      return /JUMPS\.forEach\(function\(j\)\{[\s\S]{0,200}label:j\.label/.test(src);
    });
    chk('할 일 이름을 베끼지 않고 든다', 베낌, true);

    console.log('\n── 이 숫자가 어디까지의 숫자인지 적는가 ──');
    /* 이 문장은 대시보드에만 있었다. 그런데 **학생 탭과 반 탭도** 파이널 회차
       수와 성적을 보여 준다 — 그것은 이 브라우저에 쌓인 기록이라, 다른 기기에서
       채점한 것은 시트와 맞추기 전까지 없다. 재어 보니 일곱 탭 가운데 그 문장이
       붙은 것은 대시보드와 회차 둘뿐이었다.
       ⚠ 문장을 베끼지 않는다 — `sourceLine()` 하나가 만들고 나눠 건다. */
    const 출처 = await p.evaluate(async () => {
      const out = {};
      for (const t of ['dash', 'stu', 'cls']) {
        show(t);
        await new Promise(r => setTimeout(r, 300));
        const pane = document.getElementById('p-' + t);
        out[t] = /시트|브라우저 기록|맞춘 지|받아오는 중/.test(pane.innerText || '');
      }
      return out;
    });
    chk('숫자를 보여 주는 탭이 출처를 적는다', 출처, { dash: true, stu: true, cls: true });
    const 한벌 = await p.evaluate(() => {
      const src = [...document.querySelectorAll('script')].map(s => s.textContent).join('\n');
      return /querySelectorAll\('\.srcnote'\)/.test(src) &&
             (src.match(/이 브라우저 기록만<\/b>일 수 있습니다/g) || []).length === 1;
    });
    chk('출처 문장을 한곳에서만 만든다', 한벌, true);

    /* 또래와 크게 벗어난 점수(MAD)는 **몇 명 중의 중앙값인지**를 같이 말해야
       한다. 다섯 명으로 잰 중앙값은 흔들린다 — 표본을 감추면 숫자만 남는다. */
    const mad = await p.evaluate(() => {
      const src = [...document.querySelectorAll('script')].map(s => s.textContent).join('\n');
      return /같이 본 '\+x\.n\+'명 중앙값/.test(src);
    });
    chk('또래 대비 경고에 표본 크기가 붙는다', mad, true);

    console.log('\n── 일괄로 되는 일과 한 명씩만 되는 일 ──');
    /* 문자는 일괄인데 **미루기는 한 명씩**이었다. 시험 주간처럼 반째로 미루는
       날에는 열두 번을 눌러야 했다 — 일괄로 문자를 보내는 손놀림과 갈렸다.
       ⚠ 어느 줄이 '일괄' 에 드는지는 **한곳에서만** 정해야 한다(`bulkRows`).
         문자와 미루기가 서로 다른 목록을 보면 "다 보냈는데 왜 남아 있지" 가 된다. */
    const 일괄 = await p.evaluate(() => {
      const src = [...document.querySelectorAll('script')].map(s => s.textContent).join('\n');
      return {
        한곳에서정한다: /function bulkRows\(kind\)\{/.test(src),
        문자가그걸쓴다: /copyBulk\(b, b\.dataset\.bulk, bulkRows\(b\.dataset\.bulk\)\)/.test(src),
        미루기도그걸쓴다: /data-bulksnz[\s\S]{0,400}bulkRows\(kind\)/.test(src),
        /* 이미 보낸 것을 미루면 목록에서 사라져 보낸 사실을 확인할 자리가 없어진다. */
        남은것만: /bulkRows\(kind\)\.filter\(function\(r\)\{\s*return !SENT\.has\(r\.key\) && !isSnoozed\(r\.key\)/.test(src),
        /* 낱개와 일괄이 같은 길로 나간다 — 갈라 두면 한쪽만 고쳐진다. */
        같은길: (src.match(/snoozeOne\(/g) || []).length >= 3,
      };
    });
    chk('일괄에 드는 줄을 한곳에서 정한다', 일괄.한곳에서정한다, true);
    chk('일괄 문자가 그것을 쓴다', 일괄.문자가그걸쓴다, true);
    chk('일괄 미루기도 그것을 쓴다', 일괄.미루기도그걸쓴다, true);
    chk('이미 보낸 것은 안 미룬다', 일괄.남은것만, true);
    chk('낱개와 일괄이 같은 길로 나간다', 일괄.같은길, true);

    console.log('\n── 새면 곤란한 것을 무엇이 막고 있는가 ──');
    /* 성적표 화면은 **한 학생**이 뜨지만 통합 셸은 **반 명단 전부**가 뜬다 —
       이름·학교·학년·점수, 그리고 반별 수입까지. 그런데 `tools/noindex.py` 의
       목록에 허브가 **없었다**(2026-08-09). 첫 화면 잠금은 코드가 소스에 그대로
       있는 '문고리' 라(그렇게 적혀 있다), 남는 보호막은 주소를 남이 모른다는 것
       하나뿐이다 — 그 주소가 검색에 잡히면 보호막이 통째로 사라진다. */
    const 막는것 = await p.evaluate(() => {
      const m = document.querySelector('meta[name="robots"]');
      return {
        검색에서뺐나: !!(m && /noindex/i.test(m.getAttribute('content') || '')),
        따라가지도않나: !!(m && /nofollow/i.test(m.getAttribute('content') || '')),
      };
    });
    chk('허브가 검색 목록에 안 오른다', 막는것.검색에서뺐나, true);
    chk('링크도 따라가지 않게 한다', 막는것.따라가지도않나, true);
    /* 잠금은 **한 번만** 묻는다. 얹은 앱 다섯이 각자 또 물으면 화면이 여러
       겹으로 잠긴다 — 열쇠칸을 같이 쓰기로 한 까닭이다. */
    await p.evaluate(() => { ['exam', 'dt', 'dtp', 'dtr', 'km'].forEach(t => show(t)); });
    /* 얹은 창 다섯이 다 붙을 때까지 — 고정 대기를 쓰지 않는다. */
    await p.waitForFunction(
      () => document.querySelectorAll('.pane.frame iframe').length === 5,
      null, { timeout: 15000 }).catch(() => {});
    const 얹은수 = await p.evaluate(() => {
      show('dash');
      return document.querySelectorAll('.pane.frame iframe').length;
    });
    chk('앱 다섯을 얹는다', 얹은수, 5);
    let 또묻는창 = 0;
    for (const f of p.frames()) {
      if (f === p.mainFrame()) continue;
      try { if (await f.evaluate(() => !!document.querySelector('#gateGo'))) 또묻는창++; }
      catch (e) { /* 아직 안 뜬 창은 넘어간다 */ }
    }
    chk('얹은 창이 잠금을 또 묻지 않는다', 또묻는창, 0);

    console.log('\n── 한 뜻에 한 이름인가 ──');
    /* 이 목록은 **세 이름**으로 불리고 있었다 — 카드는 'DT 미완료', 할 일 칩은
       '재시 대기', 자리 제목은 '손이 필요한 것'. 선생님은 카드를 보고 칩을 눌러
       그 자리로 오는데 셋이 다 달랐다. 칩과 반 표가 이미 쓰던 '재시 대기' 로 모았다.
       실패 안내도 카드 이름을 쓴다 — 카드는 '재시 대기' 인데 안내가 'DT 미완료'
       라고 하면 둘을 잇지 못한다. */
    await p.evaluate(() => show('dash'));
    await p.waitForFunction(
      () => document.querySelector('#dashCards .card b#pdCnt'), null, { timeout: 8000 });
    const 이름 = await p.evaluate(() => {
      const card = [...document.querySelectorAll('#dashCards .card')]
        .filter(c => (c.querySelector('b') || {}).id === 'pdCnt')[0];
      return {
        카드: card ? (card.querySelector('span') || {}).textContent : '',
        제목: (document.querySelector('#pendWrap h2') || {}).textContent || '',
        칩: (() => {
          const src = [...document.querySelectorAll('script')].map(s => s.textContent).join('\n');
          const m = src.match(/id:'pendWrap',\s*label:'([^']+)'/);
          return m ? m[1] : '';
        })(),
      };
    });
    console.log(`  카드 "${이름.카드}" · 칩 "${이름.칩}" · 제목 "${이름.제목}"`);
    chk('카드·칩·제목이 한 이름이다',
        [이름.카드, 이름.칩, 이름.제목], ['재시 대기', '재시 대기', '재시 대기']);
    /* 옛 이름이 되살아나면 잡는다. 연결 칩(창구 이름)에는 남아 있어도 된다 —
       그쪽은 "어느 창구가 대답했나" 라서 다른 축이다. */
    const 옛이름 = await p.evaluate(() => {
      const t = document.body.innerText;
      return { 손이필요한것: /손이 필요한 것/.test(t) };
    });
    chk('옛 이름이 화면에 안 남았다', 옛이름.손이필요한것, false);

    console.log('\n── 주소를 붙여 넣으면 그 화면이 열리는가 ──');
    /* 주소를 **쓰기만 하고 읽지는 않고** 있었다(첫 화면에서 한 번 빼고).
       이미 열려 있는 셸의 주소창에 `#cls?c=…` 를 붙여 넣어도 아무 일이 없었다 —
       링크를 받아 쓰는 흔한 자리다. `hashchange` 를 듣게 했다.
       ⚠ 되돌이가 안 나는 까닭: `writeHash` 는 `replaceState` 를 쓰고, 그것은
         `hashchange` 를 안 일으킨다. 사람이 바꿀 때만 온다. */
    const 붙여넣기 = [];
    for (const h of ['#cls', '#mat?g=lec', '#stu?f=noexam', '#dash']) {
      await p.evaluate(x => { location.hash = x; }, h);
      await p.waitForFunction(want => {
        const on = (document.querySelector('.pane.on') || {}).id || '';
        return on === 'p-' + want;
      }, h.replace(/^#/, '').split('?')[0], { timeout: 5000 }).catch(() => {});
      붙여넣기.push(h + '→' + ((await p.evaluate(() =>
        (document.querySelector('.pane.on') || {}).id)) || ''));
    }
    console.log('  ' + 붙여넣기.join(' · '));
    chk('붙여 넣은 주소대로 열린다', 붙여넣기,
        ['#cls→p-cls', '#mat?g=lec→p-mat', '#stu?f=noexam→p-stu', '#dash→p-dash']);
    /* 걸러 보기까지 따라와야 링크 한 줄이 '저장된 보기' 노릇을 한다. */
    const 딸린것 = await p.evaluate(() => ({ 갈래: MAT_PICK, 거르개: STU_FILTER }));
    chk('걸러 보기도 주소에서 되살아난다', 딸린것, { 갈래: 'lec', 거르개: 'noexam' });

    chk('콘솔에 예외가 없다', errs, []);
  } finally {
    await browser.close();
  }

  /* ── 그림이 유일한 통로가 되면 안 된다 ────────────────────────────────
     띠 안의 분자와 반별 3D 는 **덤**이다. WebGL 이 없는 기기(오래된 노트북 ·
     그래픽 드라이버가 막힌 회사 PC · 원격 화면)에서는 안 그려지는데, 그때
     **할 수 없게 되는 일이 있으면 결함**이다. 주석에 그렇게 적어 두었으니
     실제로 그런지 재어 둔다. */
  console.log('\n── WebGL 이 없어도 같은 일이 되는가 ──');
  const noGl = seal(await chromium.launch(Object.assign(
    { args: ['--no-sandbox', '--disable-webgl', '--disable-3d-apis'] },
    CHROMIUM ? { executablePath: CHROMIUM } : {})));
  try {
    const c2 = await noGl.newContext({ viewport: { width: 1280, height: 1400 }, serviceWorkers: 'block' });
    const p2 = await c2.newPage();
    const errs2 = [];
    p2.on('pageerror', e => errs2.push(String(e).slice(0, 120)));
    await p2.addInitScript(() => {
      try { localStorage.setItem('chemistreal:gate', String(Date.now())); } catch (e) {}
    });
    await p2.route('**/DT/**', r => r.fulfill({
      status: 200, contentType: 'text/html; charset=utf-8', body: '<!doctype html>' }));
    await p2.goto(`http://localhost:${PORT}/hub.html`, { waitUntil: 'domcontentloaded' });
    await p2.waitForFunction(() => typeof show === 'function', null, { timeout: 20000 });
    await p2.waitForFunction(
      () => document.querySelectorAll('#dashCards .card').length > 0, null, { timeout: 10000 });
    const g = await p2.evaluate(() => {
      let has = false;
      try { has = !!document.createElement('canvas').getContext('webgl'); } catch (e) {}
      return {
        webgl: has,
        띠그림: !!document.querySelector('.brand canvas'),
        반3D: !!document.querySelector('#dash3d canvas'),
        /* 그림이 없어도 남아야 하는 것들 */
        급한칸: document.querySelectorAll('#dashCards .card').length,
        탭: document.querySelectorAll('[role="tab"]').length,
        제목: (document.querySelector('.brand h1') || {}).textContent,
      };
    });
    console.log(`  webgl ${g.webgl ? '있음' : '없음'} · 띠 그림 ${g.띠그림 ? '그림' : '없음'} · 반 3D ${g.반3D ? '그림' : '없음'}`);
    chk('이 브라우저에는 WebGL 이 없다(검사가 헛돌지 않는다)', g.webgl, false);
    chk('없으면 조용히 안 그린다', [g.띠그림, g.반3D], [false, false]);
    chk('화면은 그대로 산다', g.급한칸 > 0 && g.탭 === 12, true);
    chk('제목도 그대로다', g.제목, 'Chemistreal 통합관리');
    chk('WebGL 이 없다고 화면이 터지지 않는다', errs2, []);
  } finally {
    await noGl.close();
    srv.stop();
  }

  console.log(fail ? `\nFAIL ${fail}건` : '\nPASS');
  process.exit(fail ? 1 : 0);
})().catch(e => { console.error(e); process.exit(1); });
