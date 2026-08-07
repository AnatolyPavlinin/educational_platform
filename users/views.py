from lms.models import Course
from rest_framework import viewsets, generics, permissions, status
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from users.services.payments import create_stripe_product, create_checkout_session

from .models import Payment, User
from users.serializers import PaymentSerializer, UserCreateSerializer, UserSerializer
from .filters import PaymentFilter
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.views import APIView


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
        serializer = self.get_serializer(instance)
        return Response(serializer.data)


class CreatePaymentAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, format=None):
        data = request.data.copy()

        try:
            course = Course.objects.get(id=data['course'])
        except Course.DoesNotExist:
            return Response({"error": "Курс не найден"}, status=status.HTTP_404_NOT_FOUND)

        # Конвертируем сумму в копейки (центов), как требует Stripe
        amount_cents = int(float(data['amount']) * 100)

        # Создаем локальный платеж
        payment = Payment.objects.create(
            user=request.user,
            course=course,
            amount=data['amount']
        )

        # Вызываем сервисы Stripe
        stripe_data = create_stripe_product(payment.course.title, amount_cents)
        payment.stripe_product_id = stripe_data["product_id"]
        payment.stripe_price_id = stripe_data["price_id"]

        # Формируем ссылки возврата после оплаты
        base_url = request.build_absolute_uri('/')[:-1]
        success_url = f"{base_url}/api/payments/{payment.id}/success/"
        cancel_url = f"{base_url}/api/payments/{payment.id}/cancel/"

        checkout_result = create_checkout_session(stripe_data["price_id"], success_url, cancel_url)
        payment.stripe_session_id = checkout_result["session_id"]
        payment.checkout_url = checkout_result["checkout_url"]
        payment.save()  # Сохраняем все ID и ссылку

        serializer = PaymentSerializer(payment)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
