from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .forms import CommonUserCreationForm, CommonUserChangeForm
from .models import CommonUser

class CommonUserAdmin(UserAdmin):
    add_form = CommonUserCreationForm
    form = CommonUserChangeForm
    model = CommonUser
    fieldsets = (UserAdmin.fieldsets or ()) + (
                (None, {'fields': ('scan_directory',)}),
        )
    list_display = [
        "email",
        "username",
        "is_staff",
        "is_active",
        "scan_directory",
        "last_login",
    ]


admin.site.register(CommonUser, CommonUserAdmin)
