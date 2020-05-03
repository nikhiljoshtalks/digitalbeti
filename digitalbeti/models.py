from datetime import date

from django import forms
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.db import models
import random, string
from django.utils.translation import gettext_lazy as _

# Create your models here.
from django.forms import ModelForm, RadioSelect, TextInput, Textarea
from bootstrap_datepicker.widgets import DatePicker

STATE_KEY_MAP = {
    'JAMMU AND KASHMIR': 'JK',
    'TELANGANA': 'TS',
    'TAMIL NADU': 'TN',
    'CHHATTISGARH': 'CG',
    'BIHAR': 'BR',
    'UTTAR PRADESH': 'UP',
    'KERALA': 'KL',
    'MAHARASHTRA': 'MH',
    'RAJASTHAN': 'RJ',
    'HARYANA': 'HR',
}


def generate_random_string():
    return ''.join(random.choices(string.ascii_lowercase + string.digits, k=16))


class CustomValidators:
    @staticmethod
    def validate_date_of_birth(value):
        today = date.today()
        age = today.year - value.year - ((today.month, today.day) < (value.month, value.day))
        if age < 18:
            raise ValidationError('Age needs to be in between 18 and 25 years')


class Address(models.Model):
    STATE_CHOICES = [
        ('JAMMU AND KASHMIR', 'JAMMU AND KASHMIR'),
        ('TELANGANA', 'TELANGANA'),
        ('TAMIL NADU', 'TAMIL NADU'),
        ('CHHATTISGARH', 'CHHATTISGARH'),
        ('BIHAR', 'BIHAR'),
        ('UTTAR PRADESH', 'UTTAR PRADESH'),
        ('KERALA', 'KERALA'),
        ('MAHARASHTRA', 'MAHARASHTRA'),
        ('RAJASTHAN', 'RAJASTHAN'),
        ('HARYANA', 'HARYANA'),
    ]
    state = models.CharField(max_length=100, choices=STATE_CHOICES, verbose_name=_('State'))
    subdistrict = models.CharField(max_length=100, verbose_name=_('Subdistrict'))
    district = models.CharField(max_length=100, verbose_name=_('District'))
    village = models.CharField(max_length=100, verbose_name=_('Village'))
    text = models.CharField(max_length=250, verbose_name='Full Address', blank=True)

    def __str__(self):
        return '%s:%s:%s:%s' % (self.state, self.district, self.subdistrict, self.village)


class DigitalBetiUser(models.Model):
    USER_KINDS = [
        ('USER', 'User'),
        ('VLE', 'Village Level Entrepreneur'),
        ('DM/DC', 'DM/DC'),
        ('STATE', 'States'),
        ('ADMIN', 'Admin'),
    ]
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    kind = models.CharField(max_length=100, choices=USER_KINDS)
    vle = models.ForeignKey('DigitalBetiUser', on_delete=models.SET_NULL, null=True, blank=True)
    last_login_time = models.DateTimeField(auto_now=True)
    creation_time = models.DateTimeField(auto_now_add=True)
    state = models.CharField(choices=Address.STATE_CHOICES, max_length=100, null=True)
    district = models.CharField(max_length=100, null=True, blank=True)
    subdistrict = models.CharField(max_length=100, null=True, blank=True)
    village = models.CharField(max_length=100, null=True, blank=True)
    uk = models.CharField(max_length=24, null=True, blank=True)
    prr = models.BooleanField(default=False)

    def __str__(self):
        return self.kind + ':' + self.user.username

    @classmethod
    def create_if_not_exist(cls, user, vle=None):
        try:
            digital_beti_user = user.digitalbetiuser
        except DigitalBetiUser.DoesNotExist:
            digital_beti_user = DigitalBetiUser()
            digital_beti_user.kind = 'USER'
            digital_beti_user.user = user
            if vle:
                digital_beti_user.vle = vle
            digital_beti_user.save()
        return digital_beti_user

    @property
    def examination_status(self):
        exam_count = Exam.objects.count()
        completed_count = AnswerSet.objects.filter(participant=self, result='SUCCESS').count()
        return '%s of %s' % (completed_count, exam_count)

    def certificate_hash(self):
        exam_count = Exam.objects.count()
        completed_count = AnswerSet.objects.filter(participant=self, result='SUCCESS').count()
        if exam_count == completed_count:
            return ':'.join([a.ref_hash for a in AnswerSet.objects.filter(participant=self, result='SUCCESS')])
        return None


class VillageDetails(models.Model):
    state = models.CharField(max_length=100)
    district = models.CharField(max_length=100)
    subdistrict = models.CharField(max_length=100)
    village = models.CharField(max_length=100)

    def __str__(self):
        return '%s:%s:%s:%s' % (self.state, self.district, self.subdistrict, self.village)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['state', 'district', 'subdistrict', 'village'], name='village_detail')
        ]


class BeneficiaryData(models.Model):
    GENDER_CHOICES = [(1, 'Female'), (2, 'Male')]
    EDUCATION_OPTION = [
        ('-10', 'Below 10th'),
        ('10', '10th (High School)'),
        ('12', '12th (Intermediate)'),
        ('G', 'Graduate'),
        ('PG', 'Post Graduate and Above'),
    ]
    ANNUAL_INCOME_LIST = [
        (0, 'Upto 300,000'),
        (1, 'Between 300,000 to 500,000'),
        (2, '500,000+'),
    ]
    MONTHLY_INCOME_LIST = [
        (0, '0-10,000'),
        (1, '10,000-20,000'),
        (2, '20,000+')
    ]
    YES_NO = [(True, 'Yes'), (False, 'No')]
    LANGUAGE_CHOICE = [('NA', 'Not Applicable'),
                       ('Assamese', 'Assamese'),
                       ('Bengali', 'Bengali'),
                       ('Bodo', 'Bodo'),
                       ('Dogri', 'Dogri'),
                       ('Gujarati', 'Gujarati'),
                       ('Hindi', 'Hindi'),
                       ('Kannada', 'Kannada'),
                       ('Kashmiri', 'Kashmiri'),
                       ('Konkani', 'Konkani'),
                       ('Maithili', 'Maithili'),
                       ('Malayalam', 'Malayalam'),
                       ('Manipuri', 'Manipuri'),
                       ('Marathi', 'Marathi'),
                       ('Nepali', 'Nepali'),
                       ('Oriya', 'Oriya'),
                       ('Punjabi', 'Punjabi'),
                       ('Sanskrit', 'Sanskrit'),
                       ('Santhali', 'Santhali'),
                       ('Sindhi', 'Sindhi'),
                       ('Tamil', 'Tamil'),
                       ('Telugu', 'Telugu')]
    user = models.OneToOneField(DigitalBetiUser, models.SET_NULL, null=True)
    first_name = models.CharField(max_length=100, verbose_name=_('First name'))
    middle_name = models.CharField(max_length=120, blank=True, verbose_name=_('Middle name'))
    last_name = models.CharField(max_length=120, verbose_name=_('Last name'))
    fathers_name = models.CharField(max_length=120, verbose_name=_('Father name'))
    mothers_name = models.CharField(max_length=120, verbose_name=_('Mother name'))
    gender = models.IntegerField(choices=GENDER_CHOICES, default=1, verbose_name=_('Gender'))
    date_of_birth = models.DateField(validators=[CustomValidators.validate_date_of_birth],verbose_name=_('Date of birth'))
    email_id = models.CharField(max_length=250, null=True, blank=True, verbose_name=_('Email'))
    phone_number = models.CharField(max_length=13, null=True, blank=True, verbose_name=_('Phone Number'))
    personal_monthly_income = models.IntegerField(choices=MONTHLY_INCOME_LIST, default=0,verbose_name=_('Personal monthly income'))
    permanent_address = models.ForeignKey(Address, models.SET_NULL, related_name='permanent', null=True, blank=True)
    language_pref_1 = models.CharField(verbose_name=_('First Language Preference'), max_length=30,
                                       choices=LANGUAGE_CHOICE,
                                       default='Hindi')
    language_pref_2 = models.CharField(verbose_name=_('Second Language Preference'), max_length=30,
                                       choices=LANGUAGE_CHOICE, default='NA')
    language_pref_3 = models.CharField(verbose_name=_('Third Language Preference'), max_length=30,
                                       choices=LANGUAGE_CHOICE,
                                       default='NA')
    education_qualification = models.CharField(max_length=50, choices=EDUCATION_OPTION, default='10+', verbose_name=_('Education qualification'))
    differently_abled = models.BooleanField(verbose_name=_('Are you differently abled?'), default=False, choices=YES_NO)
    bank_account = models.BooleanField(verbose_name=_('Do you have a bank account?'), default=False, choices=YES_NO)
    facebook_link = models.CharField(verbose_name=_('Facebook Profile Link'), max_length=264, null=True, blank=True)
    tc_count = models.IntegerField(verbose_name=_('Number of Training Computers'), default=0)
    vle_csc_id = models.CharField(verbose_name=_('VLE CSC ID'), max_length=20, null=True, blank=True)


class Exam(models.Model):
    title = models.CharField(max_length=100)
    urls = models.CharField(max_length=250, null=True, blank=True)

    def __str__(self):
        return self.title


class Question(models.Model):
    exam = models.ForeignKey(Exam, models.CASCADE)
    option_1 = models.CharField(max_length=1000)
    option_2 = models.CharField(max_length=1000)
    option_3 = models.CharField(max_length=1000)
    option_4 = models.CharField(max_length=1000)
    order = models.IntegerField()
    correct_answer = models.IntegerField()

    def __str__(self):
        str = self.exam.title
        for data in self.questiondata_set.all().order_by('order'):
            str += (' :: ' + data.data)
        return str


class QuestionData(models.Model):
    DATA_TYPE = [
        ('TEXT', 'Text'),
        ('IMAGE', 'Image'),
        ('VIDEO', 'Video'),
    ]
    question = models.ForeignKey(Question, models.CASCADE)
    type = models.CharField(max_length=10, choices=DATA_TYPE)
    data = models.CharField(max_length=1000)
    order = models.IntegerField()


class AnswerSet(models.Model):
    ANSWER_SET_STATUS = [
        ('STARTED', 'Started'),
        ('COMPLETED', 'Completed'),
    ]
    RESULT = [
        ('PENDING', 'Pending'),
        ('FAILED', 'Failed'),
        ('SUCCESS', 'Success'),
    ]
    ref_hash = models.CharField(max_length=16, default=generate_random_string, primary_key=True)
    status = models.CharField(max_length=10, default='STARTED', choices=ANSWER_SET_STATUS)
    result = models.CharField(max_length=10, default='PENDING', choices=RESULT)
    exam = models.ForeignKey(Exam, models.CASCADE)
    participant = models.ForeignKey(DigitalBetiUser, models.CASCADE)
    date_created = models.DateTimeField(auto_now_add=True)
    answers = models.CharField(max_length=200)
    current_question_id = models.IntegerField(default=-1)
    score = models.IntegerField(default=0)
    total_score = models.IntegerField(default=0)


class VLECompetition(models.Model):
    STATUS = [
        (0, 'PENDING'),
        (1, 'APPROVED'),
    ]
    user = models.ForeignKey(DigitalBetiUser, models.CASCADE)
    link = models.CharField(verbose_name='Facebook Profile Link', max_length=1000)
    current_likes = models.IntegerField()
    month = models.IntegerField()
    year = models.IntegerField()
    status = models.IntegerField(choices=STATUS, default=0)


class StateVideo(models.Model):
    state = models.CharField(max_length=100, choices=Address.STATE_CHOICES, verbose_name=_('State'))
    video_url = models.CharField(max_length=550)
    thumbnail = models.ImageField(upload_to='state_video/', blank=True)

    def __str__(self):
        return '%s : %s' % (self.state, self.video_url)
