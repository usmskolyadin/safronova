from django.core.exceptions import ValidationError
from django.db import models


class SingletonModel(models.Model):
    """Базовая модель для разделов, которые существуют в единственном экземпляре."""

    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        self.pk = 1
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        pass

    @classmethod
    def load(cls):
        obj, _ = cls.objects.get_or_create(pk=1)
        return obj


class SiteSettings(SingletonModel):
    """Общие настройки сайта: шапка, контакты, подвал."""

    site_name = models.CharField(
        "Название сайта", max_length=200, default="Портфолио учителя"
    )
    teacher_full_name = models.CharField(
        "ФИО учителя", max_length=200, default="Иванова Мария Петровна"
    )
    teacher_position = models.CharField(
        "Должность / предмет",
        max_length=255,
        default="Учитель русского языка и литературы",
    )
    logo_initials = models.CharField(
        "Инициалы для логотипа", max_length=5, default="МП", blank=True
    )

    hero_title = models.CharField(
        "Заголовок на главной странице",
        max_length=255,
        default="Добро пожаловать на мой сайт-портфолио",
    )
    hero_subtitle = models.TextField(
        "Подзаголовок на главной странице",
        default="Учитель русского языка и литературы высшей категории",
    )
    hero_photo = models.ImageField(
        "Фото для главной страницы",
        upload_to="site/",
        blank=True,
        null=True,
    )
    hero_quote = models.TextField(
        "Цитата на главной странице",
        blank=True,
        default="«Слово — дело великое. Великое потому, что словом можно соединить людей, "
        "словом можно и разъединить их, словом можно служить любви, "
        "словом же можно служить вражде и ненависти» — Л.Н. Толстой",
    )

    about_preview = models.TextField(
        "Краткое описание для блока «Обо мне» на главной",
        blank=True,
        default="Расскажите немного о себе — этот текст будет показан на главной странице.",
    )

    email = models.EmailField("Электронная почта", blank=True)
    phone = models.CharField("Телефон", max_length=50, blank=True)
    address = models.CharField(
        "Место работы / адрес", max_length=255, blank=True
    )
    vk_url = models.URLField("Ссылка ВКонтакте", blank=True)
    telegram_url = models.URLField("Ссылка Telegram", blank=True)

    footer_text = models.CharField(
        "Текст в подвале сайта",
        max_length=255,
        blank=True,
        default="Сайт-портфолио учителя русского языка и литературы",
    )

    class Meta:
        verbose_name = "Настройки сайта"
        verbose_name_plural = "Настройки сайта"

    def __str__(self):
        return "Настройки сайта"


class AboutPage(SingletonModel):
    """Содержимое страницы «Обо мне»."""

    photo = models.ImageField(
        "Фотография", upload_to="about/", blank=True, null=True
    )
    intro = models.TextField(
        "Вступительный текст",
        default="Здравствуйте! Меня зовут ... и я расскажу немного о себе.",
    )
    education = models.TextField("Образование", blank=True)
    experience = models.TextField("Опыт работы", blank=True)
    philosophy = models.TextField(
        "Педагогическое кредо / принципы преподавания", blank=True
    )
    achievements_summary = models.TextField(
        "Краткая информация о наградах и достижениях", blank=True
    )
    hobbies = models.TextField("Увлечения и интересы", blank=True)

    class Meta:
        verbose_name = "Страница «Обо мне»"
        verbose_name_plural = "Страница «Обо мне»"

    def __str__(self):
        return "Страница «Обо мне»"


class PortfolioPage(SingletonModel):
    """Вводный текст для раздела «Портфолио»."""

    title = models.CharField("Заголовок", max_length=255, default="Портфолио")
    intro = models.TextField(
        "Вводный текст раздела",
        blank=True,
        default="В этом разделе собраны материалы, отражающие мою педагогическую деятельность.",
    )

    class Meta:
        verbose_name = "Страница «Портфолио»"
        verbose_name_plural = "Страница «Портфолио»"

    def __str__(self):
        return "Страница «Портфолио»"


class TeacherAchievement(models.Model):
    """Мои достижения: грамоты, дипломы, сертификаты."""

    title = models.CharField("Название", max_length=255)
    description = models.TextField("Описание", blank=True)
    image = models.ImageField(
        "Изображение (скан грамоты и т.п.)",
        upload_to="achievements/teacher/",
        blank=True,
        null=True,
    )
    file = models.FileField(
        "Файл (полный текст, документ)",
        upload_to="achievements/teacher/files/",
        blank=True,
        null=True,
    )
    year = models.PositiveIntegerField("Год", blank=True, null=True)
    order = models.PositiveIntegerField("Порядок отображения", default=0)

    class Meta:
        verbose_name = "Моё достижение"
        verbose_name_plural = "Мои достижения"
        ordering = ["order", "-year", "-id"]

    def __str__(self):
        return self.title


class StudentAchievement(models.Model):
    """Достижения учащихся."""

    title = models.CharField("Название", max_length=255)
    student_name = models.CharField("Имя учащегося", max_length=255, blank=True)
    description = models.TextField("Описание", blank=True)
    image = models.ImageField("Изображение (скан грамоты и т.п.)", upload_to="achievements/students/")
    year = models.PositiveIntegerField("Год", blank=True, null=True)
    order = models.PositiveIntegerField("Порядок отображения", default=0)

    class Meta:
        verbose_name = "Достижение учащегося"
        verbose_name_plural = "Достижения учащихся"
        ordering = ["order", "-year", "-id"]

    def __str__(self):
        return f"{self.title} ({self.student_name})" if self.student_name else self.title


class MethodicalMaterial(models.Model):
    """Методическая копилка: разработки уроков, презентации и т.д."""

    CATEGORY_CHOICES = [
        ("lesson", "Разработка урока"),
        ("event", "Внеклассное мероприятие"),
        ("presentation", "Презентация"),
        ("article", "Статья / публикация"),
        ("other", "Другое"),
    ]

    title = models.CharField("Название", max_length=255)
    category = models.CharField(
        "Категория", max_length=20, choices=CATEGORY_CHOICES, default="lesson"
    )
    description = models.TextField("Описание", blank=True)
    grade = models.CharField("Класс / параллель", max_length=50, blank=True)
    file = models.FileField(
        "Файл материала", upload_to="methodical/files/", blank=True, null=True
    )
    cover_image = models.ImageField(
        "Изображение-обложка", upload_to="methodical/covers/", blank=True, null=True
    )
    date_added = models.DateField("Дата добавления", auto_now_add=True)
    order = models.PositiveIntegerField("Порядок отображения", default=0)

    class Meta:
        verbose_name = "Методический материал"
        verbose_name_plural = "Методическая копилка"
        ordering = ["order", "-date_added"]

    def __str__(self):
        return self.title


class GalleryPhoto(models.Model):
    """Фотогалерея."""

    image = models.ImageField("Фотография", upload_to="gallery/")
    caption = models.CharField("Подпись", max_length=255, blank=True)
    order = models.PositiveIntegerField("Порядок отображения", default=0)
    uploaded_at = models.DateTimeField("Дата добавления", auto_now_add=True)

    class Meta:
        verbose_name = "Фотография"
        verbose_name_plural = "Фотогалерея"
        ordering = ["order", "-uploaded_at"]

    def __str__(self):
        return self.caption or f"Фото #{self.pk}"
