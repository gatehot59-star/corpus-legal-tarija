"""sistema/django_app/config/urls.py: no legacy routes or admin exposure."""
from django.urls import include, path
from corpus import employee_portal

urlpatterns = [
    path("corpus/", include("corpus.urls")),
    path("empleados/", employee_portal.portal, name="portal"),
    path("empleados/login/", employee_portal.portal_login, name="portal-login"),
    path("empleados/salir/", employee_portal.portal_logout, name="portal-logout"),
    path("empleados/cuentas/<str:role>/<uuid:account_id>/clave/", employee_portal.portal_reissue,
         name="portal-reissue"),
    path("empleados/cuentas/<str:role>/<uuid:account_id>/eliminar/", employee_portal.portal_delete,
         name="portal-delete"),
]
