#from django import forms
from django import forms
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from usersApp.models import User, UsersKind, ClientUserInterface, LawyerUserInterface


# Данный класс переопределяется, если мы хотим переопределить форму для создания юзера. В данном случае в юзер модели мы
# прямо указываем, что применяем эту форму
class UserCreationForm(forms.ModelForm):
    # kind_of_user = forms.models.ForeignKey(UsersKind, blank=True, null=True, on_delete=models.PROTECT, )
    
    password1 = forms.CharField(label='Password', widget=forms.PasswordInput)
    password2 = forms.CharField(label='Password confirmation', widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = '__all__'

    def clean_password2(self):
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Passwords don't match")
        return password2

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
        return user

class CustomUserAdmin(UserAdmin):
    add_form = UserCreationForm
    list_display = ('id', 'username', 'kind_of_user')
    list_display_links = ('username', 'kind_of_user')
    fieldsets = (
        *UserAdmin.fieldsets,
        (
            'Custom Field Heading',# визуализируется в качестве логического раздела формы
            {
                'fields':(
                    'kind_of_user',
                ),
            }, 
        ),
        
    )
    #add_form = UserCreationForm

class ClientUserInterfaceAdmin(admin.ModelAdmin):
    list_display = ('user_name', 'full_name',)

admin.site.register(User, CustomUserAdmin)
admin.site.register(UsersKind)
admin.site.register(ClientUserInterface, ClientUserInterfaceAdmin)

# Register your models here.
