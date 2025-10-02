from django.urls import path

from mailings.apps import MailingsConfig
from mailings.views import (
    Mailing_recipientCreateView,
    Mailing_recipientDeleteView,
    Mailing_recipientDetailView,
    Mailing_recipientListView,
    Mailing_recipientUpdateView,
    MailingCreateView,
    MailingDeleteView,
    MailingDetailView,
    MailingListView,
    MailingUpdateView,
    MessageCreateView,
    MessageDeleteView,
    MessageDetailView,
    MessageListView,
    MessageUpdateView,
    mailing_statistics_view,
)

from . import views

app_name = MailingsConfig.name

urlpatterns = [
    path("", views.main_view, name="main"),
    path("message/", MessageListView.as_view(), name="message_list"),
    path("message/new", MessageCreateView.as_view(), name="message_create"),
    path("message/<int:pk>", MessageDetailView.as_view(), name="message_detail"),
    path("message/<int:pk>/edit", MessageUpdateView.as_view(), name="message_edit"),
    path("message/<int:pk>/delete", MessageDeleteView.as_view(), name="message_delete"),
    path("mailing/", MailingListView.as_view(), name="mailing_list"),
    path(
        "send_mailing/<int:mailing_id>/", views.send_mailing_view, name="send_mailing"
    ),
    path("mailing/new", MailingCreateView.as_view(), name="mailing_create"),
    path("mailing/<int:pk>", MailingDetailView.as_view(), name="mailing_detail"),
    path("mailing/<int:pk>/edit", MailingUpdateView.as_view(), name="mailing_edit"),
    path("mailing/<int:pk>/delete", MailingDeleteView.as_view(), name="mailing_delete"),
    path("recipient/", Mailing_recipientListView.as_view(), name="recipient_list"),
    path(
        "recipient/new", Mailing_recipientCreateView.as_view(), name="recipient_create"
    ),
    path(
        "recipient/<int:pk>",
        Mailing_recipientDetailView.as_view(),
        name="recipient_detail",
    ),
    path(
        "recipient/<int:pk>/edit",
        Mailing_recipientUpdateView.as_view(),
        name="recipient_edit",
    ),
    path(
        "recipient/<int:pk>/delete",
        Mailing_recipientDeleteView.as_view(),
        name="recipient_delete",
    ),
    path("statistics/", mailing_statistics_view, name="mailing_statistics"),
]
