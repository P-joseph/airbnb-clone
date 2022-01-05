from django.urls import path

urlpatterns = [
    path("create/<int:room>/<int:year>-<int-month>-<int-date>")
]