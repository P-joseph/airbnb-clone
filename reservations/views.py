import datetime
from django.http import Http404
from django.views.generic import View, DetailView, TemplateView
from django.contrib import messages
from django.shortcuts import render, redirect, reverse
from rooms import models as room_models
from reviews import forms as reviews_forms
from users import models as user_models
from . import models


class CreateError(Exception):
    pass


def create(request, room, year, month, day):
    try:
        date_obj = datetime.datetime(year, month, day)
        room = room_models.Room.objects.get(pk=room)
        models.BookedDay.objects.get(day=date_obj, reservation__room=room)
        raise CreateError()
    except (room_models.Room.DoesNotExist, CreateError):
        messages.error(request, "Can't Reserve That Room")
        return redirect(reverse("core:home"))
    except models.BookedDay.DoesNotExist:
        reservation = models.Reservation.objects.create(
            guest=request.user,
            room=room,
            check_in=date_obj,
            check_out=date_obj + datetime.timedelta(days=1),
        )
        return redirect(reverse("reservations:detail", kwargs={"pk": reservation.pk}))


class ReservationDetailView(View):
    def get(self, *args, **kwargs):
        pk = kwargs.get("pk")
        reservation = models.Reservation.objects.get_or_none(pk=pk)
        if not reservation or (reservation.guest != self.request.user and reservation.room.host != self.request.user):
            raise Http404()
        form = reviews_forms.CreateReviewForm()
        return render(self.request, "reservations/detail.html", {"reservation": reservation, "form": form})


def edit_reservation(request, pk, verb):
    reservation = models.Reservation.objects.get_or_none(pk=pk)
    if not reservation or (reservation.guest != request.user and reservation.room.host != request.user):
        raise Http404()
    if verb == "confirm":
        reservation.status = models.Reservation.STATUS_CONFIRMED
    elif verb == "cancel":
        reservation.status = models.Reservation.STATUS_CANCELED
        models.BookedDay.objects.filter(reservation=reservation).delete()
    reservation.save()
    messages.success(request, "Reservation Updated")
    return redirect(reverse("reservations:detail", kwargs={"pk": reservation.pk}))


class ReservationManagementView(TemplateView):

    template_name = "reservations/management.html"

    def get(self, request, *args, **kwargs):
        pk = kwargs.get("pk")
        try:
            is_hosting = request.session['is_hosting']
        except KeyError:
            is_hosting = False

        user = user_models.User.objects.get_or_none(pk=pk)
        rooms = room_models.Room.objects.filter(host=user)
        reservations = models.Reservation.objects.filter(guest=user)

        return render(self.request, "reservations/management.html", {"reservations": reservations, "rooms": rooms, "is_hosting": is_hosting})
