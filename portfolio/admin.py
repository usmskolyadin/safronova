from django.contrib import admin
from django.utils.html import format_html

from .models import (
    AboutPage,
    GalleryPhoto,
    MethodicalMaterial,
    PortfolioPage,
    SiteSettings,
    StudentAchievement,
    TeacherAchievement,
)

admin.site.site_header = "Управление сайтом-портфолио"
admin.site.site_title = "Панель управления сайтом"
admin.site.index_title = "Редактирование содержимого сайта"


class SingletonAdmin(admin.ModelAdmin):
    """Не позволяет создавать/удалять больше одного экземпляра."""

    def has_add_permission(self, request):
        return not self.model.objects.exists()

    def has_delete_permission(self, request, obj=None):
        return False

    def changelist_view(self, request, extra_context=None):
        obj = self.model.load()
        from django.shortcuts import redirect
        from django.urls import reverse

        return redirect(
            reverse(
                f"admin:{self.model._meta.app_label}_{self.model._meta.model_name}_change",
                args=[obj.pk],
            )
        )


@admin.register(SiteSettings)
class SiteSettingsAdmin(SingletonAdmin):
    fieldsets = (
        ("Шапка сайта", {
            "fields": ("site_name", "teacher_full_name", "teacher_position", "logo_initials"),
        }),
        ("Главная страница", {
            "fields": ("hero_title", "hero_subtitle", "hero_photo", "hero_quote", "about_preview"),
        }),
        ("Контакты", {
            "fields": ("email", "phone", "address", "vk_url", "telegram_url"),
        }),
        ("Подвал сайта", {
            "fields": ("footer_text",),
        }),
    )


@admin.register(AboutPage)
class AboutPageAdmin(SingletonAdmin):
    fieldsets = (
        (None, {
            "fields": (
                "photo",
                "intro",
                "education",
                "experience",
                "philosophy",
                "achievements_summary",
                "hobbies",
            )
        }),
    )


@admin.register(PortfolioPage)
class PortfolioPageAdmin(SingletonAdmin):
    fields = ("title", "intro")


class ImagePreviewMixin:
    def image_preview(self, obj):
        image = getattr(obj, "image", None) or getattr(obj, "cover_image", None) or getattr(obj, "hero_photo", None)
        if image:
            return format_html('<img src="{}" style="height:60px;border-radius:6px;" />', image.url)
        return "—"

    image_preview.short_description = "Превью"


@admin.register(TeacherAchievement)
class TeacherAchievementAdmin(ImagePreviewMixin, admin.ModelAdmin):
    list_display = ("title", "year", "image_preview", "order")
    list_editable = ("order",)
    search_fields = ("title", "description")
    list_filter = ("year",)


@admin.register(StudentAchievement)
class StudentAchievementAdmin(ImagePreviewMixin, admin.ModelAdmin):
    list_display = ("title", "student_name", "year", "image_preview", "order")
    list_editable = ("order",)
    search_fields = ("title", "student_name", "description")
    list_filter = ("year",)


@admin.register(MethodicalMaterial)
class MethodicalMaterialAdmin(ImagePreviewMixin, admin.ModelAdmin):
    list_display = ("title", "category", "grade", "date_added", "image_preview", "order")
    list_editable = ("order",)
    list_filter = ("category", "grade")
    search_fields = ("title", "description")


@admin.register(GalleryPhoto)
class GalleryPhotoAdmin(ImagePreviewMixin, admin.ModelAdmin):
    list_display = ("caption", "image_preview", "order", "uploaded_at")
    list_editable = ("order",)
    search_fields = ("caption",)
