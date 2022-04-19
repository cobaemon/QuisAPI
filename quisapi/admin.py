from django.contrib import admin

from quisapi.models import Follow, QuizGroup, Quiz

admin.site.register(QuizGroup)
admin.site.register(Quiz)
admin.site.register(Follow)
