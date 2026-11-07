from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User


# Register your models here.

@admin.register(User)
class UserAdmin(BaseUserAdmin):
    model = User

    list_display = (
        "id",
        "username",
        "email",
        "is_staff",
        "is_active",
    )

    list_filter = ("is_staff", "is_active")

    search_fields = ("username", "email")
    ordering = ("id",)

    fieldsets = (
        (None, {"fields": ("username", "password")}),
        ("Personal info", {"fields": ("email",)}),
        (
            "Permissions",
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                )
            },
        ),
        ("Important dates", {"fields": ("last_login", "date_joined")}),
    )

    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": (
                    "username",
                    "email",
                    "password1",
                    "password2",
                ),
            },
        ),
    )

    readonly_fields = ("last_login", "date_joined")
