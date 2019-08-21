from django.contrib import admin
from django.urls import path, include
from crud import urls as crud_url

urlpatterns = [
    path('admin/', admin.site.urls),
    path('webhook/', include(crud_url)),
]

# 'webhook/' 으로 들어온 POST request를 crud앱으로 보내겠습니다.