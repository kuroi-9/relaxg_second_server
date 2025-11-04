from django.contrib import admin
from django.urls import path, include
# Django views
from rest_framework_simplejwt.views import TokenVerifyView
# App views
from rg_server.views import (
    CustomTokenObtainPairView,
    CustomTokenRefreshView,
    LogoutView,
    UserMeView,
    ProtectedDataView,
    PublicInfoView,
    get_csrf_token
)

urlpatterns = [
    path('admin/', admin.site.urls),

    # Auth
    # Getting token if correct credentials
    path('api/token/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    # Refreshing tokens
    path('api/token/refresh/', CustomTokenRefreshView.as_view(), name='token_refresh'),
    # Verifying a token (useful for debugging)
    path('api/token/verify/', TokenVerifyView.as_view(), name='token_verify'),
    # Logout
    path('api/logout/', LogoutView.as_view(), name='logout'),

    # User and protected views
    # Retrieve user information
    path('api/user/me/', UserMeView.as_view(), name='user_me'),
    # Example of protected resource
    path('api/protected-data/', ProtectedDataView.as_view(), name='protected_data'),

    # Public views
    # Public test view
    path('api/public-info/', PublicInfoView.as_view(), name='public_info'),
    # View to obtain CSRF token
    path('api/get-csrf-token/', get_csrf_token, name='get_csrf_token'),

    # Library app views
    path('api/library/', include('library.urls')),

    # Jobs Manager app views
    path('api/jobs/', include('jobs_manager.urls'))
]
