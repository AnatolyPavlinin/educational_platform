from rest_framework import viewsets, generics, permissions, status
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from .models import Payment, User
from users.serializers import PaymentSerializer, UserCreateSerializer, UserSerializer
from .filters import PaymentFilter
from django_filters.rest_framework import DjangoFilterBackend


class PaymentViewSet(viewsets.ModelViewSet):
    queryset = Payment.objects.all().select_related('user', 'content_type')
    serializer_class = PaymentSerializer

    filter_backends = [DjangoFilterBackend]
    filterset_class = PaymentFilter


class RegistrationAPIView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserCreateSerializer
    permission_classes = [AllowAny]


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()

    def get_permissions(self):
        if self.action == 'create':
            return [permissions.AllowAny()]
        return [permissions.IsAuthenticated()]

    def get_serializer_class(self):
        if self.action == 'create':
            return UserCreateSerializer
        return UserSerializer

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()

        # ВАЖНОЕ ДОПОЛНЕНИЕ К КРИТЕРИЯМ ЗАДАНИЯ 3:
        # Пользователь может просматривать детали любого профиля через /api/users/{id}/
        # Но обновлять и удалять сможет только свои (это настроим позже).
        # Сейчас просто возвращаем данные.
        serializer = self.get_serializer(instance)
        return Response(serializer.data)
