from django.core.management.base import BaseCommand

from portfolio.models import AboutPage, PortfolioPage, SiteSettings


class Command(BaseCommand):
    help = "Заполняет сайт стартовыми текстами, которые затем можно отредактировать в админ-панели."

    def handle(self, *args, **options):
        settings_obj = SiteSettings.load()
        if not settings_obj.email:
            settings_obj.site_name = "Портфолио учителя"
            settings_obj.teacher_full_name = "Иванова Мария Петровна"
            settings_obj.teacher_position = "Учитель русского языка и литературы"
            settings_obj.logo_initials = "МП"
            settings_obj.hero_title = "Добро пожаловать на мой сайт-портфолио"
            settings_obj.hero_subtitle = (
                "Учитель русского языка и литературы высшей квалификационной категории. "
                "Люблю свой предмет и стремлюсь передать эту любовь ученикам."
            )
            settings_obj.about_preview = (
                "Работаю учителем русского языка и литературы уже много лет. "
                "На этих страницах — мой педагогический путь, достижения и творческие находки."
            )
            settings_obj.email = "example@school.ru"
            settings_obj.phone = "+7 (900) 000-00-00"
            settings_obj.address = "МБОУ СОШ №1"
            settings_obj.footer_text = "Сайт-портфолио учителя русского языка и литературы"
            settings_obj.save()
            self.stdout.write(self.style.SUCCESS("Настройки сайта заполнены стартовыми текстами."))

        about_obj = AboutPage.load()
        if not about_obj.intro or about_obj.intro.startswith("Здравствуйте! Меня зовут"):
            about_obj.intro = (
                "Здравствуйте! Меня зовут Мария Петровна. Я учитель русского языка и литературы "
                "и убеждена, что слово способно вдохновлять, учить и объединять."
            )
            about_obj.education = "Здесь можно указать информацию об образовании и повышении квалификации."
            about_obj.experience = "Здесь можно рассказать о стаже и местах работы."
            about_obj.philosophy = "Здесь можно описать свои педагогические принципы и подход к преподаванию."
            about_obj.achievements_summary = "Здесь можно кратко перечислить основные награды и звания."
            about_obj.hobbies = "Здесь можно рассказать об увлечениях вне работы."
            about_obj.save()
            self.stdout.write(self.style.SUCCESS("Страница «Обо мне» заполнена стартовыми текстами."))

        portfolio_obj = PortfolioPage.load()
        if not portfolio_obj.intro:
            portfolio_obj.title = "Портфолио"
            portfolio_obj.intro = (
                "В этом разделе собраны материалы, отражающие мою педагогическую деятельность: "
                "личные достижения, успехи учеников, методические разработки и фотографии со школьных будней."
            )
            portfolio_obj.save()
            self.stdout.write(self.style.SUCCESS("Страница «Портфолио» заполнена стартовым текстом."))

        self.stdout.write(self.style.SUCCESS("Готово. Все тексты можно изменить в административной панели."))
