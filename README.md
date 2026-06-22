# MBTI 성격유형 검사

Flask 세션으로 로그인 상태를 관리하는 MBTI 검사 사이트입니다.

로그인 → 검사 안내 → 문항 1 → 문항 2 → 결과 순서로 진행됩니다.

## 주요 기능

- 고정 계정 로그인 및 세션 유지
- 비로그인 사용자의 검사 페이지 접근 제한
- 우측 상단 사용자 아이디와 로그아웃 버튼
- 20개 문항을 두 페이지로 분할
- MBTI 유형, 설명, 성향별 그래프 출력
- `base.html`을 이용한 Jinja2 템플릿 상속

## 실행

```bash
pip install -r requirements.txt
python app.py
```

브라우저에서 `http://localhost:5000`에 접속합니다.

- 아이디: `guest`
- 비밀번호: `1234`

## URL

| URL | 방식 | 설명 |
|---|---|---|
| `/` | GET | 로그인 여부에 따라 이동 |
| `/login` | GET, POST | 로그인 |
| `/logout` | GET | 로그아웃 |
| `/main` | GET | 검사 안내 |
| `/test` | GET | 1~10번 문항 |
| `/test2` | GET, POST | 11~20번 문항 |
| `/result` | POST | 검사 결과 |

## 파일 구조

```text
app.py
requirements.txt
templates/
  base.html
  login.html
  main.html
  test.html
  result.html
static/
  style.css
```
