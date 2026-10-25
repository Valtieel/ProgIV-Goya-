from django.contrib import admin
from django.urls import path, include
from rest_framework_simplejwt.views import TokenRefreshView

from core.views import RegisterView, ThrottledTokenObtainPairView

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/", include("core.urls")),
    # Login con límite de 5 intentos por minuto y registro de los fallidos
    path("api/token/", ThrottledTokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("api/token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("api/register/", RegisterView.as_view(), name="register"),
    path("api-auth/", include("rest_framework.urls")),
]