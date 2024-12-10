from django.urls import path
from . import views

urlpatterns = [
    path('init_catalog/', views.init_catalog),
    path('process_order/', views.process_order),
    path('process_restock/', views.process_restock),
]