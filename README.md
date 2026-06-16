# MBTI 성격유형 검사

Flask로 만든 MBTI 검사 사이트. **로그인 → 검사 준비 → 문항 1 → 문항 2 → 결과** 5단계.

## 폴더 구조
```
app.py              # 서버·라우팅·점수 계산
requirements.txt    # Flask
templates/
  login.html        # 로그인
  main.html         # 검사 준비
  test.html         # 문항 1~10번
  test2.html        # 문항 11~20번
  result.html       # 결과
static/
  style.css         # 디자인
```

## 실행
```bash
pip install -r requirements.txt
python3 app.py
```
http://localhost:5000 접속 → **guest / 1234** 로그인

## 라우팅 (페이지 5개 · URL 4개)
| URL | 방식 | 설명 |
|---|---|---|
| `/` | GET | `/login`으로 이동 |
| `/login` | GET/POST | 로그인, 틀리면 하단에 메시지 |
| `/main` | GET | 검사 준비 |
| `/test` | GET | 문항 1~10번 |
| `/test2` | GET/POST | 문항 11~20번, GET으로 직접 접근하면 `/test`로 이동 |
| `/result` | POST | 결과 (폼 제출로만 진입) |

HTML 페이지는 `login.html`, `main.html`, `test.html`, `test2.html`, `result.html` 총 5개.

## 점수 계산
- 성향 5개 × 4문항 = 20문항 — energy(E/I), perception(S/N), judgement(T/F), lifestyle(J/P), identity(A/T)
- 문항은 1페이지 10개, 2페이지 10개로 나누어 보여줌
- 1페이지 답변은 `test2.html`의 hidden input으로 넘겨 최종 결과 계산에 함께 사용
- 선택지: 매우 그렇다 `+3` / 그렇다 `+2` / 보통 `+1` / 아니다 `-1` / 전혀 아니다 `-2`
- 모든 문항은 "그렇다 = 앞 글자(E·S·T·J·A)" 방향
- 합산 범위: `-8 ~ 12` (4문항)
- 글자 결정: 0 이상 → 앞 글자, 음수 → 뒤 글자
- 퍼센트: `round((score + 8) / 20 * 100)` — `-8`→0%, `0`→40%, `12`→100%
- 막대: 앞 글자면 percent, 뒤 글자면 `100 - percent` (= 내 성향 강도)
- 최종: 앞 4글자 + `-` + 정체성 → 예) `ENTP-T`

## 예상 질문
- `@app.route` — URL과 실행 함수를 잇는 데코레이터
- `render_template` — templates/의 HTML을 화면에 출력
- 로그인 정보 — app.py의 `USER_ID` / `USER_PW`
- 문항 20개 — app.py `QUESTIONS`를 `test.html` 10개, `test2.html` 10개로 나누어 출력
- 점수 계산 — `/result`에서 폼 값을 성향별로 합산
