from django.urls import path
from .views import signup, login_user, google_login
from . import views

urlpatterns = [
    path('signup/', signup),
    path('login/', login_user),
    path("google/", google_login),
    path("profile/", views.profile_view, name = "api-profile"),
]
