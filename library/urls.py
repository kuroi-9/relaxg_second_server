from django.urls import path

from . import views

urlpatterns = [
    path("bookseries/", views.LibraryDashboardBookSeriesAPIView.as_view(), name="dashboardbookseries"),
    path("refresh/", views.LibraryRefreshAPIView.as_view(), name="index"),
]
