import string
from datetime import date

from django.core.handlers.wsgi import WSGIRequest
from django import forms
from django.conf import settings
from django.core.exceptions import ValidationError

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit, Row, Column, Div, Reset, Button
from crispy_forms.bootstrap import PrependedText, PrependedAppendedText, FormActions
from crispy_bootstrap5.bootstrap5 import FloatingField, Field

from .models import User
from . import tools


class SignUpForm(forms.Form):
    first_name = forms.CharField(label='First name',
                                 max_length=64,
                                 min_length=3,
                                 required=True)

    last_name = forms.CharField(label='Last name',
                                max_length=64,
                                min_length=3,
                                required=True)

    birthday = forms.DateField(label='Birthday',
                               required=True,
                               widget=forms.DateInput(attrs={'type': 'date', 'min': '1970-01-01', 'max': date.today()}))

    email = tools.form_fields.EmailField(label='Email address')

    password = tools.form_fields.ValidatePasswordField(label='Password')

    another_password = tools.form_fields.PasswordField(label='Confirm password')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper(self)

        self.helper.form_method = 'post'

        self.helper.layout = Layout(
            FloatingField('first_name', css_class='form-floating mb-3'),
            FloatingField('last_name', css_class='form-floating mb-3'),
            FloatingField('birthday', css_class='form-floating mb-3'),
            FloatingField('email', css_class='form-floating mb-3'),
            FloatingField('password', css_class='form-floating mb-3'),
            FloatingField('another_password', css_class='form-floating mb-3'),
        )
        self.helper.add_input(Submit('submit', 'Sing up', css_class='w-100 mb-2 btn btn-lg rounded-3 btn-primary'))

    def clean_another_password(self):
        if self.data['password'] == self.data['another_password']:
            return self.data['another_password']
        raise ValidationError("Passwords isn't equal")

    def clean_email(self):
        if self.data.get('email'):
            return self.data['email']
        raise ValidationError("This field is required.")

    def save(self):
        if self.is_valid():
            return tools.create_user(self)
        return None


class SingInForm(forms.Form):

    email = forms.EmailField(label='Email address',
                             max_length=30,
                             required=True)

    password = tools.form_fields.PasswordField(label='Password', min_length=2)

    remember_me = forms.BooleanField(label='Remember me',
                                     required=False,
                                     widget=forms.CheckboxInput)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()

        self.helper.form_method = 'post'

        self.helper.layout = Layout(
            FloatingField('email', css_class='form-floating mb-3'),
            FloatingField('password', css_class='form-floating mb-3'),
            Div('remember_me', wrapper_class='checkbox mb-3'),
            Submit('submit', 'Sing In', css_class='w-100 mb-2 btn btn-lg rounded-3 btn-primary')
        )

    def clean_email(self):
        if User.objects.filter(email=self.data['email']).exists():
            return self.data['email']
        raise ValidationError('Email is not exist')


class AddPostForm(forms.Form):
    # TODO: add support of SVG
    photos = forms.ImageField(label="",
                              required=True,
                              widget=forms.FileInput(attrs={'multiple': True}))

    tags = forms.CharField(label="#Tags",
                           required=False,
                           widget=forms.Textarea,
                           help_text='tags are listed through #')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._request = None

        self.helper = FormHelper()

        self.helper.form_method = 'post'

        self.helper.layout = Layout(
            Field('photos', wrapper_class='form-floating mb-3'),
            FloatingField('tags', css_class='form-floating mb-3'),
            Submit('submit', 'Publish', css_class='w-100 mb-2 btn btn-lg rounded-3 btn-primary'),
            Reset('reset', 'Cancel', css_class='w-100 btn btn-lg btn-outline-secondary'),
        )

    @property
    def request(self):
        if self._request:
            return self._request
        raise ValueError('Attribute <request> not set')

    @request.setter
    def request(self, value):
        if not isinstance(value, WSGIRequest):
            raise TypeError('Invalid type, request must be <django.core.handlers.wsgi.WSGIRequest>')
        self._request = value

    def save(self):
        if self.is_valid():
            user = User.objects.get(username=self.request.user)
            return tools.add_new_post(user, self.files.getlist('photos'), self.cleaned_data['tags'])
        return None


class ConfirmEmailForm(forms.Form):
    code = forms.CharField(min_length=settings.LENGTH_OF_CODE_CONFIRM,
                           max_length=settings.LENGTH_OF_CODE_CONFIRM,
                           required=True,
                           label='Code confirm')

    delete_account = forms.BooleanField(label='Delete account',
                                        required=False,
                                        widget=forms.CheckboxInput)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self._code_compare = ''

        self.helper = FormHelper()

        self.helper.form_method = 'post'
        self.helper.layout = Layout(
            FloatingField('code', css_class='form-floating mb-3'),
            Div('delete_account', wrapper_class='checkbox mb-3'),
        )

        self.helper.add_input(Submit('confirm', 'Confirm', css_class='w-100 mb-2 btn btn-lg rounded-3 btn-primary'))

    @property
    def code_compare(self):
        if self._code_compare:
            return self._code_compare
        raise ValueError('Attribute <code_compare> not set')

    @code_compare.setter
    def code_compare(self, value):
        if not isinstance(value, str):
            raise TypeError('Invalid type, request must be <str>')
        self._code_compare = value

    def clean_code(self):
        if self.data.get('code') == self.code_compare:
            return self.data['code']
        raise ValidationError("Code confirm invalid")


class CommentsForm(forms.Form):
    comment = forms.CharField(label="Comment",
                              required=True,
                              max_length=400,
                              widget=forms.Textarea)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()

        self.helper.form_method = 'post'

        self.helper.layout = Layout(
            FloatingField('comment', css_class='form-floating mb-3'),
            Submit('submit', 'Publish', css_class='w-100 mb-2 btn btn-lg rounded-3 btn-primary'),
            Reset('delete', 'Clear', css_class='w-100 btn btn-lg btn-outline-secondary'),
        )
