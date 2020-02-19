import json

from django.contrib import messages
from django.contrib.auth import authenticate, logout, login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.shortcuts import render, redirect
from django.urls import reverse
from django.utils import translation
from django.views.decorators.csrf import csrf_exempt
from django_weasyprint import WeasyTemplateView

from digibeti import settings
from digitalbeti.forms import BeneficiaryDataForm, AddressForm, SignUpForm, VLEDataForm
from digitalbeti.models import DigitalBetiUser, BeneficiaryData, Exam, AnswerSet, Question, VillageDetails
from django.http import JsonResponse
from django.utils.translation import gettext_lazy as _
import logging

logger = logging.getLogger(__name__)


# Create your views here.

def index(request):
    # from django.utils import translation
    # user_language = 'hi'
    # translation.activate(user_language)
    # request.session[translation.LANGUAGE_SESSION_KEY] = user_language

    # if translation.LANGUAGE_SESSION_KEY in request.session:
    #     del request.session[translation.LANGUAGE_SESSION_KEY]

    context = {'home': True}
    return render(request, 'digitalbeti/index.html', context)


def impact(request):
    context = {'impact': True}
    return render(request, 'digitalbeti/impact.html', context)


def about_facebook(request):
    context = {'about_fb': True}
    return render(request, 'digitalbeti/about-facebook.html', context)


def about_project(request):
    context = {'about_project': True}
    return render(request, 'digitalbeti/about-project.html', context)


def about_csc(request):
    context = {'about_csc': True}
    return render(request, 'digitalbeti/about-csc.html', context)


def jobs(request):
    context = {}
    return render(request, 'digitalbeti/jobs.html', context)


def digital_marketing(request):
    context = {}
    return render(request, 'digitalbeti/digital-marketing.html', context)


def online_safety(request):
    context = {}
    return render(request, 'digitalbeti/safety.html', context)


@login_required
def user_logout(request):
    logger.debug("Logging out user: %s", request.user.username)
    logout(request)
    messages.success(request, _("You have been successfully logged out."))
    return redirect(reverse('login'))


@login_required
def curriculum(request):
    return render(request, 'digitalbeti/logged-in/user/curriculum/curriculum.html', context={})


@login_required
def vle_dashboard(request):
    return render(request, 'digitalbeti/logged-in/vle/vle_dashboard.html', context={})


@login_required
def vle_register_user_prompt(request):
    return render(request, 'digitalbeti/logged-in/vle/registration-user-prompt.html', context={})


def preregistered(email_id):
    pass


@login_required
def vle_register_user(request):
    beneficiary_data_form = BeneficiaryDataForm(
        request.POST or None, )
    permanent_address_form = AddressForm(
        request.POST or None, prefix='permanent')

    if request.method == 'POST':
        if beneficiary_data_form.is_valid() and permanent_address_form.is_valid():
            data = beneficiary_data_form.save(commit=False)
            if User.objects.filter(email=data.email_id):
                beneficiary_data_form.add_error('email_id', 'User already exists')
                messages.error(request, "User with email already registered: %s" % data.email_id)
                return render(request, 'digitalbeti/logged-in/vle/new-user-registration.html',
                              context={'form': beneficiary_data_form, 'paf': permanent_address_form})
            user = User.objects.create_user(data.email_id, data.email_id, '12345')
            user.first_name = data.first_name
            user.last_name = data.last_name
            user.save()
            dbu = DigitalBetiUser.create_if_not_exist(user, vle=request.user.digitalbetiuser)
            padd_data = permanent_address_form.save()
            data.permanent_address = padd_data
            data.user = dbu
            data.save()
            messages.success(request, 'User registered successfully.')
            return redirect(reverse('reg_user'))

    return render(request, 'digitalbeti/logged-in/vle/new-user-registration.html',
                  context={'form': beneficiary_data_form, 'paf': permanent_address_form})


@login_required
def vle_reg_history(request):
    register_users = DigitalBetiUser.objects.filter(vle=request.user.digitalbetiuser)
    return render(request, 'digitalbeti/logged-in/vle/registration-history.html', context={'ru': register_users})


@login_required
def vle_exams_history(request):
    register_users = DigitalBetiUser.objects.filter(vle=request.user.digitalbetiuser)
    answer_sets = AnswerSet.objects.filter(participant__in=register_users)
    return render(request, 'digitalbeti/logged-in/vle/examination-history.html', context={'as': answer_sets})


@login_required
def vle_competition(request):
    return render(request, 'digitalbeti/logged-in/vle/competition.html', context={})


@login_required
def vle_assets(request):
    return render(request, 'digitalbeti/logged-in/vle/ice-material.html', context={})


@login_required
def user_dashboard(request):
    digital_beti_user = request.user.digitalbetiuser
    if digital_beti_user.kind == 'USER':
        beneficiary_details_data = BeneficiaryData.objects.filter(user=request.user.digitalbetiuser)
        if not beneficiary_details_data:
            return redirect(reverse('not_registered'))
        return redirect(reverse('profile'))

    if digital_beti_user.kind == 'VLE':
        vle_details_data = BeneficiaryData.objects.filter(user=request.user.digitalbetiuser)
        if not vle_details_data:
            return redirect(reverse('vle_not_registered'))
        total_registered_users = digital_beti_user.digitalbetiuser_set.all()
        total_registered = total_registered_users.count()
        total_exams_given = AnswerSet.objects.filter(
            participant__in=total_registered_users, status='COMPLETED').values('participant').distinct().count()
        total_passed = AnswerSet.objects.filter(
            participant__in=total_registered_users, result='SUCCESS').values('participant').distinct().count()
        total_failed = AnswerSet.objects.filter(
            participant__in=total_registered_users, result='FAILED').values('participant').distinct().count()
        return render(request, 'digitalbeti/logged-in/vle/vle_dashboard.html',
                      {'total_registered': total_registered, 'total_exams_given': total_exams_given,
                       'total_passed': total_passed, 'total_failed': total_failed})

    if digital_beti_user.kind == 'DM/DC':
        vles = DigitalBetiUser.objects.filter(kind='VLE', state=digital_beti_user.state,
                                              district=digital_beti_user.district)
        return render(request, 'digitalbeti/logged-in/dmdc/dmdc_dashboard.html', {'vles': vles})

    if digital_beti_user.kind == 'STATE':
        vles = DigitalBetiUser.objects.filter(kind='VLE', state=digital_beti_user.state)
        return render(request, 'digitalbeti/logged-in/state/state_dashboard.html', {'vles': vles})


def user_login(request):
    if request.user.is_authenticated:
        return redirect(reverse('user_dashboard'))
    if request.method == 'POST':
        username = request.POST.get('username')
        user = authenticate(username=username,
                            password=request.POST.get('password'))
        if user:
            login(request, user)
            dbu = DigitalBetiUser.create_if_not_exist(user)
            dbu.save()
            return redirect(reverse('user_dashboard'))
        return render(request, 'digitalbeti/login.html',
                      dict(error_message='Invalid username or password.', username=username))

    return render(request, 'digitalbeti/login.html', {})


def user_signup(request):
    if request.user.is_authenticated:
        return redirect(reverse('user_dashboard'))
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            raw_password = form.cleaned_data.get('password1')
            user = authenticate(username=username, password=raw_password)
            login(request, user)
            DigitalBetiUser.create_if_not_exist(user)
            return redirect(reverse('user_dashboard'))
    else:
        form = SignUpForm()
    return render(request, 'digitalbeti/signup.html', {'form': form})


@login_required
def not_registerd(request):
    return render(request, 'digitalbeti/logged-in/user/not-registered.html', context={})


@login_required
def vle_not_registerd(request):
    return render(request, 'digitalbeti/vle/templates/digitalbeti/logged-in/vle/not-registered.html', context={})


@login_required
def beneficiary_details_input(request):
    if request.method == 'GET':
        beneficiary_details = BeneficiaryData.objects.filter(user=request.user.digitalbetiuser)
        if beneficiary_details.first():
            messages.warning(request, 'User already registered')
            return redirect(reverse('user_dashboard'))

    initial_data = {}
    if request.user.digitalbetiuser.kind == 'USER':
        initial_data['email_id'] = request.user.email
        initial_data['first_name'] = request.user.first_name
        initial_data['last_name'] = request.user.last_name

    beneficiary_data_form = BeneficiaryDataForm(
        request.POST or None, initial=initial_data)
    permanent_address_form = AddressForm(
        request.POST or None, prefix='permanent')
    if request.method == 'POST':
        if beneficiary_data_form.is_valid() and permanent_address_form.is_valid():
            data = beneficiary_data_form.save(commit=False)
            padd_data = permanent_address_form.save()
            data.permanent_address = padd_data
            data.user = request.user.digitalbetiuser
            data.save()
            messages.success(request, 'User registered successfully.')
            return render(request, 'digitalbeti/logged-in/user/form-completed.html')

    return render(request, 'digitalbeti/logged-in/user/registration-form.html',
                  context={'form': beneficiary_data_form, 'paf': permanent_address_form})


@login_required
def vle_details_input(request):
    if request.method == 'GET':
        beneficiary_details = BeneficiaryData.objects.filter(user=request.user.digitalbetiuser)
        if beneficiary_details.first():
            messages.warning(request, 'User already registered')
            return redirect(reverse('user_dashboard'))

    initial_data = {}
    if request.user.digitalbetiuser.kind == 'VLE':
        initial_data['email_id'] = request.user.email
        initial_data['first_name'] = request.user.first_name
        initial_data['last_name'] = request.user.last_name

    vle_data_form = VLEDataForm(
        request.POST or None, initial=initial_data)
    if request.method == 'POST':
        if vle_data_form.is_valid():
            data = vle_data_form.save(commit=False)
            data.user = request.user.digitalbetiuser
            data.save()
            messages.success(request, 'VLE registered successfully.')
            return redirect(reverse('user_dashboard'))

    return render(request, 'digitalbeti/logged-in/vle/registration-form.html', context={'form': vle_data_form})


@login_required
def user_profile(request):
    beneficiary_details = BeneficiaryData.objects.filter(user=request.user.digitalbetiuser)
    if not beneficiary_details.first():
        return redirect(reverse('not_registered'))
    beneficiary_details = beneficiary_details.first()
    return render(request, 'digitalbeti/logged-in/user/profile.html', context={'details': beneficiary_details})


@login_required
def user_exam(request):
    beneficiary_details = BeneficiaryData.objects.filter(user=request.user.digitalbetiuser)
    if not beneficiary_details.first():
        return redirect(reverse('not_registered'))
    exams = Exam.objects.all()
    if request.method == 'POST' and request.POST.get('exam_id'):
        exam_id = int(request.POST.get('exam_id'))
        try:
            exam = Exam.objects.get(id=exam_id)
        except Exam.DoesNotExist:
            messages.error(request, "Exam not found")
            return render(request, 'digitalbeti/logged-in/user/exams.html', context={'exams': exams})
        is_completed_answer_set = AnswerSet.objects.filter(participant=request.user.digitalbetiuser, exam=exam,
                                                           result='SUCCESS').first()
        if is_completed_answer_set:
            messages.warning(request, 'Exam already completed.')
            return redirect(reverse('completed_exam', args=[is_completed_answer_set.ref_hash]))
        answer_set = AnswerSet()
        answer_set.exam = exam
        answer_set.participant = request.user.digitalbetiuser
        answer_set.save()
        return redirect(reverse('conduct_exams', args=[answer_set.ref_hash]))

    return render(request, 'digitalbeti/logged-in/user/exams.html', context={'exams': exams})


@login_required
def vle_user_exam(request, user_id=None):
    user_id = request.GET.get('user_id', None)
    exams = Exam.objects.all()
    if request.method == 'POST' and request.POST.get('exam_id'):
        application_number = request.POST.get('app_number')
        application_number = application_number.replace('DB', '')
        application_number = int(application_number)
        try:
            participant = BeneficiaryData.objects.get(id=application_number)
        except:
            messages.error(request, "User not found")
            return render(request, 'digitalbeti/logged-in/vle/conduct-examination-prompt.html',
                          context={'exams': exams})
        exam_id = int(request.POST.get('exam_id'))
        try:
            exam = Exam.objects.get(id=exam_id)
        except Exam.DoesNotExist:
            messages.error(request, "Exam not found")
            return render(request, 'digitalbeti/logged-in/user/exams.html', context={'exams': exams})
        is_completed_answer_set = AnswerSet.objects.filter(participant=participant.user, exam=exam,
                                                           result='SUCCESS').first()
        if is_completed_answer_set:
            messages.warning(request, 'Exam already completed.')
            return redirect(reverse('completed_exam', args=[is_completed_answer_set.ref_hash]))
        answer_set = AnswerSet()
        answer_set.exam = exam
        answer_set.participant = participant.user
        answer_set.save()
        return redirect(reverse('conduct_exams', args=[answer_set.ref_hash]))
    return render(request, 'digitalbeti/logged-in/vle/conduct-examination-prompt.html',
                  context={'user_id': user_id, 'exams': exams})


@login_required
def conduct_exams(request, ref_hash):
    try:
        answer_set = AnswerSet.objects.get(ref_hash=ref_hash)
    except AnswerSet.DoesNotExist:
        messages.error(
            request, "Exam not started, please select an exam and try again")
        return redirect(reverse('exams'))

    if answer_set.status == 'COMPLETED':
        messages.success(request, "Exam already completed.")
        return redirect(reverse('completed_exam', args=[ref_hash]))

    if request.method == 'POST':
        question_id = int(request.POST.get('question_id'))
        answer = int(request.POST.get('answer'))
        all_questions = answer_set.exam.question_set.all().order_by('order')
        all_questions = [q for q in all_questions]
        question_index = -1
        for i in range(len(all_questions)):
            if all_questions[i].id == question_id:
                question_index = i
        current_question = all_questions[question_index]
        answer_set.total_score = 1 + (answer_set.total_score or 0)
        if current_question.correct_answer == answer:
            answer_set.score = 1 + (answer_set.score or 0)
        if question_index == len(all_questions) - 1:
            answer_set.result = 'SUCCESS' if answer_set.score / answer_set.total_score >= 0.5 else 'FAILED'
            answer_set.status = 'COMPLETED'
            answer_set.save()
            return redirect(reverse('completed_exam', args=[answer_set.ref_hash]))
        else:
            next_question = all_questions[question_index + 1]
            answer_set.current_question_id = next_question.id
        answer_set.save()

    exam = answer_set.exam
    current_question_id = answer_set.current_question_id or -1
    if current_question_id == -1:
        current_question = exam.question_set.all().order_by('order').first()
    else:
        current_question = Question.objects.get(id=current_question_id)

    return render(request, 'digitalbeti/logged-in/user/conduct_exams.html', context={
        'exam': answer_set.exam,
        'answer_set': answer_set,
        'question': current_question,
        'question_data': current_question.questiondata_set.all().order_by('order'),
        'skip_menu': True,
    })


def completed_exam(request, ref_hash):
    try:
        answer_set = AnswerSet.objects.get(ref_hash=ref_hash)
    except AnswerSet.DoesNotExist:
        messages.error(request, "Exam doesn't exist.")
        return redirect(reverse('exams'))
    if answer_set.status == 'STARTED':
        messages.error(
            request, "Exam still not completed, please complete it.")
        return redirect(reverse('conduct_exams', args=[answer_set.ref_hash]))
    score = answer_set.score
    total_score = answer_set.total_score
    success = score / total_score > 0.5
    return render(request, 'digitalbeti/logged-in/user/completed-exam.html', context={
        'exam': answer_set.exam,
        'answer_set': answer_set,
        'success': success
    })


class CertificateView(WeasyTemplateView):
    print(settings.BASE_DIR + '/bin/certificate.css')
    pdf_stylesheets = [
        settings.BASE_DIR + '/bin/certificate.css',
    ]
    template_name = "digitalbeti/certificate/certificate.html"

    def get_context_data(self, **kwargs):
        try:
            answer_set = AnswerSet.objects.get(ref_hash=kwargs.get('ref_hash'))
        except AnswerSet.DoesNotExist:
            answer_set = None
        context = super().get_context_data(**kwargs)
        context['answer_set'] = answer_set
        return context


@csrf_exempt
def get_districts_for_state(request):
    data = json.loads(request.body)
    state = data.get('state')
    districts = VillageDetails.objects.filter(state=state).values('district').distinct()
    districts = [d.get('district') for d in districts]
    return JsonResponse(dict(state=state, districts=districts))


@csrf_exempt
def get_subdistrict_for_state_and_district(request):
    data = json.loads(request.body)
    state = data.get('state')
    district = data.get('district')
    cities = VillageDetails.objects.filter(state=state, district=district).values('subdistrict').distinct()
    cities = [d.get('subdistrict') for d in cities]
    return JsonResponse(dict(state=state, district=district, cities=cities))


@csrf_exempt
def get_village_for_state_and_district_village(request):
    data = json.loads(request.body)
    state = data.get('state')
    district = data.get('district')
    subdistrict = data.get('subdistrict')
    village = VillageDetails.objects.filter(state=state, district=district, subdistrict=subdistrict).values(
        'village').distinct()
    village = [d.get('village') for d in village]
    return JsonResponse(dict(state=state, district=district, subdistrict=subdistrict, villages=village))


@login_required()
def dmdc_vle_details(request, user_id):
    dbu = DigitalBetiUser.objects.get(id=user_id)
    total_registered_users = dbu.digitalbetiuser_set.all()
    total_registered = total_registered_users.count()
    total_exams_given = AnswerSet.objects.filter(
        participant__in=total_registered_users, status='COMPLETED').values('participant').distinct().count()
    total_passed = AnswerSet.objects.filter(
        participant__in=total_registered_users, result='SUCCESS').values('participant').distinct().count()
    total_failed = AnswerSet.objects.filter(
        participant__in=total_registered_users, result='FAILED').values('participant').distinct().count()
    return render(request, 'digitalbeti/logged-in/vle/vle_dashboard.html',
                  {'vle': dbu, 'total_registered': total_registered, 'total_exams_given': total_exams_given,
                   'total_passed': total_passed, 'total_failed': total_failed})


@login_required()
def state_vle_details(request, user_id):
    dbu = DigitalBetiUser.objects.get(id=user_id)
    total_registered_users = dbu.digitalbetiuser_set.all()
    total_registered = total_registered_users.count()
    total_exams_given = AnswerSet.objects.filter(
        participant__in=total_registered_users, status='COMPLETED').values('participant').distinct().count()
    total_passed = AnswerSet.objects.filter(
        participant__in=total_registered_users, result='SUCCESS').values('participant').distinct().count()
    total_failed = AnswerSet.objects.filter(
        participant__in=total_registered_users, result='FAILED').values('participant').distinct().count()
    return render(request, 'digitalbeti/logged-in/vle/vle_dashboard.html',
                  {'vle': dbu, 'total_registered': total_registered, 'total_exams_given': total_exams_given,
                   'total_passed': total_passed, 'total_failed': total_failed})
