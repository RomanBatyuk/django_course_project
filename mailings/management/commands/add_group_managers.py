from django.contrib.auth.models import Group, Permission, User
from django.contrib.contenttypes.models import ContentType
from django.core.management.base import BaseCommand
from myapp.models import Mailing, Mailing_recipient


class Command(BaseCommand):
    help = "Создает группу Менеджеры и назначает ей права"

    def handle(self, *args, **options):
        managers_group, created = Group.objects.get_or_create(name="Менеджеры")

        mailing_recipient = ContentType.objects.get_for_model(Mailing_recipient)
        mailing = ContentType.objects.get_for_model(Mailing)
        user = ContentType.objects.get_for_model(User)

        try:
            view_client_perm = Permission.objects.get(
                codename="view_client", content_type=mailing_recipient
            )
            view_mailing_perm = Permission.objects.get(
                codename="view_mailing", content_type=mailing
            )
            view_user_perm = Permission.objects.get(
                codename="view_user", content_type=user
            )
            change_user_perm = Permission.objects.get(
                codename="change_user", content_type=user
            )
            change_mailing_perm = Permission.objects.get(
                codename="change_mailing", content_type=mailing
            )
        except Permission.DoesNotExist as e:
            self.stdout.write(self.style.ERROR(f"Ошибка: {e}"))
            return

        managers_group.permissions.set(
            [
                view_client_perm,
                view_mailing_perm,
                view_user_perm,
                change_user_perm,
                change_mailing_perm,
            ]
        )
        managers_group.save()

        if created:
            self.stdout.write(
                self.style.SUCCESS('Группа "Менеджеры" создана и права назначены')
            )
        else:
            self.stdout.write(
                self.style.SUCCESS('Группа "Менеджеры" обновлена с новыми правами')
            )
