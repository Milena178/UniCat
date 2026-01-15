from django import template
from django.utils import timezone

register = template.Library()

@register.simple_tag
def countdown_js(produkt):
    """Generiert JavaScript für Live-Countdown"""
    if not produkt.auktion_aktiv():
        return ""

    ende = produkt.auktion_ende()
    ende_timestamp = int(ende.timestamp() * 1000)  # Millisekunden für JS

    return ende_timestamp


@register.filter
def format_countdown(produkt):
    """Formatiert verbleibende Zeit als Text"""
    if not produkt.auktion_aktiv():
        return "Auktion beendet"

    delta = produkt.auktion_ende() - timezone.now()

    days = delta.days
    hours = delta.seconds // 3600
    minutes = (delta.seconds % 3600) // 60

    parts = []
    if days > 0:
        parts.append(f"{days}T")
    if hours > 0 or days > 0:
        parts.append(f"{hours}h")
    parts.append(f"{minutes}min")

    return " ".join(parts)