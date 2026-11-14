from django.urls import path
from . import views

urlpatterns = [
    path("", views.home1, name="home"),
    path("login/", views.login, name="login"),
    path("logout/", views.logout, name="logout"),
    path("register/", views.register, name="register"),
    path("profile/", views.user_profile, name="user_profile"),
    path("profile/edit/", views.edit_profile, name="edit_profile"),
    path("profile/questions/", views.user_questions_list, name="user_questions"),
    path("profile/questions/delete/", views.user_questions, name="delete_user_question"),
    path("profile/answers/", views.user_answers, name="user_answers"),
    path("profile/answers/delete/", views.user_answers_delete, name="delete_user_answer"),
    path("profile/<int:user_id>/", views.other_user_profile, name="other_user_profile"),
    path("profile/<int:user_id>/questions/", views.other_user_questions, name="other_user_questions"),
    path("profile/<int:user_id>/answers/", views.other_user_answers, name="other_user_answers"),
]
