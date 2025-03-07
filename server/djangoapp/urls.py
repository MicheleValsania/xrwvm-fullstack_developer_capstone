# Django imports
from django.urls import path
from django.conf.urls.static import static
from django.conf import settings
from . import views

app_name = 'djangoapp'
urlpatterns = [
    path(route='login', view=views.login_user, name='login'),
    # path for home page
    path('', views.index, name='index'),
    path(route='get_cars', view=views.get_cars, name ='getcars'),
    # path for logout
    path('logout/', views.logout_user, name='logout'),
    path('register', views.registration, name='register'),
]

# Add URL patterns for serving static files
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
