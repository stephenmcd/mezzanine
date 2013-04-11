
from django.contrib import admin

from mezzanine.accounts.models import get_profile_model
from mezzanine.core.admin import SitePermissionUserAdmin
from mezzanine.conf import settings
from mezzanine.utils.email import send_approved_mail
from mezzanine.utils.models import get_user_model


Profile = get_profile_model()
User = get_user_model()


class ProfileInline(admin.StackedInline):
    model = Profile
    can_delete = False
    template = "admin/profile_inline.html"
    extra = 0


user_list_display = SitePermissionUserAdmin.list_display
user_list_display += ("is_active", "date_joined", "last_login")


class UserProfileAdmin(SitePermissionUserAdmin):

    list_display = user_list_display

    def save_model(self, request, obj, form, change):
        """
        If the ``ACCOUNTS_APPROVAL_REQUIRED`` setting is ``True``,
        send a notification email to the user being saved if their
        ``active`` status has changed to ``True``.
        """
        if change and settings.ACCOUNTS_APPROVAL_REQUIRED:
            if obj.is_active and not User.objects.get(id=obj.id).is_active:
                send_approved_mail(request, obj)
        super(UserProfileAdmin, self).save_model(request, obj, form, change)


if Profile:
    UserProfileAdmin.inlines += (ProfileInline,)


admin.site.unregister(User)
admin.site.register(User, UserProfileAdmin)
