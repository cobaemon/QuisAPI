from django.urls import path, include
from rest_framework import routers

from quisapi import views

quiz_group_router = routers.SimpleRouter()
quiz_group_router.register('quiz-group', views.QuizGroupCRUD)
quiz_router = routers.SimpleRouter()
quiz_router.register('quiz', views.QuizCRUD)

urlpatterns = [
    # クイズグループ
    path('', include(quiz_group_router.urls)),
    # クイズ
    path('', include(quiz_router.urls)),
    # フォロー
    path('follow/add/<pk>', views.FollowView.as_view()),
    path('follow/remove/<pk>', views.UnfollowView.as_view()),
]
