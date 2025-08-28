from django import forms

class SignupForm(forms.Form):
    name = forms.CharField(max_length=150, widget=forms.TextInput(attrs={'placeholder': 'Enter your full name'}))
    email = forms.EmailField(widget=forms.EmailInput(attrs={'placeholder': 'example@mail.com'}))
    password = forms.CharField(min_length=6, widget=forms.PasswordInput(attrs={'placeholder': 'Create a strong password'}))
    age_confirm = forms.BooleanField(required=True, label='I confirm I am 18 or older')

class LoginForm(forms.Form):
    email = forms.EmailField(widget=forms.EmailInput(attrs={'placeholder': 'Email address'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'placeholder': 'Password'}))
