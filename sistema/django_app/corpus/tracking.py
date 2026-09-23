"""sistema/django_app/corpus/tracking.py: server-side pilot usage telemetry."""
from .models import PilotAccount, PilotEvent, Membership
from .access import EMPLOYEES_GROUP
from contracts.corpus_django import Principal

IGNORED_PREFIXES = ("/corpus/live/", "/corpus/ready/", "/corpus/health/", "/corpus/theme/",
                    "/corpus/logout/", "/corpus/reset", "/corpus/piloto/")
EMPLOYEE_PORTAL_LINK = b'<a class="button secondary" href="/empleados/">Panel de empleados</a>'


def classify(request):
    """Map an eligible request to a human-readable section; None means not tracked."""
    path = request.path
    if request.method == "POST":
        if path == "/corpus/login/":
            return "Ingreso", ""
        if path == "/corpus/feedback/":
            return "Informe de problema", request.POST.get("category", "")
        if path == "/corpus/save/":
            return "Referencia guardada", request.POST.get("uid", "")
        return None, ""
    if path == "/corpus/read/":
        return "Lectura de documento", request.GET.get("uid", "")
    if path == "/corpus/":
        if request.GET.get("q"):
            return "Búsqueda", request.GET.get("q", "")
        if "browse" in request.GET:
            filters = [request.GET.get("source", ""), request.GET.get("rubro", ""),
                       request.GET.get("tipo", "")]
            return "Catálogo", " · ".join(part for part in filters if part)
        return "Inicio", ""
    return None, ""


class PilotTrackingMiddleware:
    """Record pilot usage and route the shared login by the authenticated role."""

    def __init__(self, get_response) -> None:
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        try:
            self._route_shared_login(request, response)
            self._hide_employee_portal_link(response)
            self._record(request, response)
        except Exception:
            pass  # Telemetry and presentation cleanup never break the product.
        return response

    @staticmethod
    def _route_shared_login(request, response) -> None:
        """Send authenticated employees to the panel while lawyers go to Corpus."""
        if (request.path == "/corpus/login/" and request.method == "POST"
                and response.status_code == 302 and getattr(request.user, "is_authenticated", False)):
            enabled = Membership.objects.filter(
                user_id=request.user.pk, enabled=True, group__name=EMPLOYEES_GROUP).exists()
            if enabled and not PilotAccount.objects.filter(lawyer_id=request.user.pk).exists():
                response["Location"] = "/empleados/"

    @staticmethod
    def _hide_employee_portal_link(response) -> None:
        """Remove the employee-portal affordance from Corpus HTML, never from its own portal."""
        content_type = response.get("Content-Type", "")
        if (response.status_code < 400 and content_type.startswith("text/html")
                and hasattr(response, "content")):
            response.content = response.content.replace(EMPLOYEE_PORTAL_LINK, b"")

    def _record(self, request, response) -> None:
        user = getattr(request, "user", None)
        if user is None or not user.is_authenticated or response.status_code >= 400:
            return
        if not request.path.startswith("/corpus/"):
            return
        if any(request.path.startswith(prefix) for prefix in IGNORED_PREFIXES):
            return
        if request.path == "/corpus/login/" and response.status_code != 302:
            return
        if not PilotAccount.objects.filter(lawyer_id=user.pk).exists():
            return
        section, detail = classify(request)
        if section is None:
            return
        PilotEvent.objects.create(lawyer=user, section=section[:40],
                                  detail=detail[:240], path=request.path[:240])
