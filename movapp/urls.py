from django.urls import path
from . import views, export_views, analytics_views


urlpatterns = [
    path('', views.home, name='home'),
    path('search/', views.search_movies, name='search_movies'),
    path('filter/', views.filter_recommendations, name='filter_recommendations'),
    
    # Infinite scroll endpoint for loading more recommendations
    path('load-more/', views.load_more_recommendations, name='load_more_recommendations'),
    
    # NEW: Lazy poster loading endpoint for performance optimization
    path('get-poster/', views.get_movie_poster, name='get_movie_poster'),
    
    # Export endpoints
    path('export/csv/', export_views.export_recommendations_csv, name='export_csv'),
    path('export/pdf/', export_views.export_recommendations_pdf, name='export_pdf'),
    
    # Analytics endpoints
    path('analytics/', analytics_views.analytics_dashboard, name='analytics'),
    path('api/user-preferences/', analytics_views.user_preferences_data, name='user_preferences_data'),
    path('api/recommendation-insights/', analytics_views.recommendation_insights_data, name='recommendation_insights_data'),
    path('api/rating-distribution/', analytics_views.rating_distribution_data, name='rating_distribution_data'),
    path('api/movie-era/', analytics_views.movie_era_data, name='movie_era_data'),
]
