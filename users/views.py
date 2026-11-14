from django.contrib.auth import login as auth_login, logout as auth_logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.models import User
from django.http import HttpResponseNotAllowed
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_POST
from django.core.paginator import Paginator

from questions.models import Question, Answer
from .forms import RegistrationForm, UserProfileForm, PasswordChangeCustomForm

from django.db import transaction
from events.services import create_event

def home1(request):
    questions = Question.objects.select_related("asked_by").all().order_by("-asked_at")
    paginator = Paginator(questions, 10)
    page_obj = paginator.get_page(request.GET.get("page"))
    return render(request, "homepage_with_pagination.html", {
        "page_obj": page_obj,
        "questions": questions,
    })


def home(request):
    questions = Question.objects.order_by("-asked_at")
    return render(request, "homepage.html", {"questions": questions})


def register(request):
    if request.method == "POST":
        form = RegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("login")
    else:
        form = RegistrationForm()
    return render(request, "register.html", {"form": form})


def login(request):
    if request.method == "POST":
        form = AuthenticationForm(request, request.POST)
        if form.is_valid():
            auth_login(request, form.get_user())
            return redirect("home")
    else:
        form = AuthenticationForm(request)
    return render(request, "login.html", {"form": form})


@login_required
def logout(request):
    # Logout changes session state, so do not allow it through a GET request.
    if request.method != "POST":
        return HttpResponseNotAllowed(["POST"])
    auth_logout(request)
    return redirect("home")


@login_required
def user_profile(request):
    user = request.user
    question_count = Question.objects.filter(asked_by=user).count()
    answer_count = Answer.objects.filter(answered_by=user).count()
    return render(request, "user_profile.html", {
        "user": user,
        "question_count": question_count,
        "answer_count": answer_count,
    })


@login_required
def edit_profile(request):
    if request.method == "POST":
        action = request.POST.get("action")

        if action == "update_profile":
            profile_form = UserProfileForm(request.POST, instance=request.user)
            password_form = PasswordChangeCustomForm(request.user)
            if profile_form.is_valid():
                profile_form.save()
                return redirect("user_profile")

        elif action == "change_password":
            profile_form = UserProfileForm(instance=request.user)
            password_form = PasswordChangeCustomForm(request.user, request.POST)
            if password_form.is_valid():
                user = password_form.save()
                update_session_auth_hash(request, user)
                return redirect("user_profile")
        else:
            profile_form = UserProfileForm(instance=request.user)
            password_form = PasswordChangeCustomForm(request.user)
    else:
        profile_form = UserProfileForm(instance=request.user)
        password_form = PasswordChangeCustomForm(request.user)

    return render(request, "edit_profile.html", {
        "profile_form": profile_form,
        "password_form": password_form,
    })


@login_required
@require_POST
def user_questions(request):
    question_id = request.POST.get("question_id")

    question = get_object_or_404(
        Question,
        id=question_id,
        asked_by=request.user,
    )

    with transaction.atomic():
        create_event(
            event_type="question_deleted",
            user_id=request.user.id,
            payload={
                "question_id": question.id
            }
        )

        question.delete()

    return redirect("user_questions")

@login_required
def user_questions_list(request):
    questions = Question.objects.filter(asked_by=request.user).order_by("-asked_at")
    return render(request, "user_questions.html", {"questions": questions})


@login_required
@require_POST
def user_answers_delete(request):
    answer_id = request.POST.get("answer_id")

    answer = get_object_or_404(
        Answer,
        id=answer_id,
        answered_by=request.user,
    )

    with transaction.atomic():
        create_event(
            event_type="answer_deleted",
            user_id=request.user.id,
            payload={
                "answer_id": answer.id,
                "question_id": answer.question_id
            }
        )

        answer.delete()

    return redirect("user_answers")


@login_required
def user_answers(request):
    answers = Answer.objects.filter(answered_by=request.user).select_related(
        "question"
    ).order_by("-answered_at")
    return render(request, "user_answers.html", {"answers": answers})


def other_user_profile(request, user_id):
    user = get_object_or_404(User, pk=user_id)
    question_count = Question.objects.filter(asked_by=user).count()
    answer_count = Answer.objects.filter(answered_by=user).count()
    return render(request, "other_user_profile.html", {
        "user": user,
        "question_count": question_count,
        "answer_count": answer_count,
    })


def other_user_questions(request, user_id):
    questions = Question.objects.filter(asked_by_id=user_id).order_by("-asked_at")
    return render(request, "other_user_questions.html", {"questions": questions})


def other_user_answers(request, user_id):
    answers = Answer.objects.filter(answered_by_id=user_id).order_by("-answered_at")
    return render(request, "other_user_answers.html", {"answers": answers})
