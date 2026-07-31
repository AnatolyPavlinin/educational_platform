from rest_framework import viewsets, generics, permissions
from .models import Course, Lesson
from .serializers import CourseSerializer, LessonSerializer
from users.permissions import IsModerator, IsOwner


class CourseViewSet(viewsets.ModelViewSet):
    serializer_class = CourseSerializer

    def get_queryset(self):
        # Модераторы видят всё, обычные пользователи — только своё
        if self.request.user.groups.filter(name="moderators").exists():
            return Course.objects.all()
        return Course.objects.filter(owner=self.request.user)

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

    def get_permissions(self):
        if self.action in ["list", "retrieve"]:
            permission_classes = [permissions.IsAuthenticated]

        elif self.action == "create":
            # Авторизован И НЕ модератор
            permission_classes = [
                permissions.IsAuthenticated,
                ~IsModerator
            ]

        elif self.action in ["update", "partial_update"]:
            # Владелец ИЛИ модератор
            permission_classes = [
                permissions.IsAuthenticated,
                IsOwner | IsModerator
            ]

        elif self.action == "destroy":
            # Только владелец (модераторам удалять нельзя!)
            permission_classes = [
                permissions.IsAuthenticated,
                IsOwner
            ]

        else:
            permission_classes = [permissions.IsAuthenticated]

        return [permission() for permission in permission_classes]


class LessonListCreateAPIView(generics.ListCreateAPIView):
    serializer_class = LessonSerializer

    def get_queryset(self):
        if self.request.user.groups.filter(name="moderators").exists():
            return Lesson.objects.all()
        return Lesson.objects.filter(owner=self.request.user)

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

    def get_permissions(self):
        if self.request.method == "GET":
            permission_classes = [permissions.IsAuthenticated]
        else:  # POST
            permission_classes = [
                permissions.IsAuthenticated,
                ~IsModerator
            ]
        return [permission() for permission in permission_classes]


class LessonRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = LessonSerializer

    def get_queryset(self):
        if self.request.user.groups.filter(name="moderators").exists():
            return Lesson.objects.all()
        return Lesson.objects.filter(owner=self.request.user)

    def get_permissions(self):
        if self.request.method == "GET":
            permission_classes = [permissions.IsAuthenticated]

        elif self.request.method in ["PUT", "PATCH"]:
            permission_classes = [
                permissions.IsAuthenticated,
                IsOwner | IsModerator
            ]

        else:  # DELETE
            permission_classes = [
                permissions.IsAuthenticated,
                IsOwner
            ]

        return [permission() for permission in permission_classes]
