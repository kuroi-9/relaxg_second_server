from django.contrib.auth.forms import AdminUserCreationForm, UserChangeForm
from rg_server.models import CommonUser
from django import forms

class CommonUserCreationForm(AdminUserCreationForm):
    """
    Form called when creating a new user on the admin page.
    """

    class Meta(AdminUserCreationForm.Meta):
        model = CommonUser

    def clean_username(self):
            username = self.cleaned_data['username']
            if CommonUser._default_manager.get(username=username) == None:
                return username
            else:
                raise forms.ValidationError(self.error_messages['duplicate_username'])

class CommonUserChangeForm(UserChangeForm):
    """
    Form called when editing a user on the admin page.
    """

    class Meta(UserChangeForm.Meta):
        model = CommonUser
