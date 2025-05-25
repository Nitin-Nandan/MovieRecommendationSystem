from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from .data_loader import movie_data_loader

def home(request):
    """Homepage view for the Movie Recommendation System"""
    if request.method == 'POST':
        try:
            # Get selected movies from form
            selected_movies = request.POST.getlist('selected_movies')
            
            if len(selected_movies) < 3:
                return render(request, 'movapp/home.html', {
                    'error': 'Please select at least 3 movies to get recommendations.'
                })
            
            # Get filter parameters from form
            filters = {
                'genres': request.POST.getlist('genres'),
                'year_min': request.POST.get('year_min'),
                'year_max': request.POST.get('year_max'),
                'min_rating': request.POST.get('min_rating'),
                'sort_by': request.POST.get('sort_by', 'rating')
            }
            
            # Clean empty values
            filters = {k: v for k, v in filters.items() if v and v != '0'}
            
            print(f"🔧 Received filters: {filters}")
            
            # Generate filtered recommendations (20 total, show 10 initially)
            all_recommendations = movie_data_loader.get_filtered_recommendations(
                selected_movies, filters, 20
            )
            
            # Split into initial and additional recommendations
            initial_recommendations = all_recommendations[:10]
            additional_recommendations = all_recommendations[10:20]
            
            return render(request, 'movapp/results.html', {
                'selected_movies': selected_movies,
                'recommendations': initial_recommendations,
                'additional_recommendations': additional_recommendations,
                'has_more': len(additional_recommendations) > 0,
                'applied_filters': filters
            })
            
        except Exception as e:
            return render(request, 'movapp/home.html', {
                'error': f'An error occurred: {str(e)}'
            })
    
    return render(request, 'movapp/home.html')

def search_movies(request):
    """AJAX endpoint for movie search with filter support"""
    query = request.GET.get('q', '')
    
    if len(query) < 2:
        return JsonResponse({'movies': []})
    
    # Get filter parameters from request
    filters = {
        'genres': request.GET.getlist('genres'),
        'year_min': request.GET.get('year_min'),
        'year_max': request.GET.get('year_max'),
        'min_rating': request.GET.get('min_rating')
    }
    
    # Clean empty values
    filters = {k: v for k, v in filters.items() if v and v != '0'}
    
    matches = movie_data_loader.search_movies(query, filters, limit=10)
    
    return JsonResponse({'movies': matches})

def filter_recommendations(request):
    """AJAX endpoint for live filtering of recommendations"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            selected_movies = data.get('selected_movies', [])
            filters = data.get('filters', {})
            
            if len(selected_movies) < 3:
                return JsonResponse({
                    'success': False,
                    'error': 'Please select at least 3 movies'
                })
            
            # Generate filtered recommendations
            recommendations = movie_data_loader.get_filtered_recommendations(
                selected_movies, filters, 10
            )
            
            return JsonResponse({
                'success': True,
                'recommendations': recommendations,
                'count': len(recommendations)
            })
            
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            })
    
    return JsonResponse({'success': False, 'error': 'Invalid request method'})
