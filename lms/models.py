import uuid
from django.db import models


class Course(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=255)
    preview = models.ImageField(upload_to='course_previews/')
    description = models.TextField(blank=True, null=True)
    owner = models.ForeignKey('users.User', related_name='courses', on_delete=models.CASCADE)

    def __str__(self):
        return self.title


class Lesson(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    course = models.ForeignKey(Course, related_name='lessons', on_delete=models.CASCADE, null=True, blank=True)

    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    preview = models.ImageField(upload_to='lesson_previews/')
    video_url = models.URLField()
    owner = models.ForeignKey('users.User', related_name='lessons', on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return f'{self.course.title} - {self.title}'


class CourseSubscription(models.Model):
    user = models.ForeignKey('users.User', on_delete=models.CASCADE, related_name='subscriptions')
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='subscribers')

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        # Гарантируем, что одна пара Пользователь-Курс встречается только один раз
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'course'],
                name='unique_user_course_subscription'
            )
        ]

    def __str__(self):
        return f'{self.user.email} подписан на {self.course.title}'
