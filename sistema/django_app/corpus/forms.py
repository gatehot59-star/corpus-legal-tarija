"""sistema/django_app/corpus/forms.py: strict form inputs and private reset."""
from django import forms
from django.conf import settings
from django.contrib.auth.forms import PasswordResetForm
from django.core.mail import send_mail
from .access import CorpusError
from contracts.corpus_django import ErrorCode


def strict(data, allowed: set[str]) -> None:
    """Reject duplicates/unknown fields rather than pick an ambiguous value."""
    if set(data) - allowed or any(len(data.getlist(k)) != 1 for k in data):
        raise CorpusError(ErrorCode.INVALID_INPUT)


class QueryForm(forms.Form):
    """Bound query length, byte count and canonical pagination."""
    q = forms.CharField(min_length=1, max_length=128)
    offset = forms.RegexField(r"^(0|[1-9][0-9]{0,4})$", initial="0", required=False)
    limit = forms.RegexField(r"^([1-9]|1[0-9]|20)$", initial="10", required=False)

    def clean_q(self) -> str:
        """Reject multibyte queries above the documented byte budget."""
        q = self.cleaned_data["q"]
        if len(q.encode()) > 256:
            raise forms.ValidationError("Consulta demasiado larga.")
        return q


class BrowseForm(forms.Form):
    """Bound source, matter and norm-type filters for catalog navigation."""
    browse = forms.CharField(max_length=1, initial="1")
    source = forms.CharField(max_length=80, required=False)
    rubro = forms.CharField(max_length=120, required=False)
    tipo = forms.CharField(max_length=120, required=False)
    offset = forms.RegexField(r"^(0|[1-9][0-9]{0,4})$", initial="0", required=False)
    limit = forms.RegexField(r"^([1-9]|[1-4][0-9]|50)$", initial="20", required=False)


class PrivateResetForm(PasswordResetForm):
    """Use Django tokens; fixed origin, no external templates or real email here."""
    def send_mail(self, subject_template_name, email_template_name, context,
                  from_email, to_email, html_email_template_name=None) -> None:
        """Deliver through configured backend only; tests capture in memory."""
        link = f'{settings.CORPUS_ORIGIN}/corpus/reset/{context["uid"]}/{context["token"]}/'
        send_mail("Recuperación de Corpus", f"Restablecé tu contraseña: {link}",
                  from_email, [to_email], fail_silently=False)
