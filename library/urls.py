from django.urls import path

from . import views

urlpatterns = [
    path("bookseries/", views.LibraryDashboardBookSeriesAPIView.as_view(), name="dashboardbookseries"),
    path("refresh/", views.LibraryRefreshAPIView.as_view(), name="index"),
    path("user/preferences/", views.UserLibraryPreferencesAPIView.as_view(), name="user_detail"),
]
