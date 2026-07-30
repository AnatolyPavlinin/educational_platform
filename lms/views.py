from rest_framework import viewsets, generics, permissions
from .models import Course, Lesson
from .serializers import CourseSerializer, LessonSerializer
from rest_framework.permissions import AllowAny
from users.permissions import IsModerator


class CourseViewSet(viewsets.ModelViewSet):
    queryset = Course.objects.all()
    serializer_class = CourseSerializer

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            permission_classes = [permissions.IsAuthenticated]

        elif self.action == 'create':
            permission_classes = [permissions.IsAuthenticated]

        elif self.action in ['update', 'partial_update']:
            permission_classes = [permissions.IsAuthenticated, IsModerator]

        elif self.action == 'destroy':
            permission_classes = [permissions.IsAuthenticated, IsModerator]

        else:
            permission_classes = [permissions.IsAuthenticated]

        return [permission() for permission in permission_classes]


class LessonListCreateAPIView(generics.ListCreateAPIView):
    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer
    permission_classes = [permissions.IsAuthenticated]


class LessonRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer

    # Видеть детальки может любой залогиненный.
    # Обновлять (PUT/PATCH) — владелец ИЛИ модератор.
    # Удалять — только модератор (или владелец, см. Задание 3).
    permission_classes = [
        permissions.IsAuthenticated,
        IsModerator | permissions.DjangoModelPermissions
        # DjangoModelPermissions проверяет add/change/delete из админки
    ]
