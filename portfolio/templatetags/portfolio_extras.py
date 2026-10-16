from django import template

register = template.Library()

PREVIEWABLE_EXTENSIONS = {"pdf", "doc", "docx"}


@register.filter
def file_ext(file_field):
    """Возвращает расширение файла в нижнем регистре без точки."""
    if not file_field:
        return ""
    name = getattr(file_field, "name", "") or ""
    if "." not in name:
        return ""
    return name.rsplit(".", 1)[-1].lower()


@register.filter
def is_previewable(file_field):
    """True, если файл можно открыть во встроенном просмотрщике (PDF/DOC/DOCX)."""
    return file_ext(file_field) in PREVIEWABLE_EXTENSIONS
