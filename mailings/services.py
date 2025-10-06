from django.contrib.auth import get_user_model

User = get_user_model()


def is_user_manager(user):
    """
    Проверяет, является ли пользователь членом группы 'Менеджер'.
    """
    return user.is_authenticated and user.groups.filter(name="Менеджер").exists()


def can_view_all(user, obj_type=None):
    """
    Менеджер может просматривать всё (клиентов, рассылки, пользователей).
    """
    return is_user_manager(user)


def can_manage_own(user, obj):
    """
    Пользователь может управлять только своими объектами (если obj.owner == user).
    Используется для CRUD (создание, редактирование, удаление) своих клиентов и рассылок.
    """
    if not user.is_authenticated:
        return False
    return obj.owner == user


def can_disable_mailing(user, obj):
    """
    Менеджер может отключать рассылки (изменять статус, например, is_active).
    """
    return is_user_manager(user)


def can_block_user(user):
    """
    Менеджер может блокировать пользователей (изменять статус, например, is_active).
    """
    return is_user_manager(user)
