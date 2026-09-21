# sistema/django_app/Dockerfile: reproducible non-root synthetic build, no deploy.
FROM python:3.12-slim-bookworm@sha256:392307d22300de8b5986851a12d9176dfc0fc073e65bf6523ebd7dcbeb23564e AS dependencies
RUN python -m venv /opt/venv
COPY sistema/django_app/requirements.txt /tmp/requirements.txt
RUN /opt/venv/bin/pip install --no-cache-dir -r /tmp/requirements.txt

FROM python:3.12-slim-bookworm@sha256:392307d22300de8b5986851a12d9176dfc0fc073e65bf6523ebd7dcbeb23564e
COPY --from=dependencies /opt/venv /opt/venv
RUN groupadd --gid 10001 corpus && useradd --uid 10001 --gid 10001 --no-create-home corpus && mkdir /data && chown 10001:10001 /data
WORKDIR /app/sistema/django_app
COPY sistema/django_app /app/sistema/django_app
COPY contracts/corpus_django.py /app/contracts/corpus_django.py
COPY sistema/api/version_text.py /app/sistema/api/version_text.py
ENV PATH="/opt/venv/bin:$PATH" PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 CORPUS_DB=/data/runtime.sqlite3
USER 10001:10001
EXPOSE 8000
HEALTHCHECK --interval=30s --timeout=3s --start-period=10s CMD python -c "import os,urllib.request; r=urllib.request.Request('http://127.0.0.1:8000/corpus/live/',headers={'Host':os.environ.get('CORPUS_HOSTS','localhost').split(',')[0]}); urllib.request.urlopen(r,timeout=2).read()"
CMD ["gunicorn","config.wsgi:application","--bind","0.0.0.0:8000","--workers","2","--timeout","30","--limit-request-line","2048","--error-logfile","-"]
