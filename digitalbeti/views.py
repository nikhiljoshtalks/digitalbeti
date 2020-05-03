import csv
import json

from django.contrib import messages
from django.contrib.auth import authenticate, logout, login, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth.models import User
from django.db.models import Count
from django.shortcuts import render, redirect
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt
from django_weasyprint import WeasyTemplateView

from digibeti import settings
from digitalbeti.forms import BeneficiaryDataForm, AddressForm, SignUpForm, VLEDataForm

from digitalbeti.models import DigitalBetiUser, BeneficiaryData, Exam, AnswerSet, Question, VillageDetails, \
    STATE_KEY_MAP, VLECompetition, StateVideo
from django.http import JsonResponse
from datetime import date
from django.utils.translation import gettext_lazy as _

import logging

logger = logging.getLogger(__name__)


# Create your views here.

def index(request):
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


def state(request):
    states = StateVideo.objects.all()
    context = {
        'state': True,
        'states': states
    }
    return render(request, 'digitalbeti/state.html', context)


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
def vle_register_user_prompt(request):
    if request.user.digitalbetiuser.prr:
        messages.warning(request, "You need to reset your password to continue.")
        return redirect(reverse('reset_password'))

    vle_details_data = BeneficiaryData.objects.filter(user=request.user.digitalbetiuser)
    if not vle_details_data:
        return redirect(reverse('vle_not_registered'))
    return render(request, 'digitalbeti/logged-in/vle/registration-user-prompt.html', context={})


@login_required
def vle_register_user(request):
    if request.user.digitalbetiuser.prr:
        messages.warning(request, "You need to reset your password to continue.")
        return redirect(reverse('reset_password'))

    vle_details_data = BeneficiaryData.objects.filter(user=request.user.digitalbetiuser)
    if not vle_details_data:
        return redirect(reverse('vle_not_registered'))
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
            dbu.state = padd_data.state
            dbu.district = padd_data.district
            dbu.subdistrict = padd_data.subdistrict
            dbu.village = padd_data.village
            dbu.uk = '%s%s%06d' % (STATE_KEY_MAP.get(padd_data.state), 'VLE', dbu.id)
            dbu.prr = True
            dbu.save()
            messages.success(request, 'User registered successfully.')
            return redirect(reverse('reg_user'))

    return render(request, 'digitalbeti/logged-in/vle/new-user-registration.html',
                  context={'form': beneficiary_data_form, 'paf': permanent_address_form})


@login_required
def vle_reg_history(request):
    if request.user.digitalbetiuser.prr:
        messages.warning(request, "You need to reset your password to continue.")
        return redirect(reverse('reset_password'))

    vle_details_data = BeneficiaryData.objects.filter(user=request.user.digitalbetiuser)
    if not vle_details_data:
        return redirect(reverse('vle_not_registered'))
    register_users = DigitalBetiUser.objects.filter(vle=request.user.digitalbetiuser)
    return render(request, 'digitalbeti/logged-in/vle/registration-history.html', context={'ru': register_users})


@login_required
def vle_exams_history(request):
    if request.user.digitalbetiuser.prr:
        messages.warning(request, "You need to reset your password to continue.")
        return redirect(reverse('reset_password'))

    vle_details_data = BeneficiaryData.objects.filter(user=request.user.digitalbetiuser)
    if not vle_details_data:
        return redirect(reverse('vle_not_registered'))
    register_users = DigitalBetiUser.objects.filter(vle=request.user.digitalbetiuser)
    answer_sets = AnswerSet.objects.filter(participant__in=register_users)
    return render(request, 'digitalbeti/logged-in/vle/examination-history.html', context={'as': answer_sets})


@login_required
def vle_competition(request):
    if request.user.digitalbetiuser.prr:
        messages.warning(request, "You need to reset your password to continue.")
        return redirect(reverse('reset_password'))

    vle_details_data = BeneficiaryData.objects.filter(user=request.user.digitalbetiuser)
    if not vle_details_data:
        return redirect(reverse('vle_not_registered'))
    month = date.today().month
    year = date.today().year
    entry = VLECompetition.objects.filter(user=request.user.digitalbetiuser, month=month, year=year).first()
    context = dict(
    )
    if entry:
        context['already_participated'] = True
    return render(request, 'digitalbeti/logged-in/vle/competition.html', context=context)


@login_required
def vle_assets(request):
    if request.user.digitalbetiuser.prr:
        messages.warning(request, "You need to reset your password to continue.")
        return redirect(reverse('reset_password'))

    vle_details_data = BeneficiaryData.objects.filter(user=request.user.digitalbetiuser)
    if not vle_details_data:
        return redirect(reverse('vle_not_registered'))
    return render(request, 'digitalbeti/logged-in/vle/ice-material.html', context={})


@login_required
def user_dashboard(request):
    if request.user.is_superuser:
        dbu = DigitalBetiUser.create_if_not_exist(request.user)
        if dbu.kind != 'ADMIN':
            dbu.kind = 'ADMIN'
            dbu.save()

    digital_beti_user = request.user.digitalbetiuser
    if digital_beti_user.prr:
        messages.warning(request, "You need to reset your password to continue.")
        return redirect(reverse('reset_password'))

    if digital_beti_user.kind == 'USER':
        beneficiary_details_data = BeneficiaryData.objects.filter(user=request.user.digitalbetiuser)
        if not beneficiary_details_data:
            return redirect(reverse('not_registered'))

        return user_overview(request)

    if digital_beti_user.kind == 'VLE':
        vle_details_data = BeneficiaryData.objects.filter(user=request.user.digitalbetiuser)
        if not vle_details_data:
            return redirect(reverse('vle_not_registered'))

        return vle_overview(request)

    if digital_beti_user.kind == 'DM/DC':
        if not digital_beti_user.district:
            return redirect(reverse('dmdc_district_input'))
        return dmdc_overview(request)

    if digital_beti_user.kind == 'STATE':
        return state_overview(request)

    if digital_beti_user.kind == 'ADMIN':
        return admin_overview(request)


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
def reset_password(request):
    form = PasswordChangeForm(request.user, request.POST or None)
    if request.method == 'POST':
        if form.is_valid():
            form.save()
            request.user.digitalbetiuser.prr = False
            request.user.digitalbetiuser.save()
            update_session_auth_hash(request, form.user)
            return redirect(reverse('user_dashboard'))
    return render(request, 'digitalbeti/logged-in/reset-password.html', context={'form': form})


@login_required
def not_registerd(request):
    return render(request, 'digitalbeti/logged-in/user/not-registered.html', context={})


@login_required
def vle_not_registerd(request):
    return render(request, 'digitalbeti/logged-in/vle/not-registered.html', context={})


@login_required
def beneficiary_details_input(request):
    if request.user.digitalbetiuser.prr:
        messages.warning(request, "You need to reset your password to continue.")
        return redirect(reverse('reset_password'))
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
            dbu = request.user.digitalbetiuser
            data = beneficiary_data_form.save(commit=False)
            padd_data = permanent_address_form.save()
            data.permanent_address = padd_data
            data.user = dbu
            data.save()
            dbu.state = padd_data.state
            dbu.district = padd_data.district
            dbu.subdistrict = padd_data.subdistrict
            dbu.village = padd_data.village
            dbu.uk = '%s%s%06d' % (STATE_KEY_MAP.get(padd_data.state), 'DIR', dbu.id)
            dbu.save()
            messages.success(request, 'User registered successfully.')
            return render(request, 'digitalbeti/logged-in/user/form-completed.html')

    return render(request, 'digitalbeti/logged-in/user/registration-form.html',
                  context={'form': beneficiary_data_form, 'paf': permanent_address_form})


@login_required
def vle_details_input(request):
    if request.user.digitalbetiuser.prr:
        messages.warning(request, "You need to reset your password to continue.")
        return redirect(reverse('reset_password'))
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
    permanent_address_form = AddressForm(
        request.POST or None, prefix='permanent')
    if request.method == 'POST':
        if vle_data_form.is_valid() and permanent_address_form.is_valid():
            data = vle_data_form.save(commit=False)
            data.user = request.user.digitalbetiuser
            padd_data = permanent_address_form.save()
            data.permanent_address = padd_data
            data.save()
            request.user.digitalbetiuser.state = padd_data.state
            request.user.digitalbetiuser.district = padd_data.district
            request.user.digitalbetiuser.subdistrict = padd_data.subdistrict
            request.user.digitalbetiuser.village = padd_data.village
            request.user.digitalbetiuser.save()
            messages.success(request, 'VLE registered successfully.')
            return redirect(reverse('user_dashboard'))

    return render(request, 'digitalbeti/logged-in/vle/registration-form.html', context={
        'form': vle_data_form, 'paf': permanent_address_form})


@login_required
def user_exam(request):
    if request.user.digitalbetiuser.prr:
        messages.warning(request, "You need to reset your password to continue.")
        return redirect(reverse('reset_password'))

    beneficiary_details = BeneficiaryData.objects.filter(user=request.user.digitalbetiuser)
    if not beneficiary_details.first():
        return redirect(reverse('not_registered'))
    exams = Exam.objects.all()
    answer_sets = AnswerSet.objects.filter(participant=request.user.digitalbetiuser, status='COMPLETED',
                                           result='SUCCESS')
    completed_exams = []
    completed_exams_hash = ''
    for answer_set in answer_sets:
        completed_exams.append(answer_set.exam_id)
        completed_exams_hash += answer_set.ref_hash + ':'
    finished = []
    unfinished = []
    can_download_certificate = False
    for exam in exams:
        if exam.id in completed_exams:
            finished.append(exam)
        else:
            unfinished.append(exam)
    if not unfinished:
        can_download_certificate = True
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

    return render(request, 'digitalbeti/logged-in/user/exams.html',
                  context={'exams': unfinished, 'can_download_certificate': can_download_certificate,
                           'completed_exams_hash': completed_exams_hash})


@login_required
def vle_user_exam(request):
    if request.user.digitalbetiuser.prr:
        messages.warning(request, "You need to reset your password to continue.")
        return redirect(reverse('reset_password'))

    vle_details_data = BeneficiaryData.objects.filter(user=request.user.digitalbetiuser)
    if not vle_details_data:
        return redirect(reverse('vle_not_registered'))
    user_id = request.GET.get('user_id', None)
    exams = Exam.objects.all()
    if request.method == 'POST' and request.POST.get('exam_id'):
        application_number = request.POST.get('app_number')
        application_number = application_number.replace('DB', '')
        application_number = application_number.replace('VLE', '')
        application_number = application_number.replace('DIR', '')
        application_number = int(application_number)
        try:
            participant = DigitalBetiUser.objects.get(id=application_number)
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
        is_completed_answer_set = AnswerSet.objects.filter(participant=participant, exam=exam,
                                                           result='SUCCESS').first()
        if is_completed_answer_set:
            messages.warning(request, 'Exam already completed.')
            return redirect(reverse('completed_exam', args=[is_completed_answer_set.ref_hash]))
        answer_set = AnswerSet()
        answer_set.exam = exam
        answer_set.participant = participant
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
        ref_hash_all = kwargs.get('ref_hash')
        ref_hashes = ref_hash_all.split(':')
        final_ref = []
        for ref_hash in ref_hashes:
            if ref_hash.strip():
                final_ref.append(ref_hash.strip())
        answer_sets = AnswerSet.objects.filter(ref_hash__in=final_ref, status='COMPLETED', result='SUCCESS')

        context = super().get_context_data(**kwargs)
        context['answer_set'] = answer_sets.first()
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


def vle_competition_input(request):
    vle_details_data = BeneficiaryData.objects.filter(user=request.user.digitalbetiuser)
    if not vle_details_data:
        return redirect(reverse('vle_not_registered'))
    month = date.today().month
    year = date.today().year
    entry = VLECompetition.objects.filter(user=request.user.digitalbetiuser, month=month, year=year).first()
    if entry:
        return redirect(reverse('competition'))
    form = VLECompetitionForm(request.POST or None)
    if request.method == 'POST':
        if form.is_valid():
            d = form.save(commit=False)
            d.user = request.user.digitalbetiuser
            d.month = date.today().month
            d.year = date.today().year
            d.save()
            return redirect(reverse('user_dashboard'))
    context = {
        'form': form
    }
    return render(request, 'digitalbeti/logged-in/vle/competition_input.html', context=context)


@login_required
def admin_create_user(request):
    if request.user.digitalbetiuser.kind != 'ADMIN':
        messages.error(request, "Only admin allowed to create user")
        return redirect(reverse('user_dashboard'))
    form = UserCreateForm(request.POST or None)
    if request.method == 'POST':
        if form.is_valid():
            if User.objects.filter(email=form.cleaned_data.get('email')):
                messages.error(request, "User with email already registered: %s" % form.cleaned_data.get('email'))
                form.add_error('email', 'User already exists')
                return render(request, 'digitalbeti/logged-in/admin/create-user.html', context={'form': form})
            user = User.objects.create_user(form.cleaned_data.get('email'), form.cleaned_data.get('email'), '12345')
            user.first_name = form.cleaned_data.get('first_name')
            user.last_name = form.cleaned_data.get('last_name')
            user.save()
            dbu = form.save(commit=False)
            dbu.user = user
            dbu.prr = True
            dbu.save()
            messages.success(request, 'User successfully created.')
            form = UserCreateForm()

    return render(request, 'digitalbeti/logged-in/admin/create-user.html', context={'form': form})


@login_required
def admin_create_user_bulk(request):
    if request.user.digitalbetiuser.kind != 'ADMIN':
        messages.error(request, "Only admin allowed to create user")
        return redirect(reverse('user_dashboard'))

    form = BulkVLECreation()
    if request.method == 'POST':
        file_data = request.FILES['csv_file']
        decoded_file = file_data.read().decode('utf-8').splitlines()
        data = csv.reader(decoded_file)
        for line in data:
            if line[0].lower() == 'email':
                continue
            try:
                success, error = create_vle(line[0], line[1], line[2], line[3], line[4])
                if not success:
                    messages.error(request, "[%s] Could not create user %s" % (error, line[0]))
            except:
                messages.error(request, "Could not create user %s" % line[0])
        return render(request, 'digitalbeti/logged-in/admin/create-user-bulk.html',
                      context={'success': True, 'form': form})
    return render(request, 'digitalbeti/logged-in/admin/create-user-bulk.html', context={'form': form})


@login_required
def user_overview(request):
    if request.user.digitalbetiuser.prr:
        messages.warning(request, "You need to reset your password to continue.")
        return redirect(reverse('reset_password'))

    beneficiary_details = BeneficiaryData.objects.filter(user=request.user.digitalbetiuser)
    if not beneficiary_details.first():
        return redirect(reverse('not_registered'))
    beneficiary_details = beneficiary_details.first()
    return render(request, 'digitalbeti/logged-in/user/profile.html', context={'details': beneficiary_details})


@login_required
def vle_overview(request, user_id=None):
    if not user_id:
        digital_beti_user = request.user.digitalbetiuser
    else:
        digital_beti_user = DigitalBetiUser.objects.get(id=user_id)
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


@login_required
def dmdc_overview(request, district=None):
    if not district:
        digital_beti_user = request.user.digitalbetiuser
    else:
        digital_beti_user = DigitalBetiUser.objects.filter(district=district).first()
    total_registered_users = DigitalBetiUser.objects.filter(
        state=digital_beti_user.state, district=digital_beti_user.district, kind='USER')
    vle_count = DigitalBetiUser.objects.filter(
        state=digital_beti_user.state, district=digital_beti_user.district, kind='VLE').count()
    user_count = total_registered_users.count()
    total_exams_given = AnswerSet.objects.filter(
        participant__in=total_registered_users, status='COMPLETED').values('participant').distinct().count()
    total_passed = AnswerSet.objects.filter(
        participant__in=total_registered_users, result='SUCCESS').values('participant').distinct().count()
    total_failed = AnswerSet.objects.filter(
        participant__in=total_registered_users, result='FAILED').values('participant').distinct().count()
    subdistrict_count = DigitalBetiUser.objects.filter(
        state=digital_beti_user.state, district=digital_beti_user.district).values(
        'subdistrict').distinct().count()
    village_count = DigitalBetiUser.objects.filter(
        state=digital_beti_user.state, district=digital_beti_user.district).values(
        'village').distinct().count()
    top_vles = DigitalBetiUser.objects.filter(
        kind='VLE', state=digital_beti_user.state, district=digital_beti_user.district).annotate(
        num_reg=Count('digitalbetiuser')).order_by('-num_reg')[:3]
    return render(request, 'digitalbeti/logged-in/dmdc/dmdc_dashboard.html',
                  {'district': digital_beti_user.district, 'state': digital_beti_user.state,
                   'total_registered': user_count, 'vle_count': vle_count, 'total_exams_given': total_exams_given,
                   'total_passed': total_passed, 'total_failed': total_failed, 'subdistrict_count': subdistrict_count,
                   'village_count': village_count, 'top_vle': top_vles})


@login_required
def dmdc_all_vle(request, district=None):
    if not district:
        digital_beti_user = request.user.digitalbetiuser
    else:
        digital_beti_user = DigitalBetiUser.objects.filter(district=district).first()
    vles = DigitalBetiUser.objects.filter(
        kind='VLE', state=digital_beti_user.state, district=digital_beti_user.district)
    return render(request, 'digitalbeti/logged-in/dmdc/all_vles.html',
                  {'district': digital_beti_user.district, 'vles': vles})


@login_required
def dmdc_top_vle(request):
    digital_beti_user = request.user.digitalbetiuser
    top_vles = DigitalBetiUser.objects.filter(
        kind='VLE', state=digital_beti_user.state, district=digital_beti_user.district).annotate(
        num_reg=Count('digitalbetiuser')).order_by('-num_reg')[:10]
    return render(request, 'digitalbeti/logged-in/dmdc/top_users.html',
                  {'district': digital_beti_user.district, 'vles': top_vles})


@login_required
def dmdc_district_input(request):
    form = DMDCDistrictInput(request.POST or None, instance=request.user.digitalbetiuser)
    if request.method == 'POST':
        if form.is_valid():
            form.save()
            return redirect(reverse('user_dashboard'))
    return render(request, 'digitalbeti/logged-in/dmdc/dmdc_district_input.html', context={'form': form})


@login_required
def state_overview(request, state=None):
    if not state:
        digital_beti_user = request.user.digitalbetiuser
    else:
        digital_beti_user = DigitalBetiUser.objects.filter(state=state).first()
    total_registered_users = DigitalBetiUser.objects.filter(
        state=digital_beti_user.state, kind='USER')
    vle_count = DigitalBetiUser.objects.filter(
        state=digital_beti_user.state, kind='VLE').count()
    user_count = total_registered_users.count()
    total_exams_given = AnswerSet.objects.filter(
        participant__in=total_registered_users, status='COMPLETED').values('participant').distinct().count()
    total_passed = AnswerSet.objects.filter(
        participant__in=total_registered_users, result='SUCCESS').values('participant').distinct().count()
    total_failed = AnswerSet.objects.filter(
        participant__in=total_registered_users, result='FAILED').values('participant').distinct().count()
    district_count = DigitalBetiUser.objects.filter(state=digital_beti_user.state).values(
        'district').distinct().count()
    subdistrict_count = DigitalBetiUser.objects.filter(state=digital_beti_user.state).values(
        'subdistrict').distinct().count()
    village_count = DigitalBetiUser.objects.filter(state=digital_beti_user.state).values(
        'village').distinct().count()
    top_vles = DigitalBetiUser.objects.filter(
        kind='VLE', state=digital_beti_user.state).annotate(
        num_reg=Count('digitalbetiuser')).order_by('-num_reg')[:3]
    return render(request, 'digitalbeti/logged-in/state/state_dashboard.html',
                  {
                      'state': digital_beti_user.state,
                      'total_registered': user_count,
                      'vle_count': vle_count,
                      'total_exams_given': total_exams_given,
                      'total_passed': total_passed,
                      'total_failed': total_failed,
                      'district_count': district_count,
                      'subdistrict_count': subdistrict_count,
                      'village_count': village_count,
                      'top_vle': top_vles,
                  })


@login_required
def state_top_vle(request):
    digital_beti_user = request.user.digitalbetiuser
    top_vles = DigitalBetiUser.objects.filter(
        kind='VLE', state=digital_beti_user.state).annotate(
        num_reg=Count('digitalbetiuser')).order_by('-num_reg')[:10]
    return render(request, 'digitalbeti/logged-in/state/top_users.html',
                  {'state': digital_beti_user.state, 'vles': top_vles})


@login_required
def state_all_districts(request, state=None):
    if not state:
        digital_beti_user = request.user.digitalbetiuser
    else:
        digital_beti_user = DigitalBetiUser.objects.filter(state=state).first()
    districts = DigitalBetiUser.objects.filter(
        kind='VLE', state=digital_beti_user.state, district__isnull=False).values('district').annotate(
        num_user=Count('district')).order_by('-num_user')
    return render(request, 'digitalbeti/logged-in/state/all_districts.html', {'districts': districts})


@login_required
def admin_overview(request):
    digital_beti_user = request.user.digitalbetiuser
    total_counts = DigitalBetiUser.objects.all().values('kind').annotate(num_user=Count('kind'))
    total_exams_given = AnswerSet.objects.filter(status='COMPLETED').values('participant').distinct().count()
    total_passed = AnswerSet.objects.filter(result='SUCCESS').values('participant').distinct().count()
    total_failed = AnswerSet.objects.filter(result='FAILED').values('participant').distinct().count()
    state_count = DigitalBetiUser.objects.all().values('state').distinct().count()
    district_count = DigitalBetiUser.objects.all().values('district').distinct().count()
    subdistrict_count = DigitalBetiUser.objects.all().values('subdistrict').distinct().count()
    village_count = DigitalBetiUser.objects.all().values('village').distinct().count()
    top_vles = DigitalBetiUser.objects.filter(kind='VLE').annotate(
        num_reg=Count('digitalbetiuser')).order_by('-num_reg')[:3]
    top_states = DigitalBetiUser.objects.filter(kind='VLE').values('state').annotate(
        num_reg=Count('state')).order_by('-num_reg')[:3]
    return render(request, 'digitalbeti/logged-in/admin/admin_dashboard.html',
                  {
                      'total_counts': total_counts,
                      'total_exams_given': total_exams_given,
                      'total_passed': total_passed,
                      'total_failed': total_failed,
                      'district_count': district_count,
                      'subdistrict_count': subdistrict_count,
                      'village_count': village_count,
                      'top_vle': top_vles,
                      'top_state': top_states,
                      'state_count': state_count,
                  })


@login_required
def admin_all_states(request):
    states = DigitalBetiUser.objects.filter(
        kind='VLE').values('state').annotate(
        num_user=Count('state')).order_by('-num_user')
    return render(request, 'digitalbeti/logged-in/admin/all_states.html', {'states': states})


def create_vle(email, mobile, csc_id, name, state):
    if not email:
        return False, 'No email'
    if not csc_id:
        return False, 'No CSC ID'
    if not name:
        return False, 'Invalid Name'
    if not state:
        return False, 'Invalid State'
    if User.objects.filter(email=email):
        return False, 'Email Already Used'
    if User.objects.filter(username=csc_id):
        return False, 'CSC ID Already Used'
    user = User.objects.create_user(csc_id, email, '12345')
    user.first_name = name.split(' ')[0]
    user.last_name = ' '.join(name.split(' ')[1:])
    user.save()
    dbu = DigitalBetiUser()
    dbu.kind = 'VLE'
    dbu.user = user
    dbu.prr = True
    dbu.uk = csc_id
    dbu.state = state.upper()
    dbu.save()
    return True


def coming_soon(request, ref_hash=None):
    return render(request, 'digitalbeti/logged-in/coming_soon.html')
