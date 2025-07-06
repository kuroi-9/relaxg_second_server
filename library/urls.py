from django.urls import path

from . import views

urlpatterns = [
    path("refresh/", views.LibraryRefreshAPIView.as_view(), name="index"),
]
