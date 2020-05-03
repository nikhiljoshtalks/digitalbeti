from django.contrib.auth import admin
from django.urls import path, re_path

from . import views

urlpatterns = [
    re_path(r'^$', views.index, name='index'),
    path('impact', views.impact, name='impact'),
    path('state', views.state, name='state'),
    path('about-fb', views.about_facebook, name='about-fb'),
    path('about', views.about_project, name='about-project'),
    path('about-csc', views.about_csc, name='about-csc'),
    path('jobs', views.jobs, name='jobs'),
    path('digital-marketing', views.digital_marketing, name='digital-marketing'),
    path('online-safety', views.online_safety, name='online-safety'),

    # AUTH
    path('login', views.user_login, name='login'),
    path('logout', views.user_logout, name='logout'),
    path('signup', views.user_signup, name='signup'),
    path('reset', views.reset_password, name='reset_password'),

    # VILLAGE DETAILS API
    path('api/vd/districts', views.get_districts_for_state, name='get_district'),
    path('api/vd/cities', views.get_subdistrict_for_state_and_district, name='get_subdistrict'),
    path('api/vd/villages', views.get_village_for_state_and_district_village, name='get_village'),

    # LOGGED IN
    path('dashboard', views.user_dashboard, name='user_dashboard'),
    path('user/curriculum', views.curriculum, name='curriculum'),
    path('user/not-registered', views.not_registerd, name='not_registered'),
    path('user/fill-details', views.beneficiary_details_input, name='fill_details'),
    path('user/exams', views.user_exam, name='exams'),
    # path('user/download-certificate/<str:ref_hash>',
    #      views.CertificateView.as_view(), name='download_certificate'),
    path('user/download-certificate/<str:ref_hash>',
         views.coming_soon, name='coming_soon'),

    # VLE
    path('vle/overview/<int:user_id>', views.vle_overview, name='vle_overview'),
    path('vle/not-registered', views.vle_not_registerd, name='vle_not_registered'),
    path('vle/fill-details', views.vle_details_input, name='vle_details_input'),
    path('vle/reg_user', views.vle_register_user, name='reg_user'),
    path('vle/reg_user_prompt', views.vle_register_user_prompt, name='reg_user_prompt'),
    path('vle/reg_history', views.vle_reg_history, name='reg_history'),
    path('vle/conduct_exams/<str:ref_hash>', views.conduct_exams, name='conduct_exams'),
    path('vle/completed/<str:ref_hash>', views.completed_exam, name='completed_exam'),
    path('vle/history', views.vle_exams_history, name='history'),
    path('vle/competition', views.vle_competition, name='competition'),
    path('vle/competition_input', views.vle_competition_input, name='vle_competition_input'),
    path('vle/assets', views.vle_assets, name='assets'),
    path('vle/exams', views.vle_user_exam, name='vle_user_exam'),

    path('dmdc/overview/<str:district>', views.dmdc_overview, name='dmdc_overview'),
    path('dmdc/select-district', views.dmdc_district_input, name='dmdc_district_input'),
    path('dmdc/vles/<str:district>', views.dmdc_all_vle, name='dmdc_all_vle_list'),
    path('dmdc/vles', views.dmdc_all_vle, name='dmdc_all_vle'),
    path('dmdc/top-vles', views.dmdc_top_vle, name='dmdc_top_vle'),

    path('state/overview/<str:state>', views.state_overview, name='state_overview'),
    path('state/districts/<str:state>', views.state_all_districts, name='state_all_districts_list'),
    path('state/districts', views.state_all_districts, name='state_all_districts'),
    path('state/top-vles', views.state_top_vle, name='state_top_vle'),

    path('su/states', views.admin_all_states, name='admin_all_states'),
    path('su/create-user', views.admin_create_user, name='admin_create_user'),
    path('su/create-user-bulk', views.admin_create_user_bulk, name='admin_create_bulk'),
]
