"""sistema/django_app/config/urls.py: no legacy routes or admin exposure."""
from django.urls import include, path
from corpus import views as corpus_views

urlpatterns = [
    path("corpus/", include("corpus.urls")),
    path("empleados/", corpus_views.portal, name="portal"),
    path("empleados/login/", corpus_views.portal_login, name="portal-login"),
    path("empleados/salir/", corpus_views.portal_logout, name="portal-logout"),
    path("empleados/cuentas/<uuid:account_id>/clave/", corpus_views.portal_reissue,
         name="portal-reissue"),
    path("empleados/cuentas/<uuid:account_id>/eliminar/", corpus_views.portal_delete,
         name="portal-delete"),
]
