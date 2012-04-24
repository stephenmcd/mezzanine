
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User

from mezzanine.accounts.models import get_profile_model


Profile = get_profile_model()


class ProfileInline(admin.StackedInline):
    model = Profile
    can_delete = False
    template = "admin/profile_inline.html"
    extra = 0


class UserProfileAdmin(UserAdmin):
    inlines = (ProfileInline,) if Profile else ()


admin.site.unregister(User)
admin.site.register(User, UserProfileAdmin)
