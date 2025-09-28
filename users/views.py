from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from django.views.generic import DetailView
from django.views.generic.edit import CreateView, UpdateView

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
