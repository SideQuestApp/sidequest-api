from django.contrib import admin
from django.urls import path, include
from profiles import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('register/', view=views.RegisterView.as_view(), name='register'),
    path('api-auth/', include('rest_framework.urls')),  # ! For testing purposes
    path('o/', include('oauth2_provider.urls', namespace='oauth2_provider')),
    path('api/hello', views.TestApiEndpoint.as_view()),
]
