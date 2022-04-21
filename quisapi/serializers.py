from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator

from quisapi.models import QuizGroup, Quiz, Follower


class QuizGroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = QuizGroup
        fields = ['user', 'quiz_group_name', 'quiz_group_description', 'followings', 'scope']
        validators = [
            UniqueTogetherValidator(
                queryset=QuizGroup.objects.all(),
                fields=('user', 'quiz_group_name'),
                message='duplicate key value violates unique constraint',
            ),
        ]
        extra_kwargs = {
            'followings': {
                'read_only': True,
            },
        }


class QuizSerializer(serializers.ModelSerializer):
    class Meta:
        model = Quiz
        fields = ['quiz_group', 'quiz_title', 'quiz_content']


class FollowerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Follower
        fields = ['user', 'quiz_group']
        validators = [
            UniqueTogetherValidator(
                queryset=Follower.objects.all(),
                fields=('user', 'quiz_group'),
                message='duplicate key value violates unique constraint',
            ),
        ]

    def validate(self, data):
        user = data.get('user')
        authors = data.get('quiz_group').user

        if user == authors:
            raise serializers.ValidationError(
                'The creator himself cannot be followed'
            )
        return data
