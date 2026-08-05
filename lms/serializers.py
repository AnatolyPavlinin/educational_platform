from rest_framework import serializers
from .models import Course, Lesson, CourseSubscription
from .validators import validate_youtube_url


class LessonSerializer(serializers.ModelSerializer):
    course_title = serializers.CharField(source='course.title', read_only=True)

    class Meta:
        model = Lesson
        fields = '__all__'
        read_only_fields = ['id', 'owner']

    video_url = serializers.URLField(validators=[validate_youtube_url])


class CourseSerializer(serializers.ModelSerializer):
    lessons_count = serializers.SerializerMethodField()
    lessons = LessonSerializer(many=True, read_only=True)
    is_subscribed = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Course
        fields = ['id', 'title', 'preview', 'description', 'lessons_count', 'lessons', 'owner', 'is_subscribed']
        read_only_fields = ['id', 'owner', 'is_subscribed']

    def get_lessons_count(self, obj):
        return obj.lessons.count()

    def get_is_subscribed(self, obj):
        request = self.context.get('request')

        if not request or not request.user.is_authenticated:
            return False

        return CourseSubscription.objects.filter(
            user=request.user,
            course=obj
        ).exists()
