from .models import SiteSettings


def site_settings(request):
    """Делает настройки сайта доступными во всех шаблонах."""
    return {"site_settings": SiteSettings.load()}
