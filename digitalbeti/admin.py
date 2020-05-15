from django.contrib import admin

# Register your models here.

from .models import BeneficiaryData, Address, Exam, Question, QuestionData, AnswerSet, DigitalBetiUser, VillageDetails, \
    VLECompetition, StateVideo

admin.site.register(DigitalBetiUser)
admin.site.register(BeneficiaryData)
admin.site.register(Address)
admin.site.register(Exam)
admin.site.register(Question)
admin.site.register(QuestionData)
admin.site.register(AnswerSet)
admin.site.register(VillageDetails)
admin.site.register(VLECompetition)
admin.site.register(StateVideo)