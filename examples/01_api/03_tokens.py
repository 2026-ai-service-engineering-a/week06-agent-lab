"""토큰 세기 — 같은 문장의 한국어/영어 토큰 수 비교. 한글이 왜 더 비싼가.

  docker compose exec lab python examples/01_api/03_tokens.py

API 호출 없이 토크나이저만으로 동작한다 (키 불필요). 과금·컨텍스트 한도는
글자 수가 아니라 토큰 수 기준이다. 같은 뜻이라도 한국어가 토큰을 더 쓰는
것을 눈으로 확인한다.
"""

from litellm import token_counter

from examples._shared import h1

pairs = [
    ("안녕하세요, 오늘 날씨가 정말 좋네요.", "Hello, the weather is really nice today."),
    ("3박 4일 오사카 여행 일정을 짜 주세요. 예산은 80만원입니다.",
     "Plan a 4-day, 3-night trip to Osaka. The budget is 800,000 KRW."),
    ("대규모 언어 모델은 토큰 단위로 텍스트를 처리합니다.",
     "Large language models process text in units of tokens."),
]

# 토큰화는 모델마다 다르다. 여기서는 기준 토크나이저(gpt 계열) 하나로 상대 비교.
model = "gpt-4o"

h1(f"토큰 수 비교 (tokenizer: {model})")
print(f"  {'한국어':>4} | {'영어':>4} | 문장")
total_ko = total_en = 0
for ko, en in pairs:
    t_ko = token_counter(model=model, text=ko)
    t_en = token_counter(model=model, text=en)
    total_ko += t_ko
    total_en += t_en
    print(f"  {t_ko:>4} | {t_en:>4} | {ko[:30]}…")

h1("합계")
print(f"  한국어 {total_ko} 토큰 vs 영어 {total_en} 토큰")
print(f"  같은 내용을 한국어로 쓰면 약 {total_ko / total_en:.1f}배의 토큰 = 그만큼의 비용·컨텍스트")
