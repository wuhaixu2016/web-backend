from django import forms

# Create your models here.
class NameForm(forms.Form):
    username = forms.CharField(label='username',max_length = 100)
    password = forms.CharField(label='password',widget = forms.PasswordInput())