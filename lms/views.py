from lms.paginators import StandardResultsSetPagination
from rest_framework import viewsets, generics, permissions, status
from .models import Course, Lesson, CourseSubscription
from .serializers import CourseSerializer, LessonSerializer
from users.permissions import IsModerator, IsOwner
from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response


class CourseViewSet(viewsets.ModelViewSet):
    queryset = Course.objects.all()
    serializer_class = CourseSerializer
    pagination_class = StandardResultsSetPagination

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
    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer
    pagination_class = StandardResultsSetPagination

    def get_queryset(self):
        if self.request.user.groups.filter(name="moderators").exists():
            return Lesson.objects.all().order_by('-id')

        qs = Lesson.objects.filter(owner=self.request.user).order_by('-id')
        return qs

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


class CourseSubscribeAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, *args, **kwargs):
        course_id = kwargs.get('pk')
        course_item = get_object_or_404(Course, id=course_id)

        # Ищем существующую подписку
        subs_item = CourseSubscription.objects.filter(
            user=request.user,
            course=course_item
        )

        if subs_item.exists():
            # Если есть — отписываемся
            subs_item.delete()
            message = 'Вы успешно отписались от обновлений курса.'
            subscribed = False
        else:
            # Если нет — создаем
            CourseSubscription.objects.create(user=request.user, course=course_item)
            message = 'Вы успешно подписались на обновления курса.'
            subscribed = True

        # Возвращаем сообщение и актуальный статус для фронтенда
        return Response({
            "message": message,
            "subscribed": subscribed
        }, status=status.HTTP_200_OK)
