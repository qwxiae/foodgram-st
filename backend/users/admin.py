from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from .models import User


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ("username",
                    "email",
                    "first_name",
                    "last_name",
                    "is_active"
                    )
    search_fields = ("username", "email")
    list_filter = ("first_name", "last_name")
    ordering = ("username",)
    empty_value_display = _("[пусто]")

    readonly_fields = ("last_login", "date_joined")
