from django.db.models import Q
from django.shortcuts import redirect, reverse
from django.views.generic import DetailView
from users import  models as user_models
from . import models

def go_conversation(request, host_pk, guest_pk):
    user_host = user_models.User.objects.get_or_none(pk=host_pk)
    user_guest = user_models.User.objects.get_or_none(pk=guest_pk)
    if user_host is not None and user_guest is not None:
        try:
            conversation = models.Conversation.objects.get(
                Q(participants=user_host) & Q(participants=user_guest)
            )
        except models.Conversation.DoesNotExist:
            conversation = models.Conversation.objects.create()
            conversation.participants.add(user_host, user_guest)
        return redirect(reverse("conversations:detail", kwargs={"pk": conversation.pk}))


class ConversationDetailView(DetailView):
    pass