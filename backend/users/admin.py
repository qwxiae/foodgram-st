from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from .models import User

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ("username", "email", "first_name", "last_name", "is_active")
    search_fields = ("username", "email")
    list_filter = ("first_name", "last_name")
    ordering = ("username",)
    empty_value_display = _("[пусто]")

    fieldsets = (
        (None, {
            "fields": ("username", "email", "password")
        }),
        (_("Personal info"), {
            "fields": ("first_name", "last_name", "avatar")
        }),
        (_("Permissions"), {
            "fields": ("is_active", "is_staff", "is_superuser", "groups", "user_permissions")
        }),
        (_("Important dates"), {
            "fields": ("last_login", "date_joined")
        }),
    )

    readonly_fields = ("last_login", "date_joined")
