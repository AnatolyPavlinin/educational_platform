from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from lms.views import CourseViewSet, LessonListCreateAPIView, LessonRetrieveUpdateDestroyAPIView, CourseSubscribeAPIView
from users.views import PaymentViewSet, RegistrationAPIView, UserViewSet
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView


router = DefaultRouter()
router.register(r'courses', CourseViewSet, basename='course')
router.register(r'payments', PaymentViewSet, basename='payment')
router.register(r'users', UserViewSet)

urlpatterns = [
    path('admin/', admin.site.urls),

    path('api/courses/<uuid:pk>/subscribe/', CourseSubscribeAPIView.as_view(), name='course-subscribe'),

    path('api/', include(router.urls)),

    path('api/auth/register/', RegistrationAPIView.as_view(), name='register'),
    path('api/auth/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/auth/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),


    path('api/lessons/', LessonListCreateAPIView.as_view(), name='lesson-list'),
    path('api/lessons/<uuid:pk>/', LessonRetrieveUpdateDestroyAPIView.as_view(), name='lesson-detail'),


]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
