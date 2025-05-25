from django.shortcuts import render
from django.http import JsonResponse
from .data_loader import movie_data_loader
import json
from collections import Counter

def analytics_dashboard(request):
    """
    Main analytics dashboard view
    Renders the analytics template with Chart.js integration
    """
    return render(request, 'movapp/analytics.html')

def user_preferences_data(request):
    """
    API endpoint for user preference chart data (Genre Distribution Pie Chart)
    Returns: JSON with genre labels, counts, and Star Wars themed colors
    """
    try:
        # Get selected movies from request parameters
        selected_movies = request.GET.getlist('movies')
        
        if not selected_movies:
            # Return sample data if no movies selected
            return JsonResponse({
                'labels': ['Select movies', 'to see your', 'preference analysis'],
                'data': [1, 1, 1],
                'backgroundColor': ['#667eea', '#764ba2', '#f093fb']
            })
        
        # Extract genres from selected movies using movie data loader
        all_genres = []
        for movie_title in selected_movies:
            movie_details = movie_data_loader.get_movie_details(movie_title)
            if movie_details:
                all_genres.extend(movie_details['genres'])
        
        # Count genre preferences using Counter
        genre_counts = Counter(all_genres)
        
        # Prepare data for Chart.js format
        labels = list(genre_counts.keys())
        data = list(genre_counts.values())
        
        # Star Wars themed color palette
        colors = [
            '#FFD700',  # Gold
            '#FF2E2E',  # Sith Red
            '#667eea',  # Jedi Blue
            '#4ecdc4',  # Teal
            '#ff6b6b',  # Coral
            '#95e1d3',  # Mint
            '#f093fb',  # Pink
            '#fce38a',  # Yellow
            '#a8e6cf',  # Light Green
            '#ff8a80'   # Light Red
        ]
        
        return JsonResponse({
            'labels': labels,
            'data': data,
            'backgroundColor': colors[:len(labels)]
        })
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

def recommendation_insights_data(request):
    """
    API endpoint for recommendation confidence analysis (Bar Chart)
    Categorizes recommendations by confidence level based on predicted ratings
    Returns: JSON with confidence categories and counts
    """
    try:
        selected_movies = request.GET.getlist('movies')
        
        if not selected_movies or len(selected_movies) < 3:
            # Return empty data if insufficient movies selected
            return JsonResponse({
                'labels': ['High Confidence', 'Medium Confidence', 'Exploratory'],
                'data': [0, 0, 0],
                'backgroundColor': ['#28a745', '#ffc107', '#dc3545']
            })
        
        # Generate recommendations using SVD model to analyze confidence
        recommendations = movie_data_loader.get_filtered_recommendations(selected_movies, None, 10)
        
        # Categorize recommendations by confidence level based on predicted rating
        high_confidence = len([r for r in recommendations if r['predicted_rating'] >= 4.0])      # Strong matches
        medium_confidence = len([r for r in recommendations if 3.0 <= r['predicted_rating'] < 4.0])  # Good matches
        exploratory = len([r for r in recommendations if r['predicted_rating'] < 3.0])           # Discovery recommendations
        
        return JsonResponse({
            'labels': ['High Confidence', 'Medium Confidence', 'Exploratory'],
            'data': [high_confidence, medium_confidence, exploratory],
            'backgroundColor': ['#28a745', '#ffc107', '#dc3545']  # Green, Yellow, Red
        })
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

def rating_distribution_data(request):
    """
    Phase 3: API endpoint for rating distribution analysis (Line Chart)
    Shows distribution of predicted ratings across different ranges
    Returns: JSON with rating ranges and movie counts
    """
    try:
        selected_movies = request.GET.getlist('movies')
        
        if not selected_movies or len(selected_movies) < 3:
            # Return empty data if insufficient movies selected
            return JsonResponse({
                'labels': ['1-2 Stars', '2-3 Stars', '3-4 Stars', '4-5 Stars'],
                'data': [0, 0, 0, 0],
                'backgroundColor': ['#dc3545', '#fd7e14', '#ffc107', '#28a745']
            })
        
        # Generate recommendations to analyze rating patterns
        recommendations = movie_data_loader.get_filtered_recommendations(selected_movies, None, 20)
        
        # Categorize recommendations by rating ranges
        rating_1_2 = len([r for r in recommendations if 1.0 <= r['predicted_rating'] < 2.0])  # Poor matches
        rating_2_3 = len([r for r in recommendations if 2.0 <= r['predicted_rating'] < 3.0])  # Below average
        rating_3_4 = len([r for r in recommendations if 3.0 <= r['predicted_rating'] < 4.0])  # Good matches
        rating_4_5 = len([r for r in recommendations if 4.0 <= r['predicted_rating'] <= 5.0]) # Excellent matches
        
        return JsonResponse({
            'labels': ['1-2 Stars', '2-3 Stars', '3-4 Stars', '4-5 Stars'],
            'data': [rating_1_2, rating_2_3, rating_3_4, rating_4_5],
            'backgroundColor': ['#dc3545', '#fd7e14', '#ffc107', '#28a745']  # Red to Green gradient
        })
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

def movie_era_data(request):
    """
    Phase 3: API endpoint for movie era preferences analysis (Polar Area Chart)
    Analyzes user's selected movies by decade to show era preferences
    Returns: JSON with decade labels and movie counts
    """
    try:
        selected_movies = request.GET.getlist('movies')
        
        if not selected_movies:
            # Return empty data if no movies selected
            return JsonResponse({
                'labels': ['1970s', '1980s', '1990s', '2000s', '2010s', '2020s'],
                'data': [0, 0, 0, 0, 0, 0],
                'backgroundColor': ['#667eea', '#764ba2', '#f093fb', '#53a0fd', '#4ecdc4', '#45b7d1']
            })
        
        # Initialize decade counters
        decade_counts = {'1970s': 0, '1980s': 0, '1990s': 0, '2000s': 0, '2010s': 0, '2020s': 0}
        
        # Analyze selected movies by extracting year from title and categorizing by decade
        for movie_title in selected_movies:
            movie_details = movie_data_loader.get_movie_details(movie_title)
            if movie_details:
                # Extract year from movie title using regex (format: "Movie Title (YYYY)")
                import re
                year_match = re.search(r'\((\d{4})\)', movie_title)
                if year_match:
                    year = int(year_match.group(1))
                    
                    # Categorize by decade
                    if 1970 <= year < 1980:
                        decade_counts['1970s'] += 1
                    elif 1980 <= year < 1990:
                        decade_counts['1980s'] += 1
                    elif 1990 <= year < 2000:
                        decade_counts['1990s'] += 1
                    elif 2000 <= year < 2010:
                        decade_counts['2000s'] += 1
                    elif 2010 <= year < 2020:
                        decade_counts['2010s'] += 1
                    elif 2020 <= year < 2030:
                        decade_counts['2020s'] += 1
        
        return JsonResponse({
            'labels': list(decade_counts.keys()),
            'data': list(decade_counts.values()),
            'backgroundColor': ['#667eea', '#764ba2', '#f093fb', '#53a0fd', '#4ecdc4', '#45b7d1']  # Star Wars themed colors
        })
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
