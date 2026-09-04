from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from lms.views import (
    CourseViewSet,
    LessonListCreateAPIView,
    LessonRetrieveUpdateDestroyAPIView,
    CourseSubscribeAPIView,
)
from users.views import (
    PaymentViewSet,
    RegistrationAPIView,
    UserViewSet,
    CreatePaymentAPIView,
)
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

schema_view = get_schema_view(
    openapi.Info(
        title="Educational Platform API",
        default_version="v1",
        description="Документация для образовательного проекта.",
        terms_of_service="#",
        contact=openapi.Contact(email="contact@example.com"),
        license=openapi.License(name="BSD License"),
    ),
    public=True,
    permission_classes=[
        permissions.AllowAny,
    ],
)


router = DefaultRouter()
router.register(r"courses", CourseViewSet, basename="course")
router.register(r"payments", PaymentViewSet, basename="payment")
router.register(r"users", UserViewSet)

urlpatterns = [
    path("admin/", admin.site.urls),
    path(
        "api/courses/<uuid:pk>/subscribe/",
        CourseSubscribeAPIView.as_view(),
        name="course-subscribe",
    ),
    path("api/", include(router.urls)),
    path("api/auth/register/", RegistrationAPIView.as_view(), name="register"),
    path("api/auth/token/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("api/auth/token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("api/lessons/", LessonListCreateAPIView.as_view(), name="lesson-list"),
    path(
        "api/lessons/<uuid:pk>/",
        LessonRetrieveUpdateDestroyAPIView.as_view(),
        name="lesson-detail",
    ),
    path(
        "swagger/",
        schema_view.with_ui("swagger", cache_timeout=0),
        name="schema-swagger-ui",
    ),
    path("redoc/", schema_view.with_ui("redoc", cache_timeout=0), name="schema-redoc"),
    path("api/payments/create/", CreatePaymentAPIView.as_view(), name="create-payment"),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
