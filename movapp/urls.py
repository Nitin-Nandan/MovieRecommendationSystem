from django.urls import path
from . import views, export_views

urlpatterns = [
    path('', views.home, name='home'),
    path('search/', views.search_movies, name='search_movies'),
    path('filter/', views.filter_recommendations, name='filter_recommendations'),
    path('export/csv/', export_views.export_recommendations_csv, name='export_csv'),
    path('export/pdf/', export_views.export_recommendations_pdf, name='export_pdf'),
]
