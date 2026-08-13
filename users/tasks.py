from __future__ import absolute_import, unicode_literals
from celery import shared_task
from django.core.mail import send_mail
from lms.models import CourseSubscription, Course
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings


@shared_task
def send_course_update_email(course_id: str):
    try:
        course = Course.objects.get(id=course_id)

        subscribers = CourseSubscription.objects.filter(
            course=course,
            user__is_active=True
        ).select_related('user')

        for sub in subscribers:
            subject = f"Обновление материалов по курсу '{course.title}'"

            html_message = render_to_string('emails/course_update.html', {'course': course})
            plain_message = strip_tags(html_message)

            send_mail(
                subject,
                plain_message,
                settings.DEFAULT_FROM_EMAIL,
                [sub.user.email],
                fail_silently=False,
                html_message=html_message
            )

    except Exception as e:
        pass
