from django.urls import path

from . import views

urlpatterns = [
    path("", views.editor, name="editor"),
    path("voix/", views.voice, name="voice"),
    path("api/", views.api, name="api"),
    path("synthesize/", views.synthesize, name="synthesize"),
]
