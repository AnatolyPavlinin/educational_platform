import django_filters
from .models import Payment
from lms.models import Course, Lesson


class PaymentFilter(django_filters.FilterSet):
    ordering = django_filters.OrderingFilter(fields=(("payment_date", "date"),))

    # Фильтр по способу оплаты (выпадающий список)
    method = django_filters.ChoiceFilter(
        choices=Payment._meta.get_field("method").choices
    )

    # Фильтры по ID связанного объекта
    course = django_filters.UUIDFilter(
        field_name="object_id", method="filter_by_course"
    )
    lesson = django_filters.UUIDFilter(
        field_name="object_id", method="filter_by_lesson"
    )

    class Meta:
        model = Payment
        fields = ["method", "course", "lesson"]

    def filter_by_course(self, queryset, name, value):
        from django.contrib.contenttypes.models import ContentType

        ct = ContentType.objects.get_for_model(Course)
        return queryset.filter(content_type=ct, object_id=value)

    def filter_by_lesson(self, queryset, name, value):
        from django.contrib.contenttypes.models import ContentType

        ct = ContentType.objects.get_for_model(Lesson)
        return queryset.filter(content_type=ct, object_id=value)
