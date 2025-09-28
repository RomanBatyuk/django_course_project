from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from users.models import CustomUser  # Импортируйте вашу модель


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    # Поля для отображения в списке пользователей
    list_display = (
        "email",
        "phone_number",
        "country",
        "is_staff",
        "is_active",
        "date_joined",
    )

    # Поля для поиска
    search_fields = ("email", "phone_number")

    # Сортировка по умолчанию
    ordering = ("email",)

    # Настройка fieldset'ов (групп полей) для страницы редактирования пользователя
    # Убираем username из основных полей, так как USERNAME_FIELD = 'email'
    fieldsets = (
        (None, {"fields": ("email", "password")}),  # Основные поля: email как логин
        (
            "Персональная информация",
            {
                "fields": (
                    "first_name",
                    "last_name",
                    "avatar",
                    "phone_number",
                    "country",
                )
            },
        ),
        (
            "Разрешения",
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
        ("Важные даты", {"fields": ("last_login", "date_joined")}),
    )

    # Настройка fieldset'ов для создания нового пользователя
    # Email обязателен, username не нужен
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": (
                    "email",
                    "password1",
                    "password2",
                    "first_name",
                    "last_name",
                    "phone_number",
                    "country",
                    "is_active",
                    "is_staff",
                    "is_superuser",
                ),
            },
        ),
    )
