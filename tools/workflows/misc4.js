export const meta = {
  name: 'misc4',
  description: '한 회차의 선지별 오답 해설을 크롭 원문에서 집필 → 적대적 반박 → 수리',
  phases: [{ title: '집필' }, { title: '반박' }, { title: '수리' }],
}

/* args = { exam: 'hwol-2017', chunks: [{ name:'c01', qs:[1,2,...] }, ...] }
 *
 * 왜 세 단계인가 — 집필만 하면 그림을 잘못 읽은 것이 그대로 학생에게 간다.
 * 반박자에게는 「통과시키는 것이 아니라 틀린 것을 찾는 것이 목적」이라 이르고,
 * 수리하는 사람에게는 「지적을 먼저 직접 확인해라, 반박이 틀렸으면 고치지 말고
 * 적어라」고 이른다. 셋을 다 지나기 전에는 아무것도 답지에 안 들어간다.
 */

const EXAM = args.exam
const CHUNKS = args.chunks
const OUT = '/home/user/exam/answers/_crop'

const RULES = `
■ 무엇을 만드는가
「학생이 왜 **그 선지**를 골랐는가」를 오답 선지마다 한 문단씩 쓴다.

■ 절대 규칙
1. **정답 키를 절대 쓰지 마라.** 결과 JSON 에 answer · acceptableAnswers 를
   넣으면 그 항목 전체가 거부된다. 정답이 무엇인지는 읽되 적지는 않는다.
2. **정답 선지에는 오답 해설을 달지 마라.** misconceptions 의 열쇠는
   오답 선지 번호뿐이다(사지선다면 셋).
3. **지문과 선지는 그림에 있는 그대로 옮겨라.** 지어내지 마라. 첨자·기호도
   그대로(H₂O · Δ · ⁻ · °C). 그림에 없는 원자량·상수를 「주어졌다」고 쓰지 마라.
4. 그림이 안 읽히거나 표·그래프라서 글로 옮길 수 없으면 **그 문항을 통째로
   빼라.** 억지로 지어내는 것보다 빠지는 편이 낫다.

■ 좋은 오답 해설이란 (실제 통과한 예)
  "화학식 속 1 : 5라는 개수비를 질량비로 바꿔 읽어 10.00 g을 여섯 몫으로
   나눈 값이다. 10.00 ÷ 6 = 1.67이 정확히 이 선지가 된다. 개수비는 몰비일
   뿐이라 몰질량을 거쳐야 질량 관계가 나온다."

  · **그 선지의 값이 어떤 잘못된 셈에서 나오는지**를 짚는다. 수치 선지라면
    그 수가 실제로 나오는 계산을 보여라.
  · 「잘 몰라서 틀렸다」 「개념을 혼동했다」 같은 두루뭉술한 말은 쓰지 마라.
  · 두세 문장. 마지막은 바로잡는 한 줄.
`

const results = await pipeline(
  CHUNKS,
  c => agent(
`화학 시험지 원문을 읽고 선지별 오답 해설을 쓴다.

시험: ${EXAM} · 문항 ${c.qs.join(', ')}

1) 문항마다 그림을 읽어라:
   /home/user/exam/crops/${EXAM}/<번호>.png
   (Read 도구로 열면 그림이 보인다. 지문·선지·정답이 다 적혀 있다.)

2) 그 문항의 정답·개념·기존 해설은 여기 있다:
   /home/user/exam/answers/${EXAM}.json 의 questions["<번호>"]
   (answer · concept · explanation · misconception 를 읽어라. 기존 해설은
    정답 풀이라서, 오답 선지가 왜 매력적인지는 네가 새로 써야 한다.)

${RULES}

3) 결과를 이 파일에 JSON 으로 써라(Write 도구):
   ${OUT}/${EXAM}__${c.name}.json

   꼴:
   {
    "12": {
     "stem": "다음 결합각을 순서대로 바르게 나열한 것은? 가. N₂H₂의 ∠H-N-N …",
     "choices": ["가 < 나 < 다", "가 < 다 < 나", "나 < 가 < 다", "다 < 나 < 가"],
     "misconceptions": { "1": "…", "2": "…", "4": "…" }
    }
   }

   열쇠는 문항 번호 문자열. choices 는 ①②③④ 차례대로 넷.
   misconceptions 의 열쇠는 **오답 선지 번호**만.

끝나면 몇 문항을 썼고 몇 문항을 왜 뺐는지 한 줄로 보고해라.`,
      { label: `집필:${EXAM}:${c.name}`, phase: '집필' }
    ).then(() => c),

  c => agent(
`너는 반박자다. **통과시키는 것이 목적이 아니라 틀린 것을 찾는 것이 목적이다.**

방금 누가 ${EXAM} 문항 ${c.qs.join(', ')} 의 선지별 오답 해설을 썼다.
결과: ${OUT}/${EXAM}__${c.name}.json

너는 **그 사람의 글을 믿지 말고 원본을 직접 봐라.**
   /home/user/exam/crops/${EXAM}/<번호>.png
   /home/user/exam/answers/${EXAM}.json

하나하나 확인해라:
1. **지문이 그림과 다른가.** 숫자·단위·물질명이 바뀌지 않았나.
2. **선지가 그림과 글자 그대로 같은가.** 차례가 바뀌지 않았나.
3. **오답 해설이 정말 그 선지를 낳는가.** 수치 선지면 네가 직접 계산해서
   그 값이 나오는지 확인해라. 안 나오면 그건 틀린 해설이다.
4. **정답 선지에 오답 해설이 달려 있지 않은가.** answers/${EXAM}.json 의
   answer 와 대조해라. 달려 있으면 심각한 결함이다.
5. **answer · acceptableAnswers 가 결과 파일에 들어 있지 않은가.**
6. **그림에 없는 것을 「주어졌다」고 쓰지 않았는가** (원자량·상수 등).
7. 두루뭉술한 해설("개념 혼동", "잘 몰라서")이 섞이지 않았는가.

찾은 것을 문항 번호와 함께 구체적으로 적어라. 「고쳐라」가 아니라
**「무엇이 왜 틀렸는지」**를 적어라. 아무 문제가 없는 문항은 적지 마라.
파일을 고치지는 마라 — 지적만 한다.`,
      { label: `반박:${EXAM}:${c.name}`, phase: '반박' }
    ).then(objections => ({ chunk: c, objections })),

  r => agent(
`너는 수리하는 사람이다.

${OUT}/${EXAM}__${r.chunk.name}.json 에 대해 반박자가 이렇게 적었다:

---
${r.objections}
---

**중요: 지적을 먼저 네가 직접 확인해라.**
원본(/home/user/exam/crops/${EXAM}/<번호>.png 와
/home/user/exam/answers/${EXAM}.json)을 열어서 반박이 맞는지 봐라.

· 반박이 맞으면 → 파일을 고쳐라.
· **반박이 틀렸으면 고치지 마라.** 대신 「이 지적은 틀렸다, 왜냐하면 …」을
  보고에 적어라. 반박자가 틀렸는데 고치면 멀쩡한 것을 망가뜨리는 것이다.

고친 뒤 JSON 이 그대로 읽히는지 확인해라
(python3 -c "import json;json.load(open('...'))").

보고: 고친 것 · 안 고친 것과 그 까닭.`,
      { label: `수리:${EXAM}:${r.chunk.name}`, phase: '수리' }
    ).then(report => ({ chunk: r.chunk.name, report }))
)

return { exam: EXAM, chunks: results.length, results }
