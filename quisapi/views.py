from rest_framework import viewsets, status
from rest_framework.generics import get_object_or_404
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.response import Response

from quisapi.models import QuizGroup, Quiz, Follow
from quisapi.serializers import QuizGroupSerializer, QuizSerializer, FollowSerializer


class StandardResultsSetPagination(PageNumberPagination):
    page_size = 100
    page_size_query_param = 'page_size'
    max_page_size = 1000


class QuizGroupCRUD(viewsets.ModelViewSet):
    queryset = QuizGroup.objects.all()
    serializer_class = QuizGroupSerializer
    pagination_class = StandardResultsSetPagination
    permission_classes = [IsAuthenticatedOrReadOnly]

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
