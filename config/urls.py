from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from lms.views import CourseViewSet, LessonListCreateAPIView, LessonRetrieveUpdateDestroyAPIView

router = DefaultRouter()
router.register(r'courses', CourseViewSet, basename='course')

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include(router.urls)),

    # Эндпоинты для уроков через Generic API Views
    path('api/lessons/', LessonListCreateAPIView.as_view(), name='lesson-list-create'),
    path('api/lessons/<uuid:pk>/', LessonRetrieveUpdateDestroyAPIView.as_view(), name='lesson-detail'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
