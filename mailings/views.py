import os

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied
from django.core.mail import send_mail
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from django.views.generic import DetailView, ListView
from django.views.generic.edit import CreateView, DeleteView, UpdateView

from mailings.forms import MailingForm, MailingRecipientForm, MessageForm
from mailings.models import Mailing, Mailing_attempt, Mailing_recipient, Message
from mailings.services import can_manage_own, can_view_all, is_user_manager


def send_mailing_view(request, mailing_id):
    mailing = get_object_or_404(Mailing, id=mailing_id)
    send_mailing(mailing)
    messages.success(request, "Рассылка отправлена. Проверьте попытки отправки.")
    return redirect("mailings:mailing_list")


def send_mailing(mailing):
    """
    Отправляет письмо всем получателям рассылки mailing,
    создает записи Mailing_attempt с результатом.
    """
    if not mailing.message:
        return  # Без сообщения рассылка не имеет смысла

    recipients = mailing.recipients.all()
    subject = mailing.message.subject_of_the_letter
    body = mailing.message.body_of_the_letter
    from_email = os.getenv("EMAIL_HOST_USER")

    for recipient in recipients:
        try:
            send_mail(
                subject=subject,
                message=body,
                from_email=from_email,
                recipient_list=[recipient.email],
                fail_silently=False,
            )
            Mailing_attempt.objects.create(
                mailing=mailing,
                status="Успешно",
                server_response="Отправлено успешно",
            )
        except Exception as e:
            Mailing_attempt.objects.create(
                mailing=mailing,
                status="Не успешно",
                server_response=str(e),
            )


@login_required
def main_view(request):
    """Главная страница со статистикой рассылок и списком рассылок."""
    user = request.user

    # Проверка на наличие данных в БД
    if not Mailing.objects.exists():
        return render(request, 'empty_db.html')

    # Проверки прав доступа
    if is_user_manager(user):
        # Менеджер: видит все рассылки в списке, но статистика только своя
        queryset = Mailing.objects.all()  # Все рассылки для списка
    elif not can_view_all(user):
        # Обычный пользователь: видит только свои рассылки в списке и статистику
        queryset = Mailing.objects.filter(owner=user)
    else:
        raise PermissionDenied("Недостаточно прав для просмотра.")

    # Статистика: всегда только для рассылок текущего пользователя (персональная)
    user_mailings = Mailing.objects.filter(owner=user)

    # Подсчёты
    total_mailings = user_mailings.count()
    active_mailings = user_mailings.filter(
        status=Mailing.STATUS_RUNNING
    ).count()  # Активные — статус "Запущена"

    # Уникальные получатели: через ManyToMany
    unique_recipients = (
        user_mailings.values_list("recipients", flat=True).distinct().count()
    )

    context = {
        "total_mailings": total_mailings,
        "active_mailings": active_mailings,
        "unique_recipients": unique_recipients,
        "mailings": queryset,  # Список рассылок для отображения (все для менеджеров, свои для обычных)
        "is_manager": (
            request.user.groups.filter(name="Менеджер").exists()
            if request.user.is_authenticated
            else False
        ),
    }

    return render(request, "mailing_statistics.html", context)


@login_required
def mailing_statistics_view(request):
    user = request.user

    # Всего рассылок пользователя
    total_mailings = Mailing.objects.filter(owner=user).count()

    # Активных рассылок (статус "Запущена")
    active_mailings = Mailing.objects.filter(owner=user, status="Запущена").count()

    # Уникальных получателей: все получатели пользователя (уникальны по email)
    unique_recipients = Mailing_recipient.objects.filter(owner=user).count()

    # Успешных попыток рассылок
    successful_attempts = Mailing_attempt.objects.filter(
        mailing__owner=user, status="Успешно"
    ).count()

    # Неуспешных попыток рассылок
    unsuccessful_attempts = Mailing_attempt.objects.filter(
        mailing__owner=user, status="Не успешно"
    ).count()

    # Отправленных сообщений: приравниваем к успешным попыткам
    sent_messages = successful_attempts

    context = {
        "total_mailings": total_mailings,
        "active_mailings": active_mailings,
        "unique_recipients": unique_recipients,
        "successful_attempts": successful_attempts,
        "unsuccessful_attempts": unsuccessful_attempts,
        "sent_messages": sent_messages,
    }

    return render(request, "personal_mailing_statistics.html", context)


@method_decorator(cache_page(60 * 15), name="dispatch")
class MessageCreateView(CreateView):
    model = Message
    # fields = "__all__"
    form_class = MessageForm
    template_name = "message_form.html"
    success_url = reverse_lazy("mailings:message_list")

    def form_valid(self, form):
        form.instance.owner = self.request.user
        return super().form_valid(form)


@method_decorator(cache_page(60 * 15), name="dispatch")
class MessageDetailView(DetailView):
    model = Message
    template_name = "message_detail.html"
    context_object_name = "message"


@method_decorator(cache_page(60 * 15), name="dispatch")
class MessageUpdateView(UpdateView):
    model = Message
    fields = "__all__"
    # form_class = ProductForm
    template_name = "message_form.html"
    success_url = reverse_lazy("mailings:message_list")
    # permission_required = 'catalog.change_product'


@method_decorator(cache_page(60 * 15), name="dispatch")
class MessageListView(ListView):
    model = Message
    template_name = "message_list.html"
    context_object_name = "message"

    def dispatch(self, request, *args, **kwargs):
        # Проверка доступа: если пользователь - менеджер, запрещаем доступ
        if is_user_manager(request.user):
            raise PermissionDenied("У вас нет доступа к этому разделу.")  # 403 ошибка
        return super().dispatch(request, *args, **kwargs)

    def get_queryset(self):
        # Для обычных пользователей: фильтруем по владельцу
        return Message.objects.filter(owner=self.request.user)


@method_decorator(cache_page(60 * 15), name="dispatch")
class MessageDeleteView(DeleteView):
    model = Message
    template_name = "message_confirm_delete.html"
    success_url = reverse_lazy("mailings:message_list")


@method_decorator(cache_page(60 * 15), name="dispatch")
class MailingCreateView(LoginRequiredMixin, CreateView):
    model = Mailing
    form_class = MailingForm
    template_name = "mailing_form.html"
    success_url = reverse_lazy("mailings:main")

    def dispatch(self, request, *args, **kwargs):
        # Менеджер не может создавать рассылки
        if is_user_manager(request.user):
            raise PermissionDenied("Менеджеры не могут создавать рассылки.")
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        form.instance.owner = self.request.user
        return super().form_valid(form)


@method_decorator(cache_page(60 * 15), name="dispatch")
class MailingDetailView(LoginRequiredMixin, DetailView):
    model = Mailing
    template_name = "mailing_detail.html"
    context_object_name = "mailing"

    def get_object(self, queryset=None):
        obj = super().get_object(queryset)
        # Менеджер видит всё, владелец — свой
        if not (
            is_user_manager(self.request.user) or can_manage_own(self.request.user, obj)
        ):
            raise PermissionDenied("У вас нет доступа к этому объекту.")
        return obj


@method_decorator(cache_page(60 * 15), name="dispatch")
class MailingUpdateView(LoginRequiredMixin, UpdateView):
    model = Mailing
    form_class = MailingForm
    template_name = "mailing_form.html"
    success_url = reverse_lazy("mailings:main")

    def get_object(self, queryset=None):
        obj = super().get_object(queryset)
        # Только владелец может редактировать (менеджер — нет)
        if not can_manage_own(self.request.user, obj):
            raise PermissionDenied("Вы можете редактировать только свои рассылки.")
        return obj


@method_decorator(cache_page(60 * 15), name="dispatch")
class MailingListView(LoginRequiredMixin, ListView):
    model = Mailing
    template_name = "mailing_list.html"
    context_object_name = "mailings"

    def get_queryset(self):
        queryset = super().get_queryset()
        # Если не менеджер, фильтруем по owner
        if not can_view_all(self.request.user):
            queryset = queryset.filter(owner=self.request.user)
        return queryset


@method_decorator(cache_page(60 * 15), name="dispatch")
class MailingDeleteView(LoginRequiredMixin, DeleteView):
    model = Mailing
    template_name = "mailing_confirm_delete.html"
    success_url = reverse_lazy("mailings:main")

    def get_object(self, queryset=None):
        obj = super().get_object(queryset)
        # Только владелец может удалять (менеджер — нет)
        if not can_manage_own(self.request.user, obj):
            raise PermissionDenied("Вы можете удалять только свои рассылки.")
        return obj


@method_decorator(cache_page(60 * 15), name="dispatch")
class Mailing_recipientCreateView(LoginRequiredMixin, CreateView):
    model = Mailing_recipient
    form_class = MailingRecipientForm
    template_name = "recipient_form.html"
    success_url = reverse_lazy("mailings:main")

    def dispatch(self, request, *args, **kwargs):
        # Менеджер не может создавать получателей
        if is_user_manager(request.user):
            raise PermissionDenied("Менеджеры не могут создавать получателей.")
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        form.instance.owner = self.request.user
        return super().form_valid(form)


@method_decorator(cache_page(60 * 15), name="dispatch")
class Mailing_recipientDetailView(LoginRequiredMixin, DetailView):
    model = Mailing_recipient
    template_name = "recipient_detail.html"
    context_object_name = "recipient"

    def get_object(self, queryset=None):
        obj = super().get_object(queryset)
        # Менеджер видит всё, владелец — свой
        if not (
            is_user_manager(self.request.user) or can_manage_own(self.request.user, obj)
        ):
            raise PermissionDenied("У вас нет доступа к этому объекту.")
        return obj


@method_decorator(cache_page(60 * 15), name="dispatch")
class Mailing_recipientUpdateView(LoginRequiredMixin, UpdateView):
    model = Mailing_recipient
    form_class = MailingRecipientForm
    template_name = "recipient_form.html"
    success_url = reverse_lazy("mailings:main")

    def get_object(self, queryset=None):
        obj = super().get_object(queryset)
        # Только владелец может редактировать (менеджер — нет)
        if not can_manage_own(self.request.user, obj):
            raise PermissionDenied("Вы можете редактировать только своих получателей.")
        return obj


@method_decorator(cache_page(60 * 15), name="dispatch")
class Mailing_recipientListView(LoginRequiredMixin, ListView):
    model = Mailing_recipient
    template_name = "recipient_list.html"
    context_object_name = "recipients"

    def get_queryset(self):
        queryset = super().get_queryset()
        # Если не менеджер, фильтруем по owner
        if not can_view_all(self.request.user):
            queryset = queryset.filter(owner=self.request.user)
        return queryset


@method_decorator(cache_page(60 * 15), name="dispatch")
class Mailing_recipientDeleteView(LoginRequiredMixin, DeleteView):
    model = Mailing_recipient
    template_name = "recipient_confirm_delete.html"
    success_url = reverse_lazy("mailings:main")

    def get_object(self, queryset=None):
        obj = super().get_object(queryset)
        # Только владелец может удалять (менеджер — нет)
        if not can_manage_own(self.request.user, obj):
            raise PermissionDenied("Вы можете удалять только своих получателей.")
        return obj
