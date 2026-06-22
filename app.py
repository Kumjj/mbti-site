from flask import Flask, render_template, request, redirect, session, url_for

app = Flask(__name__)
app.secret_key = "mbti-session-key"

# 테스트용 로그인 정보
USER_ID = "guest"
USER_PW = "1234"

# (폼 이름, 양수 글자, 음수 글자, 화면 이름)
DIMENSIONS = [
    ("energy", "E", "I", "에너지 방향"),
    ("perception", "S", "N", "인식 방식"),
    ("judgement", "T", "F", "판단 기준"),
    ("lifestyle", "J", "P", "생활 양식"),
    ("identity", "A", "T", "정체성"),
]

OPTIONS = [
    {"value": 3, "cls": "a2"},
    {"value": 2, "cls": "a1"},
    {"value": 1, "cls": "n"},
    {"value": -1, "cls": "d1"},
    {"value": -2, "cls": "d2"},
]

# 성향별 4문항, 총 20문항
QUESTIONS = [
    {"name": "energy1", "text": "처음 만난 사람과도 쉽게 대화를 시작하는 편이다."},
    {"name": "energy2", "text": "여러 사람과 어울릴 때 오히려 에너지가 솟는다."},
    {"name": "energy3", "text": "주말에는 집에 있기보다 밖에서 약속을 잡는 게 좋다."},
    {"name": "energy4", "text": "생각을 혼자 정리하기보다 말하면서 정리하는 편이다."},
    {"name": "perception1", "text": "상상 속 이야기보다 실제 경험과 사실이 더 와닿는다."},
    {"name": "perception2", "text": "일을 할 때 구체적이고 현실적인 방법을 먼저 떠올린다."},
    {"name": "perception3", "text": "'왜?'라는 추상적 질문보다 '어떻게?'라는 실제 방법이 궁금하다."},
    {"name": "perception4", "text": "눈에 보이는 사실과 데이터를 근거로 판단한다."},
    {"name": "judgement1", "text": "결정을 내릴 때 감정보다 논리와 사실을 우선한다."},
    {"name": "judgement2", "text": "의견이 틀렸다면 분위기보다 사실을 짚는 편이다."},
    {"name": "judgement3", "text": "공감해주는 것보다 해결책을 제시하는 게 더 도움이 된다고 본다."},
    {"name": "judgement4", "text": "비판을 받으면 기분보다 그 내용이 맞는지부터 따져본다."},
    {"name": "lifestyle1", "text": "할 일을 미리 계획하고 일정대로 움직이는 게 편하다."},
    {"name": "lifestyle2", "text": "여행을 가기 전에 동선과 일정을 미리 정해둔다."},
    {"name": "lifestyle3", "text": "마감 직전보다 미리미리 끝내두는 편이다."},
    {"name": "lifestyle4", "text": "정리정돈된 환경에서 더 집중이 잘 된다."},
    {"name": "identity1", "text": "실수를 해도 크게 자책하지 않고 금방 털어낸다."},
    {"name": "identity2", "text": "내 선택과 능력에 대체로 확신이 있는 편이다."},
    {"name": "identity3", "text": "남의 평가에 크게 흔들리지 않는다."},
    {"name": "identity4", "text": "스트레스 상황에서도 비교적 침착함을 유지한다."},
]

BASE_TYPE_INFO = {
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

IDENTITY_INFO = {
    "A": ("확신형", "자기 확신이 높고 스트레스 상황에서도 비교적 침착하게 대응합니다."),
    "T": ("신중형", "스스로를 세심하게 돌아보며 더 나은 결과를 위해 꾸준히 개선합니다."),
}

TYPE_INFO = {
    f"{mbti}-{identity}": {"nick": f"{info['nick']} · {trait[0]}", "desc": f"{info['desc']} {trait[1]}"}
    for mbti, info in BASE_TYPE_INFO.items() for identity, trait in IDENTITY_INFO.items()
}


@app.before_request
def require_login():
    if request.endpoint not in {"root", "login", "static"} and "user_id" not in session:
        return redirect(url_for("login"))


@app.get("/")
def root():
    return redirect(url_for("main" if "user_id" in session else "login"))


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        if (request.form.get("user_id"), request.form.get("password")) == (USER_ID, USER_PW):
            session["user_id"] = USER_ID
            return redirect(url_for("main"))
        return render_template("login.html", error="아이디 또는 비밀번호가 올바르지 않습니다.")
    return render_template("login.html")


@app.get("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))


@app.get("/main")
def main():
    return render_template("main.html")


@app.get("/test")
@app.route("/test2", methods=["GET", "POST"], endpoint="test2")
def test():
    page = 2 if request.path == "/test2" else 1
    if page == 2 and request.method == "GET":
        return redirect(url_for("test"))

    answers = []
    if page == 2:
        names = [q["name"] for q in QUESTIONS[:10]]
        if not all(name in request.form for name in names):
            return redirect(url_for("test"))
        answers = [(name, request.form[name]) for name in names]

    start = (page - 1) * 10
    return render_template(
        "test.html",
        page=page,
        questions=QUESTIONS[start:start + 10],
        options=OPTIONS,
        answers=answers,
    )


@app.post("/result")
def result():
    letters, rows = [], []
    for name, positive, negative, label in DIMENSIONS:
        score = sum(int(request.form.get(f"{name}{i}", 0)) for i in range(1, 5))
        percent = round((score + 8) / 20 * 100)
        letter = positive if score >= 0 else negative
        strength = percent if score >= 0 else 100 - percent
        letters.append(letter)
        rows.append({"label": label, "letter": letter, "strength": strength})

    mbti = "".join(letters[:4]) + "-" + letters[4]
    info = TYPE_INFO[mbti]
    return render_template("result.html", mbti=mbti, info=info, rows=rows)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
