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

   실행:  node tools/health_check.js
   ============================================================ */
'use strict';

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

(async () => {
  const bad = [];
  for (const c of CHECKS) {
    const name = c.app + ' · ' + c.action;
    let res;
    try { res = await ask(c.app, c.action); }
    catch (e) {
      bad.push(name + ' — 응답 없음 (' + (e.name === 'AbortError' ? '시간 초과' : e.message) + ')');
      console.log('  ✗ ' + name + ' — 응답 없음'); continue;
    }
    if (res.status !== 200) {
      bad.push(name + ' — HTTP ' + res.status);
      console.log('  ✗ ' + name + ' — HTTP ' + res.status); continue;
    }
    const body = res.text.trim();
    /* 여기가 이 검사의 이유다. 콜백으로 안 감싸면 셸의 <script> 가 이 응답을
       자바스크립트로 실행하려다 죽는다 — 저쪽은 200 을 주고 있어서 겉으로는
       멀쩡해 보인다. */
    if (!body.startsWith(CB + '(')) {
      bad.push(name + ' — JSONP 로 안 감쌌다 (셸이 못 읽는다)');
      console.log('  ✗ ' + name + ' — JSONP 로 안 감쌌다'); continue;
    }
    let j;
    try { j = JSON.parse(body.slice(CB.length + 1).replace(/\);?$/, '')); }
    catch (e) { bad.push(name + ' — 감싼 안쪽이 JSON 이 아니다');
                console.log('  ✗ ' + name + ' — 안쪽이 JSON 이 아니다'); continue; }
    if (!j || j.ok !== true) {
      bad.push(name + ' — ok:true 가 아니다 (' + ((j && j.error) || '이유 없음') + ')');
      console.log('  ✗ ' + name + ' — ok 가 아니다'); continue;
    }
    if (!(c.key in j)) {
      bad.push(name + " — '" + c.key + "' 열쇠가 없다 (셸이 읽는 자리다)");
      console.log('  ✗ ' + name + " — '" + c.key + "' 없음"); continue;
    }
    // 개인 정보는 찍지 않는다. 크기만 적는다.
    const v = j[c.key];
    const size = Array.isArray(v) ? v.length + '건'
               : (v && typeof v === 'object') ? Object.keys(v).length + '항목' : '있음';
    console.log('  ✓ ' + name + ' · ' + size);
  }

  if (bad.length) {
    console.log('\n대답하지 않는 창구 ' + bad.length + '개:');
    bad.forEach(b => console.log('  · ' + b));
    console.log('\n이 상태면 통합 셸(hub.html)의 해당 칸이 비어 있습니다.');
    process.exit(1);
  }
  console.log('\n모든 창구 정상 (' + CHECKS.length + '개)');
})().catch(e => { console.error('점검 자체가 실패:', e.message); process.exit(1); });
