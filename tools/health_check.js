#!/usr/bin/env node
/* ============================================================
   세 앱의 창구가 실제로 대답하는지 확인한다
   ------------------------------------------------------------
   DT 는 한 해 내내 대답하지 않고 있었다. 통합 셸이 JSONP 로 부르는데 저쪽이
   콜백을 무시하고 순수 JSON 을 줘서, 받는 쪽 브라우저가 그걸 자바스크립트로
   실행하려다 죽었다. 화면에는 '…' 와 '—' 만 남았고, 그게 '아직 불러오는 중'
   인지 '고장' 인지 알 길이 없어 아무도 눈치채지 못했다.

   사람이 화면을 봐야 아는 고장은 안 고쳐진다. 기계가 매일 본다.

   여기서 보는 것 — 셸이 실제로 부르는 방식 그대로다:
     · 응답이 오는가 (시간 초과 아닌가)
     · **JSONP 로 감싸 주는가** (이것 하나가 그 한 해를 만들었다)
     · 감싼 안쪽이 ok:true 인가
     · 셸이 읽는 열쇠가 실제로 들어 있는가

   개인 정보는 찍지 않는다 — 로그는 공개된 곳에 남는다.

   ── 같은 소식을 두 번 말하지 않는다 ──────────────────────────────
   매일 도는 검사가 매일 실패하면, 깃허브가 매일 아침 메일을 보낸다. 그런데
   이틀째부터 그 메일에는 **새 소식이 없다.** 새 소식이 없는 알림이 쌓이면
   사람이 알림을 안 보게 되고, 그러면 진짜가 와도 안 본다 — 알림을 켠 뜻이
   사라진다. 실제로 배포 열쇠가 죽은 이틀 동안 같은 메일이 두 번 왔다.

   그래서 지난번 결과를 들고 있다가 **바뀐 것만** 빨간불로 낸다.

     처음 고장 났다        → 빨간불 (메일)
     어제도 그랬다         → 초록불 + 경고 줄 (메일 없음)
     이레가 지나도 그대로  → 빨간불 한 번 더 (잊지 않게)
     고쳐졌다              → 초록불, 통나무에만 적는다

   지난번 결과는 --state 파일에 담는다. 파일이 없으면 '처음' 으로 친다 —
   한 번은 더 알리게 되지만, 조용히 넘기는 것보다 낫다.

   실행:  node tools/health_check.js [--state <파일>]
          DEPLOY_KEY=ok|dead|unset  배포 열쇠 판정을 밖에서 받는다(선택)
   ============================================================ */
'use strict';

const fs = require('fs');

const QUIET_DAYS = 7;      // 같은 고장을 다시 짚기까지

/* 지난번과 견줘 **알릴 것이 있는지**만 정한다. 다른 것은 아무것도 안 한다 —
   그래야 검사가 이 판단을 창구 없이 그대로 확인할 수 있다. */
function decide(prev, bad, now) {
  const prevBad = (prev && prev.bad) || {};
  const nowIso = new Date(now).toISOString();
  const fresh = bad.filter(function (n) { return !(n in prevBad); });

  const lastAlert = prev && prev.alertedAt ? Date.parse(prev.alertedAt) : 0;
  const stale = bad.length > 0 && lastAlert > 0 &&
                (now - lastAlert) >= QUIET_DAYS * 86400000;

  const ring = fresh.length > 0 || stale;
  const nextBad = {};
  bad.forEach(function (n) { nextBad[n] = prevBad[n] || nowIso; });

  return {
    ring: ring,
    fresh: fresh,
    why: fresh.length ? '새로 고장났다'
       : stale ? '고장이 이레 넘게 이어진다'
       : bad.length ? '어제도 그랬다 — 다시 알리지 않는다'
       : '모두 정상',
    state: {
      at: nowIso,
      bad: nextBad,
      /* 고친 뒤에는 지워 둔다. 다음에 무엇이 깨지든 곧바로 알리게 된다. */
      alertedAt: !bad.length ? null : (ring ? nowIso : (prev && prev.alertedAt) || nowIso),
    },
  };
}

module.exports = { decide: decide, QUIET_DAYS: QUIET_DAYS };

const EP = {
  파이널: 'https://script.google.com/macros/s/AKfycbxGmSCkip0cQCyOH_JA2SiAMSxri00XObLmHyXlyXwxhG7u7w-x0FH02VN4DQySiUsv9Q/exec',
  DT:     'https://script.google.com/macros/s/AKfycbzvFaPXgEgCBQ8HowtP8tPTtdiIVFtmZSUf0KFXUOVOh3ektrFMkz4KSR4I52LDBzB8rw/exec',
  KMChC:  'https://script.google.com/macros/s/AKfycbxdD_pKlNZaHyce2mUsDcmTspMW4uh--wOr3MggvDABEDs7n64re6DLYEVOlh8ANE9-/exec',
};

/* 셸이 부르는 창구를 그대로. key 는 응답에 반드시 있어야 하는 열쇠다. */
const CHECKS = [
  { app: '파이널', action: 'all',       key: 'rows' },
  { app: 'DT',     action: 'names',     key: 'classes' },
  { app: 'DT',     action: 'pending',   key: 'pending' },
  { app: 'DT',     action: 'passed',    key: 'passed' },
  { app: 'DT',     action: 'absentees', key: 'absentees' },
  { app: 'DT',     action: 'cohortmis', key: 'rows' },
  { app: 'KMChC',  action: 'names',     key: 'students' },
];

const CB = '__health';
const TIMEOUT = 25000;

async function ask(app, action) {
  const url = EP[app] + '?action=' + encodeURIComponent(action) + '&callback=' + CB;
  const ac = new AbortController();
  const t = setTimeout(() => ac.abort(), TIMEOUT);
  try {
    const r = await fetch(url, { signal: ac.signal, redirect: 'follow' });
    return { status: r.status, text: await r.text() };
  } finally { clearTimeout(t); }
}

function arg(flag) {
  const i = process.argv.indexOf(flag);
  return i > 0 ? process.argv[i + 1] : null;
}
function readState(path) {
  if (!path) return null;
  try { return JSON.parse(fs.readFileSync(path, 'utf8')); } catch (e) { return null; }
}
function writeState(path, st) {
  if (!path) return;
  try { fs.writeFileSync(path, JSON.stringify(st, null, 2) + '\n'); } catch (e) {}
}
/* 실행 요약(초록불이어도 보이는 자리)에 늘 적어 둔다. 메일이 안 오는 대신
   여기는 채워 두어야, 궁금할 때 한 곳만 열면 된다. */
function summary(lines) {
  const f = process.env.GITHUB_STEP_SUMMARY;
  if (!f) return;
  try { fs.appendFileSync(f, lines.join('\n') + '\n'); } catch (e) {}
}

/* 검사에서 require 로 불러 판단 규칙만 확인한다 — 그때 창구를 두드리면 안 된다. */
if (require.main === module) (async () => {
  const bad = [];
  for (const c of CHECKS) {
    const name = c.app + ' · ' + c.action;
    let res;
    try { res = await ask(c.app, c.action); }
    catch (e) {
      bad.push({ name: name, why: '응답 없음 (' + (e.name === 'AbortError' ? '시간 초과' : e.message) + ')' });
      console.log('  ✗ ' + name + ' — 응답 없음'); continue;
    }
    if (res.status !== 200) {
      bad.push({ name: name, why: 'HTTP ' + res.status });
      console.log('  ✗ ' + name + ' — HTTP ' + res.status); continue;
    }
    const body = res.text.trim();
    /* 여기가 이 검사의 이유다. 콜백으로 안 감싸면 셸의 <script> 가 이 응답을
       자바스크립트로 실행하려다 죽는다 — 저쪽은 200 을 주고 있어서 겉으로는
       멀쩡해 보인다. */
    if (!body.startsWith(CB + '(')) {
      bad.push({ name: name, why: 'JSONP 로 안 감쌌다 (셸이 못 읽는다)' });
      console.log('  ✗ ' + name + ' — JSONP 로 안 감쌌다'); continue;
    }
    let j;
    try { j = JSON.parse(body.slice(CB.length + 1).replace(/\);?$/, '')); }
    catch (e) { bad.push({ name: name, why: '감싼 안쪽이 JSON 이 아니다' });
                console.log('  ✗ ' + name + ' — 안쪽이 JSON 이 아니다'); continue; }
    if (!j || j.ok !== true) {
      bad.push({ name: name, why: 'ok:true 가 아니다 (' + ((j && j.error) || '이유 없음') + ')' });
      console.log('  ✗ ' + name + ' — ok 가 아니다'); continue;
    }
    if (!(c.key in j)) {
      bad.push({ name: name, why: "'" + c.key + "' 열쇠가 없다 (셸이 읽는 자리다)" });
      console.log('  ✗ ' + name + " — '" + c.key + "' 없음"); continue;
    }
    // 개인 정보는 찍지 않는다. 크기만 적는다.
    const v = j[c.key];
    const size = Array.isArray(v) ? v.length + '건'
               : (v && typeof v === 'object') ? Object.keys(v).length + '항목' : '있음';
    console.log('  ✓ ' + name + ' · ' + size);
  }

  /* 배포 열쇠 판정은 밖(워크플로)에서 받는다 — 여기서 clasp 를 부르지 않는다. */
  const key = process.env.DEPLOY_KEY || '';
  if (key === 'dead') {
    bad.push({ name: '배포 열쇠',
      why: 'clasp 인증 만료(invalid_grant) — .gs 를 고쳐도 앱스크립트에 안 올라간다' });
    console.log('  ✗ 배포 열쇠 — 만료');
  } else if (key === 'unset') {
    console.log('  · 배포 열쇠 — 시크릿 미설정(건너뜀)');
  } else if (key === 'ok') {
    console.log('  ✓ 배포 열쇠 · 살아 있음');
  }

  const statePath = arg('--state');
  const d = decide(readState(statePath), bad.map(b => b.name), Date.now());
  writeState(statePath, d.state);

  const lines = ['## 앱 창구 점검', ''];
  if (bad.length) {
    console.log('\n대답하지 않는 곳 ' + bad.length + '개:');
    bad.forEach(b => console.log('  · ' + b.name + ' — ' + b.why));
    console.log('\n이 상태면 통합 셸(hub.html)의 해당 칸이 비어 있습니다.');
    lines.push('대답하지 않는 곳 **' + bad.length + '개**', '');
    bad.forEach(b => lines.push('- `' + b.name + '` — ' + b.why));
  } else {
    console.log('\n모든 창구 정상 (' + CHECKS.length + '개)');
    lines.push('모든 창구 정상 (' + CHECKS.length + '개)');
  }
  lines.push('', '_' + d.why + '_');
  summary(lines);

  if (d.ring) {
    /* ::error:: 를 붙여야 실행 화면 맨 위에 뜬다. 메일 본문에도 이 줄이 간다. */
    console.log('::error title=앱 창구 점검::' + d.why + ' — ' +
                bad.map(b => b.name).join(', '));
    process.exit(1);
  }
  if (bad.length) {
    /* 빨간불은 안 낸다(=메일이 안 간다). 그래도 실행 화면에는 노란 줄로 남는다. */
    console.log('::warning title=아직 고장난 채::' + bad.map(b => b.name).join(', ') +
                ' — 이미 알린 것이라 다시 알리지 않습니다(' + QUIET_DAYS + '일 뒤 한 번 더).');
  }
})().catch(e => { console.error('점검 자체가 실패:', e.message); process.exit(1); });
