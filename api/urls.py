from django.urls import path

from api import views

urlpatterns = [
    path("ping/", views.ping, name="ping"),
    path("email/process/", views.process_email, name="process-email"),
]
