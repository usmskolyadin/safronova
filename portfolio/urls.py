from django.urls import path

from . import views

app_name = "portfolio"

urlpatterns = [
    path("", views.HomeView.as_view(), name="home"),
    path("about/", views.AboutView.as_view(), name="about"),
    path("portfolio/", views.PortfolioHomeView.as_view(), name="portfolio_home"),
    path(
        "portfolio/achievements/",
        views.TeacherAchievementListView.as_view(),
        name="teacher_achievements",
    ),
    path(
        "portfolio/students/",
        views.StudentAchievementListView.as_view(),
        name="student_achievements",
    ),
    path(
        "portfolio/methodical/",
        views.MethodicalMaterialListView.as_view(),
        name="methodical",
    ),
    path("portfolio/gallery/", views.GalleryListView.as_view(), name="gallery"),
]
