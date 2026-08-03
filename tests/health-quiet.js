/* ============================================================
   같은 소식을 두 번 말하지 않는다
   ------------------------------------------------------------
   매일 도는 점검이 매일 실패하면 매일 아침 메일이 온다. 그런데 이틀째부터
   그 메일에는 **새 소식이 없다.** 새 소식 없는 알림이 쌓이면 사람이 알림을
   안 보게 되고, 그러면 진짜가 와도 안 본다 — 알림을 켠 뜻이 사라진다.
   실제로 배포 열쇠가 죽은 이틀 동안 같은 메일이 두 번 왔다.

   그래서 지키는 것:
   - 처음 고장 나면 알린다
   - 어제도 같은 고장이면 **안 알린다**
   - 고장이 하나 더 늘면 그건 새 소식이니 알린다
   - 이레가 지나도 그대로면 한 번 더 알린다(잊지 않게)
   - 고쳐졌다가 다시 깨지면 다시 알린다 — '이미 알린 것' 으로 남으면 안 된다

   창구를 두드리지 않는다(규칙만 본다).

   실행:  node tests/health-quiet.js
   ============================================================ */
'use strict';
const { decide, QUIET_DAYS } = require('../tools/health_check.js');

let fail = 0;
const chk = (n, got, want) => {
  const ok = JSON.stringify(got) === JSON.stringify(want);
  console.log((ok ? '  PASS  ' : '  FAIL  ') + n +
    (ok ? '' : `  → ${JSON.stringify(got)} (기대 ${JSON.stringify(want)})`));
  if (!ok) fail++;
};

const DAY = 86400000;
const T0 = Date.parse('2026-08-03T22:00:00.000Z');

console.log('── 처음과 그다음 ──');
{
  const d1 = decide(null, ['배포 열쇠'], T0);
  chk('처음 고장 나면 알린다', d1.ring, true);
  chk('무엇이 새것인지 적는다', d1.fresh, ['배포 열쇠']);

  const d2 = decide(d1.state, ['배포 열쇠'], T0 + DAY);
  chk('어제도 그랬으면 안 알린다', d2.ring, false);
  chk('그래도 고장은 들고 있다', Object.keys(d2.state.bad), ['배포 열쇠']);
  /* 언제부터 고장이었는지는 처음 본 날로 남아야 한다 — 매일 갱신하면
     '이레가 지났나' 를 영영 못 센다. */
  chk('처음 본 날을 안 덮는다', d2.state.bad['배포 열쇠'], d1.state.bad['배포 열쇠']);

  const d3 = decide(d2.state, ['배포 열쇠'], T0 + 2 * DAY);
  chk('사흘째도 조용하다', d3.ring, false);
}

console.log('\n── 새 소식이 생기면 ──');
{
  const d1 = decide(null, ['배포 열쇠'], T0);
  const d2 = decide(d1.state, ['배포 열쇠', 'KMChC · names'], T0 + DAY);
  chk('고장이 하나 늘면 알린다', d2.ring, true);
  chk('늘어난 것만 새것', d2.fresh, ['KMChC · names']);
}

console.log('\n── 이레가 지나면 ──');
{
  let st = decide(null, ['배포 열쇠'], T0).state;
  for (let i = 1; i < QUIET_DAYS; i++) {
    const d = decide(st, ['배포 열쇠'], T0 + i * DAY);
    if (d.ring) { chk(`${i}일째는 조용해야 한다`, d.ring, false); }
    st = d.state;
  }
  const last = decide(st, ['배포 열쇠'], T0 + QUIET_DAYS * DAY);
  chk('이레가 지나면 한 번 더 알린다', last.ring, true);
  chk('그 뒤 다시 조용해진다', decide(last.state, ['배포 열쇠'], T0 + (QUIET_DAYS + 1) * DAY).ring, false);
}

console.log('\n── 고쳐졌다가 다시 깨지면 ──');
{
  const d1 = decide(null, ['배포 열쇠'], T0);
  const ok = decide(d1.state, [], T0 + DAY);
  chk('고쳐지면 조용하다', ok.ring, false);
  chk('고장 목록이 빈다', ok.state.bad, {});
  /* 여기서 alertedAt 이 남아 있으면, 다음에 깨졌을 때 '이레가 안 지났다' 는
     이유로 조용히 넘어갈 수 있다. 고쳐진 순간 지워야 한다. */
  chk('알린 기록도 지운다', ok.state.alertedAt, null);
  const again = decide(ok.state, ['배포 열쇠'], T0 + 2 * DAY);
  chk('다시 깨지면 다시 알린다', again.ring, true);
}

console.log('\n── 망가진 기록에도 안 죽는다 ──');
{
  chk('빈 것', decide({}, ['A'], T0).ring, true);
  chk('bad 가 없을 때', decide({ at: 'x' }, ['A'], T0).ring, true);
  chk('alertedAt 이 쓰레기일 때', decide({ bad: { A: 'x' }, alertedAt: '???' }, ['A'], T0).ring, false);
  chk('아무 고장도 없으면 조용', decide(null, [], T0).ring, false);
}

console.log(fail ? `\n${fail}개 실패` : '\n모두 통과');
process.exit(fail ? 1 : 0);
