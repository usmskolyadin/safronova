from django.views.generic import ListView, TemplateView

from .models import (
    AboutPage,
    GalleryPhoto,
    MethodicalMaterial,
    PortfolioPage,
    SiteSettings,
    StudentAchievement,
    TeacherAchievement,
)


class HomeView(TemplateView):
    template_name = "portfolio/home.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["about"] = AboutPage.load()
        context["teacher_achievements"] = TeacherAchievement.objects.all()[:3]
        context["gallery_preview"] = GalleryPhoto.objects.all()[:6]
        return context


class AboutView(TemplateView):
    template_name = "portfolio/about.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["about"] = AboutPage.load()
        return context


class PortfolioHomeView(TemplateView):
    template_name = "portfolio/portfolio_home.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["portfolio_page"] = PortfolioPage.load()
        context["teacher_achievements_count"] = TeacherAchievement.objects.count()
        context["student_achievements_count"] = StudentAchievement.objects.count()
        context["methodical_count"] = MethodicalMaterial.objects.count()
        context["gallery_count"] = GalleryPhoto.objects.count()
        return context


class TeacherAchievementListView(ListView):
    model = TeacherAchievement
    template_name = "portfolio/teacher_achievements.html"
    context_object_name = "achievements"
    paginate_by = 12


class StudentAchievementListView(ListView):
    model = StudentAchievement
    template_name = "portfolio/student_achievements.html"
    context_object_name = "achievements"
    paginate_by = 12


class MethodicalMaterialListView(ListView):
    model = MethodicalMaterial
    template_name = "portfolio/methodical.html"
    context_object_name = "materials"
    paginate_by = 12

    def get_queryset(self):
        qs = super().get_queryset()
        category = self.request.GET.get("category")
        if category:
            qs = qs.filter(category=category)
        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["categories"] = MethodicalMaterial.CATEGORY_CHOICES
        context["selected_category"] = self.request.GET.get("category", "")
        return context


class GalleryListView(ListView):
    model = GalleryPhoto
    template_name = "portfolio/gallery.html"
    context_object_name = "photos"
    paginate_by = 24
