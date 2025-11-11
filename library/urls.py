from django.urls import path

from . import views

urlpatterns = [
    path("titles/", views.LibraryDashboardTitlesAPIView.as_view(), name="dashboard-titles"),
    path("titles/covers/", views.LibraryDashboardTitlesCoversAPIView.as_view(), name="dashboard-titles-covers"),
    path("titles/books/<str:title_name>", views.LibraryTitlesBooksAPIView.as_view(), name="dashboard-titles-books"),
    path("refresh/", views.LibraryRefreshAPIView.as_view(), name="index"),
    path("user/preferences/", views.UserLibraryPreferencesAPIView.as_view(), name="user-detail"),
    path("process/", views.TitleUpscaleRequestAPIView.as_view(), name="title-upscale-request-api-view"),
]
