from modeltranslation.translator import register, TranslationOptions
from .models import Exam

@register(Exam)
class ExamTranslationOptions(TranslationOptions):
    fields = ('title','urls')

# translator.register(News, NewsTranslationOptions)
