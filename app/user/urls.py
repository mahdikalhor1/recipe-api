from django.urls import path
from . import views

app_name='user'

urlpatterns=(
    path('create/', views.CreateUserApi.as_view(), name='create'),
    path('token/',views.CreateAuthTokenApi.as_view(), name='token'),
    path('myaccount/', views.ManageUserApi.as_view(), name='myaccount'),
)