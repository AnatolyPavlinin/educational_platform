from io import BytesIO
from PIL import Image
from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase, APIClient
from users.models import User
from lms.models import Course, Lesson, CourseSubscription
from django.contrib.auth.models import Group


class LmsApiTests(APITestCase):

    def setUp(self):
        # Обычный пользователь
        self.user = User.objects.create_user(
            email="student@test.ru", password="testpass123"
        )

        # Модератор
        self.mod_group, _ = Group.objects.get_or_create(name="moderators")
        self.moderator = User.objects.create_user(
            email="mod@test.ru", password="modpass123"
        )
        self.moderator.groups.add(self.mod_group)

        # Объекты курса и урока
        self.course = Course.objects.create(
            title="Курс для тестов", description="Описание", owner=self.user
        )
        self.lesson = Lesson.objects.create(
            title="Урок 1",
            description="Описание урока",
            video_url="https://youtube.com/watch?v=valid",
            course=self.course,
            owner=self.user,
        )

        # URL-адреса
        self.list_url = reverse("lesson-list")
        self.detail_url = reverse("lesson-detail", args=[self.lesson.id])
        self.subscribe_url = reverse("course-subscribe", args=[self.course.id])

    def get_client(self, user=None):
        """Вспомогательный метод для получения клиента с аутентификацией"""
        client = APIClient()
        if user:
            client.force_authenticate(user=user)
        return client

    # --- ТЕСТЫ УРОКОВ (CRUD) ---

    def test_lesson_creation_by_owner(self):
        client = self.get_client(self.user)

        img_io = BytesIO()
        image = Image.new("RGB", (10, 10), color="red")
        image.save(img_io, format="JPEG")
        img_io.seek(0)

        uploaded_image = SimpleUploadedFile(
            name="test.jpg", content=img_io.read(), content_type="image/jpeg"
        )

        data = {
            "title": "Новый урок",
            "description": "Текст",
            "video_url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
            "course": str(self.course.id),
            "preview": uploaded_image,
        }

        response = client.post(self.list_url, data, format="multipart")

        print("DEBUG CREATE:", response.status_code, response.content.decode())

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_lesson_update_by_owner(self):
        client = self.get_client(self.user)
        new_title = "Обновленное название"
        response = client.patch(self.detail_url, {"title": new_title}, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.lesson.refresh_from_db()
        self.assertEqual(self.lesson.title, new_title)

    def test_lesson_delete_by_owner(self):
        """Владелец может удалить свой урок"""
        client = self.get_client(self.user)
        response = client.delete(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Lesson.objects.filter(id=self.lesson.id).exists())

    def test_permissions_cross_access(self):
        """Обычный пользователь НЕ может видеть/редактировать чужие уроки"""
        other_user = User.objects.create_user(email="other@test.ru", password="123")
        client_other = self.get_client(other_user)

        # 1. Проверка LIST: другой юзер не должен увидеть этот lesson в своем списке
        resp_list = client_other.get(reverse("lesson-list"))
        lessons_ids = [str(item["id"]) for item in resp_list.json()["results"]]

        # Главный критерий безопасности данных
        self.assertNotIn(str(self.lesson.id), lessons_ids)

        resp_patch = client_other.patch(
            self.detail_url, {"title": "Hack"}, format="json"
        )

        self.assertEqual(resp_patch.status_code, status.HTTP_404_NOT_FOUND)

    def test_moderator_can_edit_but_not_delete_via_viewset_logic(self):
        """Модератор может обновлять, но удаление сейчас разрешено только владельцу"""
        client = self.get_client(self.moderator)

        # Update - разрешен (IsOwner | IsModerator)
        resp_patch = client.patch(self.detail_url, {"title": "Mod Edit"}, format="json")
        self.assertEqual(resp_patch.status_code, status.HTTP_200_OK)

        # Delete - должен быть Forbidden (только IsOwner)
        resp_del = client.delete(self.detail_url)
        self.assertEqual(resp_del.status_code, status.HTTP_403_FORBIDDEN)

    # --- ТЕСТЫ ПОДПИСКИ ---

    def test_subscribe_toggle(self):
        client = self.get_client(self.user)

        # 1. Подписываемся (создаем запись)
        response = client.post(self.subscribe_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(
            CourseSubscription.objects.filter(
                user=self.user, course=self.course
            ).exists()
        )
        self.assertEqual(
            response.json()["message"], "Вы успешно подписались на обновления курса."
        )

        # 2. Отписываемся (удаляем запись)
        response = client.post(self.subscribe_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(
            CourseSubscription.objects.filter(
                user=self.user, course=self.course
            ).exists()
        )
        self.assertEqual(
            response.json()["message"], "Вы успешно отписались от обновлений курса."
        )

    def test_subscribe_anonymous_forbidden(self):
        """Неавторизованный пользователь не может подписываться"""
        client = APIClient()  # Без force_authenticate
        response = client.post(self.subscribe_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
