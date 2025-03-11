from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm

tailwindcss_classes_register_form = 'mt-1 block w-full px-4 py-2 bg-gray-700 border border-gray-600 rounded-lg shadow-sm text-white focus:outline-none focus:ring-2 focus:ring-blue-500 placeholder-gray-400'

class CustomUserCreationForm(UserCreationForm):
    fullname = forms.CharField(
        max_length=100, required=True, label='Full Name',
        widget=forms.TextInput(attrs={
            'class': tailwindcss_classes_register_form,
            'placeholder': 'Your Full Name'
        })
    )
    
    class Meta:
        model = User
        fields = ['username', 'fullname', 'email', 'password1', 'password2']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['username'].widget.attrs.update({
            'class': tailwindcss_classes_register_form,
            'placeholder': 'Username',
            'autofocus': True
        })
        self.fields['username'].label = 'User Name'

        self.fields['email'].widget.attrs.update({
            'class': tailwindcss_classes_register_form,
            'placeholder': 'Email Address'
        })
        self.fields['email'].label = 'Email Address'

        self.fields['password1'].widget.attrs.update({
            'class': tailwindcss_classes_register_form,
            'placeholder': 'Password'
        })
        self.fields['password1'].label = 'Password'

        self.fields['password2'].widget.attrs.update({
            'class': tailwindcss_classes_register_form,
            'placeholder': 'Confirm Password'
        })
        self.fields['password2'].label = 'Password (again)'

    
    def save(self, commit=True):
        user = super().save(commit=False)
        fullname = self.cleaned_data.get('fullname').strip()
        name_parts = fullname.split()

        # Split the full name into first and last name
        if len(name_parts) == 1:
            user.first_name = name_parts[0]
            user.last_name = ""
        elif len(name_parts) == 2:
            user.first_name = name_parts[0]
            user.last_name = name_parts[1]
        else:
            user.first_name = " ".join(name_parts[:-1])
            user.last_name = name_parts[-1]

        if commit:
            user.save()
        return user