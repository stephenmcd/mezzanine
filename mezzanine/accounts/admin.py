from django.contrib import admin

from mezzanine.accounts.models import get_profile_model
from mezzanine.utils.models import get_user_model
from mezzanine.core.admin import SitePermissionUserAdmin


Profile = get_profile_model()
User = get_user_model()


class ProfileInline(admin.StackedInline):
    model = Profile
    can_delete = False
    template = "admin/profile_inline.html"
    extra = 0


class UserProfileAdmin(SitePermissionUserAdmin):
    pass

if Profile:
    UserProfileAdmin.inlines += (ProfileInline,)


admin.site.unregister(User)
admin.site.register(User, UserProfileAdmin)
