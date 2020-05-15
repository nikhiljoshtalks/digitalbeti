from modeltranslation.translator import register, TranslationOptions
from .models import Exam, Question, QuestionData


@register(Exam)
class ExamTranslationOptions(TranslationOptions):
    fields = ('title',)
    required_languages = ('en',)


@register(Question)
class QuestionTranslationOptions(TranslationOptions):
    fields = ('option_1', 'option_2', 'option_3', 'option_4')
    required_languages = ('en',)

@register(QuestionData)
class QuestionDataTranslationOptions(TranslationOptions):
    fields = ('data',)
    required_languages = ('en',)

