from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django.contrib.auth import password_validation
from .models import User

class CustomUserCreationForm(UserCreationForm):
    # Use standard Django field names 'password1' and 'password2'
    password1 = forms.CharField(
        label="Password",
        widget=forms.PasswordInput,
        help_text=password_validation.password_validators_help_text_html(),
    )
    password2 = forms.CharField(
        label="Password confirmation",
        widget=forms.PasswordInput,
        help_text="Enter the same password as before, for verification.",
    )

    class Meta:
        model = User
        fields = ('email', 'first_name', 'last_name', 'mobile', 'branch')

    def save(self, commit=True):
        # We can just call super().save() because now we use the standard field names
        # UserCreationForm.save() handles the password setting for 'password1' automatically
        return super().save(commit=commit)

class CustomUserChangeForm(UserChangeForm):
    class Meta:
        model = User
        fields = ('email', 'first_name', 'last_name', 'mobile', 'branch', 'is_active', 'is_staff', 'is_superuser')
