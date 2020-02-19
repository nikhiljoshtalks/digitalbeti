from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.forms import ModelForm, RadioSelect, TextInput, Textarea
from django.utils.translation import gettext_lazy as _
from digitalbeti.models import BeneficiaryData, Address


# Create your models here.

class SignUpForm(UserCreationForm):
    first_name = forms.CharField(max_length=30, required=True)
    last_name = forms.CharField(max_length=30, required=True)

    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name','password1', 'password2',)


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
    district = forms.CharField(required=True, widget=forms.Select(choices=[]))
    subdistrict = forms.CharField(required=True, widget=forms.Select(choices=[]))
    village = forms.CharField(required=True, widget=forms.Select(choices=[]))

    class Meta:
        model = Address
        exclude = []
        widgets = {
            'text': Textarea(
                attrs={'cols': 40, 'rows': 2}
            )
        }
