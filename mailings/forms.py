from django import forms

from mailings.models import Mailing, Mailing_recipient, Message


class MailingForm(forms.ModelForm):
    class Meta:
        model = Mailing
        fields = ["status", "message", "recipients"]  # Включаем ключевые поля
        # Или fields = '__all__' если хотите все, но start_message и end_message лучше исключить
        widgets = {
            "status": forms.Select(
                attrs={"class": "form-control"}
            ),  # Выпадающий список для статуса
            "message": forms.Select(
                attrs={"class": "form-control"}
            ),  # Выпадающий список для сообщения (ForeignKey)
            "recipients": forms.SelectMultiple(
                attrs={"class": "form-control"}
            ),  # Множественный выбор для получателей
        }
        labels = {
            "status": "Статус рассылки",
            "message": "Сообщение",
            "recipients": "Получатели",
        }


class MessageForm(forms.ModelForm):
    class Meta:
        model = Message
        fields = "__all__"
        widgets = {
            "subject_of_the_letter": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "Тема письма"}
            ),
            "body_of_the_letter": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 5,
                    "placeholder": "Текст письма",
                }
            ),
        }
        labels = {
            "subject_of_the_letter": "Тема письма",
            "body_of_the_letter": "Текст письма",
        }


class MailingRecipientForm(forms.ModelForm):
    class Meta:
        model = Mailing_recipient
        fields = "__all__"
        widgets = {
            "email": forms.EmailInput(
                attrs={"class": "form-control", "placeholder": "example@email.com"}
            ),
            "full_name": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "Иванов Иван Иванович"}
            ),
            "comment": forms.Textarea(
                attrs={"class": "form-control", "rows": 3, "placeholder": "Комментарий"}
            ),
        }
        labels = {
            "email": "Email",
            "full_name": "Ф.И.О.",
            "comment": "Комментарий",
        }
