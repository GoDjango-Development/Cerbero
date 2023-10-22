from django import forms
from django.contrib.auth.models import User, Group
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model
from config.models import Profile

class EditProfileForm(forms.ModelForm):
    first_name = forms.CharField(
        widget=forms.TextInput(attrs={
            'class':'shadow-sm focus:ring-indigo-500 dark:bg-dark-third dark:text-dark-txt focus:border-indigo-500 block w-full sm:text-sm border-gray-300 rounded-md',
            })
    )
    last_name = forms.CharField(
        widget=forms.TextInput(attrs={
            'class':'shadow-sm focus:ring-indigo-500 dark:bg-dark-third dark:text-dark-txt focus:border-indigo-500 block w-full sm:text-sm border-gray-300 rounded-md',
            })
    )
    picture = forms.ImageField(label='Profile Picture',required=False, widget=forms.FileInput)
    
    class Meta:
        model = Profile
        fields = ('first_name','last_name','picture')

 
class UpdateUser(UserChangeForm):
    class Meta(UserChangeForm.Meta):
        model = User
        fields = ['first_name','last_name',"email", "username", "is_active", "groups",'is_superuser']
        

    



class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(label='Correo electrónico')
    first_name = forms.CharField(label='Nombres')
    last_name = forms.CharField(label='Apellidos')

    class Meta(UserCreationForm.Meta):
        model = User
        fields = UserCreationForm.Meta.fields + ('email', 'first_name', 'last_name')
        
        def clean_first_name(self):
            first_name = self.cleaned_data.get('first_name')
            if not first_name[0].isupper():
                raise ValidationError("El nombre debe comenzar con una letra mayúscula.")
            if not all(ch.isalpha() or ch.isspace() or ch in ['á', 'é', 'í', 'ó', 'ú'] for ch in first_name):
                raise ValidationError("El nombre solo puede contener letras, espacios y tildes.")
            return first_name

        def clean_last_name(self):
            last_name = self.cleaned_data.get('last_name')
            if not last_name[0].isupper():
                raise ValidationError("El apellido debe comenzar con una letra mayúscula.")
            if not all(ch.isalpha() or ch.isspace() or ch in ['á', 'é', 'í', 'ó', 'ú'] for ch in last_name):
                raise ValidationError("El apellido solo puede contener letras, espacios y tildes.")
            return last_name
        
        def clean_username(self):
            username = self.cleaned_data.get('username')
            if User.objects.filter(username=username).exists():
                raise forms.ValidationError("Ya existe un usuario con este nombre de usuario.")
            return username

        #clean email field
        def clean_email(self):
            email = self.cleaned_data.get("email")
            if User.objects.filter(email=email).exists():
                raise forms.ValidationError(F' El correo ya esta registrado , pruebe con otro')
            return email
   
   

 