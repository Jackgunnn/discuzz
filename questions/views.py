from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404

from questions.forms import QuestionForm, AnswerForm
from questions.models import Question


@login_required
def ask_question(request):
    if request.method == "POST":
        form = QuestionForm(request.POST)
        if form.is_valid():
            question = form.save(commit=False)
            question.asked_by = request.user
            question.save()
            return redirect("ask_question")
    else:
        form = QuestionForm()
    return render(request, "ask_question.html", {"form": form})


def show_answer(request, question_id):
    question = get_object_or_404(
        Question.objects.select_related("asked_by"),
        pk=question_id,
    )

    if request.method == "POST":
        if not request.user.is_authenticated:
            return redirect("login")
        form = AnswerForm(request.POST)
        if form.is_valid():
            answer = form.save(commit=False)
            answer.question = question
            answer.answered_by = request.user
            answer.save()
            return redirect("show_answer", question_id=question.pk)
    else:
        form = AnswerForm()

    answers = question.answers.select_related("answered_by").order_by("-answered_at")
    return render(request, "show_answers.html", {
        "question": question,
        "answers": answers,
        "form": form,
    })
