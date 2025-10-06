from django import forms
from django.contrib.auth.forms import UserCreationForm
from django_countries.widgets import CountrySelectWidget

from users.models import CustomUser


class CustomUserCreationForm(UserCreationForm):
    phone_number = forms.CharField(
        max_length=15,
        required=False,
        help_text="Необязательное поле. Введите ваш номер телефона.",
    )

    class Meta(UserCreationForm.Meta):
        model = CustomUser
        fields = (
            "email",
            "avatar",
            "first_name",
            "last_name",
            "phone_number",
            "country",
            "password1",
            "password2",
        )

    def clean_phone_number(self):
        phone_number = self.cleaned_data.get("phone_number")
        if phone_number and not phone_number.isdigit():
            raise forms.ValidationError("Phone number must contain only digits.")
        return phone_number


class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = [
            "first_name",
            "last_name",
            "avatar",
            "phone_number",
            "country",
        ]  # Исключены email и is_mailing_active
        widgets = {
            "country": CountrySelectWidget(
                attrs={"class": "form-control"}
            ),  # Красивый выбор страны
            "phone_number": forms.TextInput(attrs={"placeholder": "+79123456789"}),
        }

    # Убираем email из формы (если не хотим его редактировать)
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if "email" in self.fields:
            self.fields["email"].disabled = True

    # Валидация телефона
    def clean_phone_number(self):
        phone_number = self.cleaned_data.get("phone_number")
        if phone_number and not phone_number.startswith("+"):
            raise forms.ValidationError(
                "Номер должен начинаться с '+' (например, +79123456789)."
            )
        return phone_number
