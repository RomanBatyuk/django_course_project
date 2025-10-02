from django.contrib import admin

from mailings.models import Mailing, Mailing_attempt, Mailing_recipient, Message


@admin.register(Mailing_recipient)
class MailingRecipientAdmin(admin.ModelAdmin):
    """Админка для модели Mailing_recipient."""

    list_display = ("id", "email", "full_name", "comment")
    search_fields = ("email", "full_name")
    list_filter = ("email", "full_name")


@admin.register(Mailing)
class MailingAdmin(admin.ModelAdmin):
    """Админка для модели Mailing."""

    list_display = ("id", "start_message", "end_message", "status", "message")
    search_fields = ("status", "start_message", "end_message")
    list_filter = ("status", "start_message", "end_message")
    ordering = ("-start_message",)
    date_hierarchy = "start_message"
    fieldsets = ((None, {"fields": ("status", "message", "recipients")}),)
    readonly_fields = ("start_message", "end_message")
    list_select_related = ("message",)
    filter_horizontal = ("recipients",)  # Для удобства выбора получателей


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    """Админка для модели Message."""

    list_display = ("id", "subject_of_the_letter", "body_of_the_letter")
    search_fields = ("subject_of_the_letter", "body_of_the_letter")
    list_filter = ("subject_of_the_letter",)


@admin.register(Mailing_attempt)
class MailingAttemptAdmin(admin.ModelAdmin):
    """Админка для модели Mailing_attempt."""

    # Поля для отображения в списке (убрал 'status', так как его нет в модели)
    list_display = ("id", "mailing", "data_attempt", "server_response")

    # Поля для поиска (убрал 'status')
    search_fields = ("server_response",)

    # Сортировка по умолчанию
    ordering = ("-data_attempt",)

    # Фильтры (убрал 'status')
    list_filter = ("data_attempt",)

    # Иерархия по датам
    date_hierarchy = "data_attempt"

    # Группы полей для редактирования (убрал 'status')
    fieldsets = ((None, {"fields": ("mailing", "server_response")}),)

    # Поля только для чтения
    readonly_fields = ("data_attempt",)

    # Оптимизация запросов для связанных моделей
    list_select_related = ("mailing",)
