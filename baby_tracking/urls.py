from django.urls import path
from .views import BabyView

urlpatterns = [
    path("", BabyView.as_view(), name="create-baby")
]