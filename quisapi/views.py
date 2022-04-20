from django.db.models import Q
from rest_framework import viewsets, status
from rest_framework.generics import get_object_or_404
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.response import Response

from quisapi.models import QuizGroup, Quiz, Follow
from quisapi.serializers import QuizGroupSerializer, QuizSerializer


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

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)

        if serializer.validated_data['scope']:
            Follow.objects.create(
                quiz_group=get_object_or_404(
                    QuizGroup,
                    user=self.request.user,
                    quiz_group_name=serializer.validated_data['quiz_group_name'],
                ),
            )

        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)


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
