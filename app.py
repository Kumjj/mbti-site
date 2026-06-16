from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)

# =====================================================================
#  1. 로그인 정보 (간단하게 고정값으로 둠)
# =====================================================================
USER_ID = "guest"
USER_PW = "1234"

# =====================================================================
#  2. 5개의 성향(차원) 정의
#     (변수명, 양수일 때 글자, 음수일 때 글자, 화면에 보일 이름)
#     - 점수가 0 이상이면 앞 글자, 음수면 뒤 글자를 선택한다.
# =====================================================================
DIMENSIONS = [
    ("energy",     "E", "I", "에너지 방향"),   # 외향 / 내향
    ("perception", "S", "N", "인식 방식"),     # 감각 / 직관
    ("judgement",  "T", "F", "판단 기준"),     # 사고 / 감정
    ("lifestyle",  "J", "P", "생활 양식"),     # 계획 / 즉흥
    ("identity",   "A", "T", "정체성"),        # 확신형 / 신중형(-A / -T)
]

# =====================================================================
#  3. 라디오 버튼 5개의 점수와 디자인용 클래스
#     - "그렇다"에 가까울수록 +점수 → 앞 글자(E,S,T,J,A) 성향
#     - 보통이다는 +1점 (모두 0점이 되는 것을 막기 위함)
# =====================================================================
OPTIONS = [
    {"value":  3, "cls": "a2"},  # 매우 그렇다
    {"value":  2, "cls": "a1"},  # 그렇다
    {"value":  1, "cls": "n"},   # 보통이다 (0점 방지용)
    {"value": -1, "cls": "d1"},  # 아니다
    {"value": -2, "cls": "d2"},  # 전혀 아니다
]

# =====================================================================
#  4. 20개 질문 (성향별 4문항)
#     name 은 "변수명 + 번호" 형식 (예: energy1 ~ energy4)
#     → 결과 페이지에서 변수명+번호로 다시 모아 점수를 합산한다.
#     모든 문항은 "그렇다 = 앞 글자(E/S/T/J/A) 성향" 방향으로 작성함.
# =====================================================================
QUESTIONS = [
    # --- 에너지 E/I : 그럴수록 E(외향) ---
    {"name": "energy1", "text": "처음 만난 사람과도 쉽게 대화를 시작하는 편이다."},
    {"name": "energy2", "text": "여러 사람과 어울릴 때 오히려 에너지가 솟는다."},
    {"name": "energy3", "text": "주말에는 집에 있기보다 밖에서 약속을 잡는 게 좋다."},
    {"name": "energy4", "text": "생각을 혼자 정리하기보다 말하면서 정리하는 편이다."},
    # --- 인식 S/N : 그럴수록 S(감각) ---
    {"name": "perception1", "text": "상상 속 이야기보다 실제 경험과 사실이 더 와닿는다."},
    {"name": "perception2", "text": "일을 할 때 구체적이고 현실적인 방법을 먼저 떠올린다."},
    {"name": "perception3", "text": "'왜?'라는 추상적 질문보다 '어떻게?'라는 실제 방법이 궁금하다."},
    {"name": "perception4", "text": "눈에 보이는 사실과 데이터를 근거로 판단한다."},
    # --- 판단 T/F : 그럴수록 T(사고) ---
    {"name": "judgement1", "text": "결정을 내릴 때 감정보다 논리와 사실을 우선한다."},
    {"name": "judgement2", "text": "의견이 틀렸다면 분위기보다 사실을 짚는 편이다."},
    {"name": "judgement3", "text": "공감해주는 것보다 해결책을 제시하는 게 더 도움이 된다고 본다."},
    {"name": "judgement4", "text": "비판을 받으면 기분보다 그 내용이 맞는지부터 따져본다."},
    # --- 생활 J/P : 그럴수록 J(계획) ---
    {"name": "lifestyle1", "text": "할 일을 미리 계획하고 일정대로 움직이는 게 편하다."},
    {"name": "lifestyle2", "text": "여행을 가기 전에 동선과 일정을 미리 정해둔다."},
    {"name": "lifestyle3", "text": "마감 직전보다 미리미리 끝내두는 편이다."},
    {"name": "lifestyle4", "text": "정리정돈된 환경에서 더 집중이 잘 된다."},
    # --- 정체성 A/T : 그럴수록 A(확신형) ---
    {"name": "identity1", "text": "실수를 해도 크게 자책하지 않고 금방 털어낸다."},
    {"name": "identity2", "text": "내 선택과 능력에 대체로 확신이 있는 편이다."},
    {"name": "identity3", "text": "남의 평가에 크게 흔들리지 않는다."},
    {"name": "identity4", "text": "스트레스 상황에서도 비교적 침착함을 유지한다."},
]

# =====================================================================
#  5. 16가지 유형 설명 (이모지 / 별명 / 한 줄 설명)
# =====================================================================
TYPE_INFO = {
    "ISTJ": {"nick": "청렴결백한 논리주의자", "desc": "현실적이고 책임감이 강하며, 맡은 일을 끝까지 해내는 유형입니다."},
    "ISFJ": {"nick": "용감한 수호자",         "desc": "조용하지만 헌신적이며, 주변 사람을 성실하게 챙기는 유형입니다."},
    "INFJ": {"nick": "선의의 옹호자",         "desc": "깊은 통찰력으로 사람과 세상을 이해하려는 이상주의 유형입니다."},
    "INTJ": {"nick": "용의주도한 전략가",     "desc": "큰 그림을 그리고 전략을 세우는 데 강한 독립적 유형입니다."},
    "ISTP": {"nick": "만능 재주꾼",           "desc": "논리적이고 손재주가 좋아 문제를 직접 분석하고 해결하는 유형입니다."},
    "ISFP": {"nick": "호기심 많은 예술가",     "desc": "온화하고 감각적이며, 자신만의 방식으로 표현하는 유형입니다."},
    "INFP": {"nick": "열정적인 중재자",       "desc": "뚜렷한 가치와 신념을 품고 진정성을 추구하는 유형입니다."},
    "INTP": {"nick": "논리적인 사색가",       "desc": "호기심이 많고 논리적이며, 아이디어를 깊이 파고드는 유형입니다."},
    "ESTP": {"nick": "모험을 즐기는 사업가",   "desc": "에너지가 넘치고 도전을 즐기는 현실 감각의 행동가 유형입니다."},
    "ESFP": {"nick": "자유로운 영혼의 연예인", "desc": "밝고 사교적이며, 현재의 순간을 즐길 줄 아는 유형입니다."},
    "ENFP": {"nick": "재기발랄한 활동가",     "desc": "열정과 상상력이 넘치고, 주변에 영감을 주는 유형입니다."},
    "ENTP": {"nick": "뜨거운 논쟁을 즐기는 변론가", "desc": "재치 있고 논쟁을 즐기며, 새로운 가능성을 탐구하는 유형입니다."},
    "ESTJ": {"nick": "엄격한 관리자",         "desc": "체계적이고 추진력이 강해 조직을 이끄는 데 능한 유형입니다."},
    "ESFJ": {"nick": "사교적인 외교관",       "desc": "협력적이며, 사람들을 챙기고 화합을 이끄는 유형입니다."},
    "ENFJ": {"nick": "정의로운 사회운동가",    "desc": "설득력 있는 리더십으로 사람들을 이끌고 성장시키는 유형입니다."},
    "ENTJ": {"nick": "대담한 통솔자",         "desc": "목표 지향적이고 결단력 있는 타고난 통솔자 유형입니다."},
}


# =====================================================================
#  라우팅
# =====================================================================

@app.route("/")
def root():
    # 시작은 무조건 로그인 페이지로 보낸다.
    return redirect(url_for("login"))


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        user_id = request.form.get("user_id")
        password = request.form.get("password")
        # 아이디/비밀번호가 맞으면 검사 준비 페이지로 이동
        if user_id == USER_ID and password == USER_PW:
            return redirect(url_for("main"))
        # 틀리면 같은 페이지에 에러 메시지만 하단에 표시
        return render_template("login.html", error="아이디 또는 비밀번호가 올바르지 않습니다.")
    return render_template("login.html")


@app.route("/main")
def main():
    # 검사 준비 화면 (MBTI 설명 + 검사 시작 버튼)
    return render_template("main.html")


@app.route("/test")
def test():
    # 검사 지문 1페이지 (1~10번)
    return render_template(
        "test.html",
        questions=QUESTIONS[:10],
        options=OPTIONS,
        start_index=0,
    )


@app.route("/test2", methods=["GET", "POST"])
def test2():
    # 주소창으로 바로 들어오면 1페이지부터 다시 시작한다.
    if request.method == "GET":
        return redirect(url_for("test"))

    first_answers = []
    for q in QUESTIONS[:10]:
        value = request.form.get(q["name"])
        if value is None:
            return redirect(url_for("test"))
        first_answers.append((q["name"], value))

    # 검사 지문 2페이지 (11~20번), 1페이지 답변은 hidden input으로 같이 넘긴다.
    return render_template(
        "test2.html",
        questions=QUESTIONS[10:],
        options=OPTIONS,
        start_index=10,
        first_answers=first_answers,
    )


@app.route("/result", methods=["POST"])
def result():
    rows = []            # 화면에 그릴 5개 막대 데이터
    type_letters = ""    # 앞 4글자 (E/I, S/N, T/F, J/P)
    identity_letter = "A"

    for var, pos, neg, label in DIMENSIONS:
        # 1) 같은 성향 4문항 점수를 합산 (점수 범위: -8 ~ 12)
        score = 0
        for i in range(1, 5):
            score += int(request.form.get(f"{var}{i}", 0))

        # 2) 표준화: -8~12 점을 0~100% 로 변환 (앞 글자 기준 강도)
        #    score=-8 → 0% , score=0 → 40% , score=12 → 100%
        percent = round((score + 8) / 20 * 100)

        # 3) 점수 부호로 글자 결정 (0 이상이면 앞 글자)
        letter = pos if score >= 0 else neg
        # 선택된 글자 자신의 강도 (막대에 채울 값)
        strength = percent if score >= 0 else 100 - percent

        rows.append({
            "label": label,
            "letter": letter,
            "strength": strength,
        })

        if var == "identity":
            identity_letter = letter      # 정체성은 -A / -T 접미사로 사용
        else:
            type_letters += letter        # 나머지는 4글자 유형으로 합침

    mbti = type_letters + "-" + identity_letter
    info = TYPE_INFO.get(type_letters, {
        "nick": "나만의 유형", "desc": "당신만의 성향 조합입니다."
    })

    return render_template("result.html", mbti=mbti, info=info, rows=rows)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
