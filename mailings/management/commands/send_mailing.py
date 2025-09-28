from django.conf import settings
from django.core.mail import send_mail
from django.core.management.base import BaseCommand
from django.utils import timezone

from mailings.models import Mailing


class Command(BaseCommand):
    help = "Отправляет email-рассылку на основе существующего Mailing (по ID)"

    def add_arguments(self, parser):
        parser.add_argument(
            "--mailing_id", type=int, required=True, help="ID существующего Mailing"
        )
        parser.add_argument(
            "--test",
            action="store_true",
            help="Тестовый режим (отправит только владельцу рассылки)",
        )

    def handle(self, *args, **options):
        mailing_id = options["mailing_id"]
        test_mode = options["test"]

        # Получаем Mailing по ID
        try:
            mailing = Mailing.objects.get(id=mailing_id)
        except Mailing.DoesNotExist:
            self.stdout.write(self.style.ERROR(f"Mailing с ID {mailing_id} не найден."))
            return

        # Проверяем статус
        if mailing.status != Mailing.STATUS_CREATED:
            self.stdout.write(
                self.style.ERROR(
                    f"Mailing уже запущен или завершён (статус: {mailing.status})."
                )
            )
            return

        # Получаем получателей
        recipients = mailing.recipients.all()
        if not recipients:
            self.stdout.write(self.style.ERROR("Нет получателей для рассылки."))
            return

        # Тестовый режим: отправляем только владельцу
        if test_mode:
            test_recipients = [mailing.owner.email] if mailing.owner.email else []
            self.stdout.write(
                self.style.WARNING(
                    "Режим тестирования! Отправляем только владельцу рассылки."
                )
            )
        else:
            # Получаем email из recipients
            test_recipients = [
                recipient.email for recipient in recipients if recipient.email
            ]
            self.stdout.write(
                f"Найдено {len(test_recipients)} получателей для рассылки."
            )

        # Получаем содержимое из message
        if not mailing.message:
            self.stdout.write(self.style.ERROR("У Mailing нет связанного Message."))
            return
        subject = mailing.message.subject_of_the_letter
        text_content = mailing.message.body_of_the_letter  # Текстовое содержимое

        # Обновляем статус на RUNNING
        mailing.status = Mailing.STATUS_RUNNING
        mailing.save()

        # Отправка писем
        sent_count = 0
        for recipient in (
            recipients if not test_mode else [None]
        ):  # В тесте recipient=None, используем owner
            try:
                email = recipient.email if recipient else mailing.owner.email
                full_name = (
                    recipient.full_name
                    if recipient
                    else mailing.owner.get_full_name() or "Владелец"
                )

                # Персонализация: заменяем плейсхолдеры в текстовом контенте
                personalized_content = text_content.replace(
                    "{{ full_name }}", full_name
                )
                personalized_content = personalized_content.replace(
                    "{{ email }}", email
                )
                # Добавьте другие плейсхолдеры, если нужны (например, {{ comment }} для recipient.comment)

                # Добавляем ссылку на отписку в конец текста
                unsubscribe_url = f"{settings.SITE_URL}/unsubscribe/?email={email}"  # Адаптируйте под вашу логику
                personalized_content += (
                    f"\n\nДля отписки перейдите по ссылке: {unsubscribe_url}"
                )

                send_mail(
                    subject=subject,
                    message=personalized_content,  # Текстовое сообщение
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[email],
                    fail_silently=False,
                )
                sent_count += 1
                self.stdout.write(f"Отправлено письмо для {email}")
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f"Ошибка отправки для {email}: {str(e)}")
                )

        # Обновляем статус на COMPLETED и end_message
        mailing.status = Mailing.STATUS_COMPLETED
        mailing.end_message = timezone.now()
        mailing.save()

        self.stdout.write(
            self.style.SUCCESS(
                f"Рассылка завершена! Успешно отправлено {sent_count} писем."
            )
        )
