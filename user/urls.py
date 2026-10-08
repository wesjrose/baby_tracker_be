from django.urls import path
from .views import UserView, ProfileView

urlpatterns = [
    path("", UserView.as_view(), name="create-user"),
    path("me/", ProfileView.as_view(), name="profile"),
]
