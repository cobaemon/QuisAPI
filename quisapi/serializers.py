from rest_framework import serializers

from quisapi.models import QuizGroup, Quiz, Follow


class QuizGroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = QuizGroup
        fields = ['user', 'quiz_group_name', 'quiz_group_description', 'scope']


class QuizSerializer(serializers.ModelSerializer):
    class Meta:
        model = Quiz
        fields = ['quiz_group', 'quiz_title', 'quiz_content']


class FollowSerializer(serializers.ModelSerializer):
    class Meta:
        model = Follow
        fields = ['quiz_group']
