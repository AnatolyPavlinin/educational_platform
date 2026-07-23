from lms.models import Course, Lesson
from rest_framework import serializers
from django.contrib.contenttypes.models import ContentType
from .models import Payment
from lms.serializers import CourseSerializer, LessonSerializer


class PaidObjectRelatedField(serializers.RelatedField):
    """
    Собственное поле для GenericForeignKey.
    В зависимости от типа связанного объекта возвращает нужный вложенный сериализатор.
    """

    def to_representation(self, value):
        if isinstance(value, Course):
            serializer = CourseSerializer(value, context=self.context)
        elif isinstance(value, Lesson):
            serializer = LessonSerializer(value, context=self.context)
        else:
            return None

        return serializer.data

    def to_internal_value(self, data):
        raise NotImplementedError("Это поле только для чтения при выводе")


class PaymentSerializer(serializers.ModelSerializer):
    user_email = serializers.ReadOnlyField(source='user.email')
    paid_object = PaidObjectRelatedField(read_only=True)
    method_display = serializers.CharField(source='get_method_display', read_only=True)

    class Meta:
        model = Payment
        fields = [
            'id',
            'user',
            'user_email',
            'payment_date',
            'paid_object',
            'amount',
            'method',
            'method_display'
        ]
        read_only_fields = ['id', 'payment_date', 'user']
