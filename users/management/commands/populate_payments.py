from django.core.management.base import BaseCommand
from django.utils import timezone
from decimal import Decimal
from users.models import User, Payment
from lms.models import Course, Lesson
from django.contrib.contenttypes.models import ContentType


class Command(BaseCommand):
    help = "Заполняет таблицу платежей тестовыми данными"

    def handle(self, *args, **options):
        # Получаем контент-типы для GenericRelation
        course_ct = ContentType.objects.get_for_model(Course)
        lesson_ct = ContentType.objects.get_for_model(Lesson)

        try:
            user = User.objects.first()
            course = Course.objects.first()
            lesson = Lesson.objects.first()

            if not all([user, course, lesson]):
                self.stdout.write(
                    self.style.ERROR(
                        "Сначала создайте хотя бы одного пользователя, один курс и один урок."
                    )
                )
                return

            Payment.objects.create(
                user=user,
                content_type=course_ct,
                object_id=course.id,
                amount=Decimal("999.00"),
                method="cash",
                payment_date=timezone.now(),
            )

            Payment.objects.create(
                user=user,
                content_type=lesson_ct,
                object_id=lesson.id,
                amount=Decimal("199.00"),
                method="transfer",
                payment_date=timezone.now(),
            )

            self.stdout.write(self.style.SUCCESS("Данные успешно добавлены!"))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Ошибка: {e}"))
