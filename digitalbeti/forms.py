from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.forms import ModelForm, RadioSelect, TextInput, Textarea, Form
from django.utils.translation import gettext_lazy as _
from digitalbeti.models import BeneficiaryData, Address, VLECompetition, DigitalBetiUser


# Create your models here.

class SignUpForm(UserCreationForm):
    first_name = forms.CharField(label=_('First name'),max_length=30, required=True)
    last_name = forms.CharField(label=_('Last name'),max_length=30, required=True)

    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name','password1', 'password2',)

        help_texts = {
            'username': _('Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.'),
            'password2': _('Enter the same password as before, for verification.'),
        }

class BeneficiaryDataForm(ModelForm):
    class Meta:
        model = BeneficiaryData
        exclude = ['user', 'tc_count', 'facebook_link']
        widgets = {
            'differently_abled': RadioSelect,
            'bank_account': RadioSelect,
            'date_of_birth': TextInput(
                attrs={'type': 'date'}
            )
        }


class VLEDataForm(ModelForm):
    class Meta:
        model = BeneficiaryData
        fields = ['first_name', 'last_name', 'date_of_birth', 'email_id', 'phone_number', 'facebook_link',
                  'personal_monthly_income', 'education_qualification', 'tc_count']
        widgets = {
            'date_of_birth': TextInput(
                attrs={'type': 'date', 'max': '2000-01-01'}
            )
        }


class AddressForm(ModelForm):
    district = forms.CharField(required=True, widget=forms.Select(choices=[]), label=_('District'))
    subdistrict = forms.CharField(required=True, widget=forms.Select(choices=[]), label=_('Subdistrict'))
    village = forms.CharField(required=True, widget=forms.Select(choices=[]), label=_('Village'))

    class Meta:
        model = Address
        exclude = []
        widgets = {
            'text': Textarea(
                attrs={'cols': 40, 'rows': 2}
            )
        }


class VLECompetitionForm(ModelForm):
    class Meta:
        model = VLECompetition
        fields = ['link', 'current_likes']


class UserCreateForm(ModelForm):
    email = forms.EmailField(required=True, label=_('email'))
    first_name = forms.CharField(required=False, label=_('First Name'))
    last_name = forms.CharField(required=False, label=_('Last name'))
    district = forms.CharField(required=False, widget=forms.Select(choices=[]), label=_('District'))
    subdistrict = forms.CharField(required=False, widget=forms.Select(choices=[]), label=_('Subdistrict'))
    village = forms.CharField(required=False, widget=forms.Select(choices=[]), label=_('Village'))
    kind = forms.CharField(required=True, widget=forms.Select(choices=[('USER', 'User'),
                                                                       ('VLE', 'Village Level Entrepreneur'),
                                                                       ('DM/DC', 'DM or DC'),
                                                                       ('STATE', 'State'), ]))

    class Meta:
        model = DigitalBetiUser
        fields = ['kind', 'state', 'district', 'subdistrict', 'village']


class DMDCDistrictInput(ModelForm):
    district = forms.CharField(required=False, widget=forms.Select(choices=[]))

    class Meta:
        model = DigitalBetiUser
        fields = ['state', 'district']


class BulkVLECreation(Form):
    csv_file = forms.FileField()
