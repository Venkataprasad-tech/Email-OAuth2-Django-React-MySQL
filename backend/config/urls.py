from django.http import JsonResponse
from django.contrib import admin
from django.urls import path, include
from accounts import views as account_views


def home(request):
    return JsonResponse({"status": "Backend running"})


urlpatterns = [
    path('admin/', admin.site.urls),
    path("", home),
    path("api/accounts/get-csrf/", account_views.get_csrf, name="get-csrf"),
    path('api/accounts/', include('accounts.urls')),
]
