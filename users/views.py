from rest_framework import viewsets
from .models import Payment
from users.serializers import PaymentSerializer
from .filters import PaymentFilter
from django_filters.rest_framework import DjangoFilterBackend


class PaymentViewSet(viewsets.ModelViewSet):
    queryset = Payment.objects.all().select_related('user', 'content_type')
    serializer_class = PaymentSerializer

    filter_backends = [DjangoFilterBackend]
    filterset_class = PaymentFilter
