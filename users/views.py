from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from django.views.generic import DetailView, ListView
from django.views.generic.edit import CreateView, UpdateView
from django.views import View
from users.models import CustomUser
from mailings.services import is_user_manager
from django.core.exceptions import PermissionDenied
from django.contrib import messages
from django.shortcuts import redirect


from users.forms import CustomUserCreationForm, ProfileUpdateForm

User = get_user_model()


class RegisterView(CreateView):
    template_name = "register.html"
    form_class = CustomUserCreationForm
    success_url = reverse_lazy("mailings:main")


@method_decorator(cache_page(60 * 15), name="dispatch")
class ProfileDetailView(LoginRequiredMixin, DetailView):
    model = User
    template_name = "profile_detail.html"
    context_object_name = "profile_user"

    def get_object(self, queryset=None):
        # Показывает текущего пользователя
        return self.request.user


@method_decorator(cache_page(60 * 15), name="dispatch")
class ProfileUpdateView(LoginRequiredMixin, UpdateView):
    model = User
    form_class = ProfileUpdateForm
    template_name = "profile_edit.html"
    success_url = reverse_lazy("users:profile_detail")

    def get_object(self, queryset=None):
        # Редактирует текущего пользователя
        return self.request.user


# 1. Просмотр списка пользователей (только для менеджеров)
class UserListView(LoginRequiredMixin, ListView):
    model = CustomUser
    template_name = "user_list.html"
    context_object_name = "users"
    paginate_by = 10

    def dispatch(self, request, *args, **kwargs):
        if not is_user_manager(request.user):
            raise PermissionDenied("Доступ только для менеджеров.")
        return super().dispatch(request, *args, **kwargs)

    def get_queryset(self):
        # Показываем всех пользователей, кроме самого менеджера (опционально)
        return User.objects.exclude(pk=self.request.user.pk).order_by("username")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["total_users"] = User.objects.count()
        context["is_manager"] = self.request.user.groups.filter(
            name="Менеджер"
        ).exists()
        return context


# 2. Блокировка/разблокировка пользователя (toggle is_active)
class ToggleUserActiveView(LoginRequiredMixin, View):

    def get(self, request, *args, **kwargs):
        if not is_user_manager(request.user):
            raise PermissionDenied("Доступ только для менеджеров.")

        # Получаем пользователя по pk из URL
        user = CustomUser.objects.get(pk=kwargs["pk"])

        # Не даём блокировать самого себя
        if user == request.user:
            messages.error(request, "Нельзя блокировать самого себя.")
            return redirect("mailings:user_list")

        # Toggle: меняем is_active на противоположное
        user.is_active = not user.is_active
        user.save()

        # Сообщение
        status = "заблокирован" if not user.is_active else "разблокирован"
        messages.success(request, f"Пользователь {user.username} {status}.")

        # Редирект на список
        return redirect("users:user_list")


# 3. Отключение/включение рассылок для пользователя (toggle is_mailing_active)
class ToggleUserMailingView(LoginRequiredMixin, View):

    def get(self, request, *args, **kwargs):
        if not is_user_manager(request.user):
            raise PermissionDenied("Доступ только для менеджеров.")

        # Получаем пользователя по pk из URL
        user = CustomUser.objects.get(pk=kwargs["pk"])

        # Не даём изменять свои рассылки таким способом
        if user == request.user:
            messages.error(request, "Нельзя изменять свои рассылки таким способом.")
            return redirect("mailings:user_list")

        # Toggle: меняем is_mailing_active на противоположное
        user.is_mailing_active = not user.is_mailing_active
        user.save()

        # Сообщение
        status = "отключены" if not user.is_mailing_active else "включены"
        messages.success(request, f"Рассылки для {user.username} {status}.")

        # Редирект на список
        return redirect("users:user_list")
