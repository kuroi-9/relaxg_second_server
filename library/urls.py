from django.urls import path

from . import views

urlpatterns = [
    path("bookseries/", views.LibraryDashboardBookSeriesAPIView.as_view(), name="dashboardbookseries"),
    path("bookseries/covers/", views.LibraryDashboardBookSeriesCoversAPIView.as_view(), name="dashboardbookseriescovers"),
    path("bookseries/books/<str:bookseries_title>", views.LibraryBookseriesBooksAPIView.as_view(), name="dashboardbookseriesbooks"),
    path("refresh/", views.LibraryRefreshAPIView.as_view(), name="index"),
    path("user/preferences/", views.UserLibraryPreferencesAPIView.as_view(), name="user_detail"),
]
