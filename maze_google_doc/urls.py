"""maze_google_doc URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf.urls import url
from django.contrib import admin
from django.urls import path
from rest_framework.authtoken.views import ObtainAuthToken

from apps.google_doc.views import NewDocView, CopyDocView

urlpatterns = [
    path('admin/', admin.site.urls),
    url(r'^api/v1/new_doc/?$', NewDocView.as_view()),
    url(r'^api/v1/copy_doc/?$', CopyDocView.as_view()),
    # curl -H "Content-Type: application/json" --request POST "http://127.0.0.1:8000/api/v1/login/"
    # -d '{"username": "xxx", "password": "xxx"}'
    # 返回形如 {"token":"28f26466c6e541e83b3597060961f25aeef182c3"}
    url(r'^api/v1/login/?', ObtainAuthToken.as_view()),
]
