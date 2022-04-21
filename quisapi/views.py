from django.db import transaction
from django.db.models import Q
from django.shortcuts import get_object_or_404
from rest_framework import viewsets, views, status
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticatedOrReadOnly, IsAuthenticated
from rest_framework.response import Response

from quisapi.models import QuizGroup, Quiz, Follower
from quisapi.serializers import QuizGroupSerializer, QuizSerializer, FollowerSerializer


class StandardResultsSetPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 1000


class QuizGroupCRUD(viewsets.ModelViewSet):
    queryset = QuizGroup.objects.all()
    serializer_class = QuizGroupSerializer
    pagination_class = StandardResultsSetPagination
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        query_set = super().get_queryset()
        if self.request.user.is_authenticated:
            query_set = query_set.filter(
                Q(user=self.request.user) |
                Q(scope=True)
            ).distinct()
        else:
            query_set = query_set.filter(
                scope=True,
            )

        return query_set.order_by('quiz_group_name')


class QuizCRUD(viewsets.ModelViewSet):
    queryset = Quiz.objects.all()
    serializer_class = QuizSerializer
    pagination_class = StandardResultsSetPagination
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        query_set = super().get_queryset()
        if self.request.user.is_authenticated:
            query_set = query_set.filter(
                Q(quiz_group__user=self.request.user) |
                Q(quiz_group__scope=True)
            ).distinct()
        else:
            query_set = query_set.filter(
                quiz_group__scope=True,
            )

        return query_set.order_by('quiz_title')


class FollowView(views.APIView):
    permission_classes = [IsAuthenticated]

    @transaction.atomic
    def put(self, request, pk, *args, **kwargs):
        quiz_group = get_object_or_404(
            QuizGroup,
            uuid=pk
        )
        serializer = FollowerSerializer(
            instance=quiz_group,
            data=request.data,
        )
        serializer.is_valid(raise_exception=True)

        Follower.objects.create(
            user=request.user,
            quiz_group=get_object_or_404(
                QuizGroup,
                uuid=serializer.validated_data['quiz_group'],
            ),
        )
        QuizGroup.objects.values().filter(
            uuid=pk
        ).update(
            followings=quiz_group.followings + 1,
        )

        return Response(status.HTTP_200_OK)


class UnfollowView(views.APIView):
    permission_classes = [IsAuthenticated]

    @transaction.atomic
    def put(self, request, pk, *args, **kwargs):
        quiz_group = get_object_or_404(
            QuizGroup,
            uuid=pk
        )

        QuizGroup.objects.values().filter(
            uuid=pk
        ).update(
            followings=quiz_group.followings - 1,
        )
        get_object_or_404(
            Follower,
            user=request.user,
            quiz_group=quiz_group,
        ).delete()

        return Response(status.HTTP_200_OK)
