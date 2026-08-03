#!/usr/bin/env node
/* ============================================================
   저장소에 있는 것과 **실제로 서비스되는 것**이 같은가
   ------------------------------------------------------------
   2026-08-03 하루에 같은 모양의 사고가 다섯 번 났다.

     · 자동 커밋이 데이터를 지웠는데 아무도 안 밀어서 네 시간 몰랐다
     · tools/ 를 고친 PR 이 paths 목록에 없어 검사 없이 초록불이었다
     · 배포 열쇠가 죽었는데 .gs 를 안 고치는 동안 아무도 몰랐다
     · demos/·premium/ 폴더가 한 번도 재어진 적이 없었다
     · 성적표 인원 고침을 배포했는데 화면은 옛것이었다

   전부 한 문장이다 — **"고쳤다" 와 "실제로 그렇게 돌고 있다" 사이가 비어
   있었다.** 검사는 저장소 안만 본다. 저장소 안이 아무리 초록불이어도,
   학부모가 여는 화면이 옛 코드면 아무것도 고쳐진 것이 아니다.

   그래서 여기서는 **밖에서** 본다.

     1. 깃허브 페이지가 내주는 화면이 지금 저장소 것과 같은가
     2. 앱스크립트 창구가 살아 있고, 새 코드가 올라가 있는가
     3. 그 창구가 내주는 숫자가 말이 되는가(회차별 인원)

   개인정보는 찍지 않는다 — 로그는 공개된 곳에 남는다. 인원만 센다.

   실행:  node tools/live_check.js [--retry N]
          BASE_URL 로 다른 곳을 볼 수 있다(기본 chemistreal.github.io/exam)

   ⚠ 병합 직후에는 깃허브 페이지가 아직 옛 파일을 내준다(보통 1~2분). 배포
   뒤에 곧바로 돌릴 때는 --retry 를 준다 — 안 그러면 "안 갔다" 고 잘못
   말하고, 그 거짓 빨간불이 쌓이면 진짜가 와도 안 보게 된다.
   ============================================================ */
'use strict';

const fs = require('fs');
const path = require('path');
const crypto = require('crypto');

const ROOT = path.join(__dirname, '..');
const BASE = (process.env.BASE_URL || 'https://chemistreal.github.io/exam').replace(/\/$/, '');
const TIMEOUT = 25000;

let fail = 0;
const chk = (name, ok, why) => {
  console.log((ok ? '  ✓ ' : '  ✗ ') + name + (ok ? '' : '  — ' + why));
  if (!ok) fail++;
};

function sha(text) {
  return crypto.createHash('sha256').update(text, 'utf8').digest('hex').slice(0, 12);
}

async function get(url) {
  const ac = new AbortController();
  const t = setTimeout(() => ac.abort(), TIMEOUT);
  try {
    const r = await fetch(url, { signal: ac.signal, cache: 'no-store' });
    return { status: r.status, text: await r.text() };
  } finally { clearTimeout(t); }
}

/* 저장소의 파일과 서비스되는 파일이 **글자 하나까지** 같은지 본다.
   "새 기능이 들어 있나" 를 문자열로 찾는 방식은 다음 고침 때 또 손대야 한다.
   통째로 견주면 무엇을 고치든 그대로 걸린다. */
const SHIPPED = ['final.html', 'hub.html', 'index.html', 'sw.js', 'exams.json'];

async function once() {
  fail = 0;
  console.log('── 깃허브 페이지가 내주는 것이 저장소 것과 같은가 ──');
  console.log('   ' + BASE);
  for (const rel of SHIPPED) {
    const local = path.join(ROOT, rel);
    if (!fs.existsSync(local)) { chk(rel, false, '저장소에 없다'); continue; }
    let res;
    try { res = await get(BASE + '/' + rel); }
    catch (e) { chk(rel, false, '못 받아 왔다 (' + (e.name === 'AbortError' ? '시간 초과' : e.message) + ')'); continue; }
    if (res.status !== 200) { chk(rel, false, 'HTTP ' + res.status); continue; }
    const want = sha(fs.readFileSync(local, 'utf8'));
    const got = sha(res.text);
    chk(rel + ' · ' + got, want === got,
        '저장소 ' + want + ' ≠ 서비스 ' + got + ' (배포가 아직 안 갔거나 캐시가 남았다)');
  }

  console.log('\n── 앱스크립트 창구 ──');
  const EP = (fs.readFileSync(path.join(ROOT, 'final.html'), 'utf8')
    .match(/const SHEET_ENDPOINT='([^']+)'/) || [])[1];
  if (!EP) { chk('창구 주소를 찾았다', false, 'final.html 에서 SHEET_ENDPOINT 를 못 읽었다'); }
  else {
    /* 새 코드가 올라갔는지는 **새 창구가 대답하는지**로 본다. 배포가 초록불인
       것만으로는 모자란다 — clasp 이 성공해도 웹앱이 옛 판을 내주는 일이 있다. */
    const exams = JSON.parse(fs.readFileSync(path.join(ROOT, 'exams.json'), 'utf8'));
    const base = JSON.parse(fs.readFileSync(path.join(ROOT, 'cohort', 'baseline.json'), 'utf8')).exams || {};
    const want = exams.filter(e => base[e.id]).slice(0, 3).map(e => e.id);
    for (const id of want.length ? want : [exams[0] && exams[0].id]) {
      let res;
      try { res = await get(EP + '?action=cohort&exam=' + encodeURIComponent(id) + '&callback=__c'); }
      catch (e) { chk('cohort · ' + id, false, '응답 없음'); continue; }
      const body = (res.text || '').trim();
      if (!body.startsWith('__c(')) { chk('cohort · ' + id, false, 'JSONP 로 안 감쌌다 — 옛 코드일 수 있다'); continue; }
      let j;
      try { j = JSON.parse(body.slice(4).replace(/\);?$/, '')); }
      catch (e) { chk('cohort · ' + id, false, '안쪽이 JSON 이 아니다'); continue; }
      if (!j || j.ok !== true) { chk('cohort · ' + id, false, 'ok:true 가 아니다'); continue; }
      /* 있어야 할 열쇠가 없으면 옛 판이 돌고 있다는 뜻이다. */
      const miss = ['hist', 'n', 'yhist', 'yn', 'year'].filter(k => !(k in j));
      if (miss.length) { chk('cohort · ' + id, false, '없는 열쇠 ' + miss.join(',') + ' — 배포가 안 갔다'); continue; }
      chk('cohort · ' + id + ' · 누적 ' + j.n + '명 · 올해 ' + j.yn + '명' +
          (j.skipped ? ' · 검사줄 ' + j.skipped + '개 뺌' : ''), true);
    }
  }

  return fail;
}

(async () => {
  const at = process.argv.indexOf('--retry');
  const tries = at > 0 ? Math.max(1, Number(process.argv[at + 1]) || 1) : 1;
  let left = 0;
  for (let i = 1; i <= tries; i++) {
    left = await once();
    if (!left || i === tries) break;
    /* 페이지가 퍼지는 데 시간이 걸린다. 30초씩 기다렸다 다시 본다. */
    console.log(`\n  … ${left}개 어긋남. 30초 뒤 다시 봅니다 (${i}/${tries - 1})`);
    await new Promise(r => setTimeout(r, 30000));
  }
  console.log(left ? `\n실패 ${left}개 — 고친 것이 실제로는 안 갔습니다.`
                   : '\n저장소와 실제 화면이 같습니다.');
  process.exit(left ? 1 : 0);
})().catch(e => { console.error('점검 자체가 실패:', e.message); process.exit(1); });
