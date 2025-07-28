from flask import Flask, render_template, request, redirect, url_for, session
from gemini_api import generate_question, analyze_answer, check_translation, call_ai_model, evaluate_academic_english
from utils import get_random_word_by_level
import secrets #session

from langchain.memory import ConversationBufferMemory

memory = ConversationBufferMemory(return_messages=True)


app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def select_level():
    if request.method == "POST":
        level = request.form["level"]
        return redirect(url_for("mode_select", level=level))
    return render_template("select_level.html")

@app.route("/mode-select/<level>", methods=["GET", "POST"])
def mode_select(level):
    if request.method == "POST":
        selected_mode = request.form["mode"]
        if selected_mode == "chat":
            return redirect(url_for("chat_mode", level=level))
        elif selected_mode == "word":
            return redirect(url_for("word_mode", level=level))
        elif selected_mode == "free":
            return redirect(url_for("free_mode", level=level))
        elif selected_mode == "academic":
            return redirect(url_for("academic_mode", level=level))
    return render_template("select_mode.html", level=level)




app.secret_key = secrets.token_hex(16) # Kullancı için session anahtarı rüetme
@app.route("/chat/<level>", methods=["GET", "POST"])
def chat_mode(level):
    if "asked_questions" not in session:
        session["asked_questions"] = []

    if request.method == "POST":
        user_answer = request.form["user_answer"]
        current_question = request.form["current_question"]

        asked_questions = session.get("asked_questions", [])
        if current_question not in asked_questions:
            asked_questions.append(current_question)
            session["asked_questions"] = asked_questions

        feedback = analyze_answer(user_answer, level)
        next_question = generate_question(level, asked_questions)

        return render_template(
            "chat.html",
            question=next_question,
            feedback=feedback,
            level=level,
            last_question=current_question
        )

    session["asked_questions"] = []
    question = generate_question(level, session["asked_questions"])
    return render_template("chat.html", question=question, level=level)


@app.route("/word/<level>", methods=["GET", "POST"])
def word_mode(level):
    word = get_random_word_by_level(level)

    if request.method == "POST":
        user_input = request.form["user_input"].strip()
        old_word = request.form["old_word"].strip()
        feedback = check_translation(old_word, user_input)

        new_word = get_random_word_by_level(level)

        return render_template(
            "word.html",
            word=new_word,
            feedback=feedback,
            show_result=True,
            level=level,
            old_word=old_word,
            user_input=user_input
        )

    return render_template(
        "word.html",
        word=word,
        show_result=False,
        level=level
    )


@app.route("/free/<level>", methods=["GET", "POST"])
def free_mode(level):
    response = None
    history = []

    if request.method == "POST":
        user_message = request.form["user_input"]
        memory.chat_memory.add_user_message(user_message)
        response = call_ai_model(user_message)
        memory.chat_memory.add_ai_message(response)
        
    history = memory.chat_memory.messages

    return render_template("free.html", response=response, level=level, history=history)


@app.route("/academic/<level>", methods=["GET", "POST"])
def academic_mode(level):
    feedback = None
    score = None
    if request.method == "POST":
        user_text = request.form["user_text"]
        feedback, score = evaluate_academic_english(user_text)  
    return render_template("academic.html", feedback=feedback, score=score, level=level)



if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True, use_reloader=False)





















