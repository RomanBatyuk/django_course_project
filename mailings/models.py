from django.db import models

from users.models import CustomUser


class Mailing_recipient(models.Model):
    """Модель «Получатель рассылки»"""

    email = models.EmailField(unique=True, verbose_name="Email")
    full_name = models.CharField(max_length=50, verbose_name="Ф.И.О")
    comment = models.TextField(verbose_name="Комментарий")
    owner = models.ForeignKey(
        CustomUser, on_delete=models.CASCADE, verbose_name="Владелец"
    )

    class Meta:
        verbose_name = "Получатель рассылки"
        verbose_name_plural = "Получатели рассылок"

        permissions = [
            # ("cancellation_of_product", "cancellation of product"),  # отмена публикации
        ]


class Message(models.Model):
    """Модель «Сообщение»"""

    subject_of_the_letter = models.CharField(
        max_length=30, verbose_name="Тема сообщения"
    )
    body_of_the_letter = models.TextField(verbose_name="Тело сообщения")
    owner = models.ForeignKey(
        CustomUser, on_delete=models.CASCADE, verbose_name="Владелец"
    )

    class Meta:
        verbose_name = "Сообщение"
        verbose_name_plural = "Сообщения"

        permissions = [
            # ("cancellation_of_product", "cancellation of product"),  # отмена публикации
        ]


class Mailing(models.Model):
    """Модель «Рассылка»"""

    start_message = models.DateTimeField(auto_now_add=True)
    end_message = models.DateTimeField(auto_now=True)

    STATUS_CREATED = "Создана"
    STATUS_RUNNING = "Запущена"
    STATUS_COMPLETED = "Завершена"

    STATUS_CHOICES = [
        (STATUS_CREATED, "Создана"),
        (STATUS_RUNNING, "Запущена"),
        (STATUS_COMPLETED, "Завершена"),
    ]

    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        verbose_name="Статус",
        default=STATUS_CREATED,
    )

    message = models.ForeignKey(
        Message,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="child_mailings",
        verbose_name="Сообщение",
    )
    recipients = models.ManyToManyField(
        Mailing_recipient,
        related_name="messages",
        blank=True,
        verbose_name="Получатели",
    )
    owner = models.ForeignKey(
        CustomUser, on_delete=models.CASCADE, verbose_name="Владелец"
    )

    class Meta:
        verbose_name = "Рассылка"
        verbose_name_plural = "Рассылки"

        permissions = [
            # ("cancellation_of_product", "cancellation of product"),  # отмена публикации
        ]


class Mailing_attempt(models.Model):
    """Модель «Попытка рассылки»"""

    STATUS_CHOICES = [
        ("Успешно", "Успешно"),
        ("Не успешно", "Не успешно"),
    ]
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="Не успешно",
        verbose_name="Статус",
    )
    data_attempt = models.DateTimeField(
        auto_now_add=True, verbose_name="Дата и время попытки"
    )
    server_response = models.TextField(verbose_name="Ответ сервера")
    mailing = models.ForeignKey(
        Mailing,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="attempts",
        verbose_name="Рассылка",
    )

    def __str__(self):
        return f"Попытка {self.data_attempt} - {self.status}"

    class Meta:
        verbose_name = "Попытка рассылки"
        verbose_name_plural = "Попытки рассылок"
