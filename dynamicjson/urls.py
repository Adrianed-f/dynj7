from django.urls import path

from . import views

app_name = "dynamicjson"

urlpatterns = [
    path("", views.submit, name="submit"),
    path("result/<int:pk>/", views.result, name="result"),
]

