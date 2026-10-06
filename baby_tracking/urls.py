from django.urls import path
from .views import BabyView, EventView

urlpatterns = [
    path("", BabyView.as_view(), name="baby"),
    path("<uuid:baby_id>/event/", EventView.as_view(), name="event"),
]
