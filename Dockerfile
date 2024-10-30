FROM python:3.11-slim-buster
LABEL authors="Viktor"


WORKDIR /home/app
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1

COPY requirements.txt ./
RUN pip install -r requirements.txt

COPY . .
RUN python manage.py collectstatic --noinput

EXPOSE 8000
#CMD ["gunicorn", "--bind", "0.0.0.0:8000", "base.wsgi:application"]
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
