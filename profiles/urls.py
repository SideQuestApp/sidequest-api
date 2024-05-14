from django.urls import path, include
from profiles import views


urlpatterns = [
    path('register/', view=views.RegisterView.as_view(), name='register'),
    path('hello/', views.TestApiEndpoint.as_view()),
    path('o/', include('oauth2_provider.urls', namespace='oauth2_provider')),
]
