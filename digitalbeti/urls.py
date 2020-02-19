from django.contrib.auth import admin
from django.urls import path, re_path

from . import views

urlpatterns = [
    re_path(r'^$', views.index, name='index'),
    path('impact', views.impact, name='impact'),
    path('about-fb', views.about_facebook, name='about-fb'),
    path('about', views.about_project, name='about-project'),
    path('about-csc', views.about_csc, name='about-csc'),
    path('jobs', views.jobs, name='jobs'),
    path('digital-marketing', views.digital_marketing, name='digital-marketing'),
    path('online-safety', views.online_safety, name='online-safety'),

    # AUTH
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),
    path('signup/', views.user_signup, name='signup'),

    # VILLAGE DETAILS API
    path('api/vd/districts', views.get_districts_for_state, name='get_district'),
    path('api/vd/cities', views.get_subdistrict_for_state_and_district, name='get_subdistrict'),
    path('api/vd/villages', views.get_village_for_state_and_district_village, name='get_village'),

    # LOGGED IN
    path('dashboard', views.user_dashboard, name='user_dashboard'),
    path('curriculum', views.curriculum, name='curriculum'),
    path('not-registered', views.not_registerd, name='not_registered'),
    path('fill-details', views.beneficiary_details_input, name='fill_details'),
    path('profile', views.user_profile, name='profile'),
    path('exams', views.user_exam, name='exams'),
    path('download-certificate/<str:ref_hash>',
         views.CertificateView.as_view(), name='download_certificate'),

    # VLE
    path('vle/not-registered', views.vle_not_registerd, name='vle_not_registered'),
    path('vle/fill-details', views.vle_details_input, name='vle_details_input'),
    path('vle/reg_user', views.vle_register_user, name='reg_user'),
    path('vle/reg_user_prompt', views.vle_register_user_prompt, name='reg_user_prompt'),
    path('vle/reg_history', views.vle_reg_history, name='reg_history'),
    path('vle/conduct_exams/<str:ref_hash>', views.conduct_exams, name='conduct_exams'),
    path('vle/completed/<str:ref_hash>', views.completed_exam, name='completed_exam'),
    path('vle/history', views.vle_exams_history, name='history'),
    path('vle/competition', views.vle_competition, name='competition'),
    path('vle/assets', views.vle_assets, name='assets'),
    path('vle/dashboard', views.vle_dashboard, name='vle_dashboard'),
    path('vle/exams', views.vle_user_exam, name='vle_user_exam'),

    path('dmdc/vle_details/<int:user_id>', views.dmdc_vle_details, name='dmdc_vle_details'),
    path('state/vle_details/<int:user_id>', views.state_vle_details, name='state_vle_details'),



]
