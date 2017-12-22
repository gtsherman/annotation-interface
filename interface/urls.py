from django.urls import include, path
from django.contrib import admin

urlpatterns = [
    path('interface/', include('topicterms.urls')),
    path('admin/', admin.site.urls),
    path('accounts/', include('django.contrib.auth.urls'))
]
