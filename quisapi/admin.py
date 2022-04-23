from django.contrib import admin

from quisapi.models import QuizGroup, Quiz, QuisAPIUser, Follower

admin.site.register(QuisAPIUser)
admin.site.register(QuizGroup)
admin.site.register(Quiz)
admin.site.register(Follower)
