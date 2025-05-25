import pandas as pd
import pickle
import os
import numpy as np
import requests
from urllib3.util.retry import Retry
from requests.adapters import HTTPAdapter
import time
import random
from django.conf import settings

class MovieDataLoader:
    def __init__(self):
        self.movies_df = None
        self.svd_model = None
        self.movie_titles = []
        # TMDB API configuration
        self.tmdb_api_key = "74cdb9b204e5c6f95ffc62fb7ea57b13"  # Your API key
        self.tmdb_base_url = "https://api.themoviedb.org/3"
        self.tmdb_image_base_url = "https://image.tmdb.org/t/p/w500"
        self.setup_session()
        self.load_data()
    
    def setup_session(self):
        """Setup requests session with retry logic"""
        retry_strategy = Retry(
            total=2,  # Only 2 retries to avoid long waits
            backoff_factor=0.5,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["HEAD", "GET", "OPTIONS"]
        )
        
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session = requests.Session()
        self.session.mount("https://", adapter)
        self.session.mount("http://", adapter)
        
        # Set headers to avoid blocking
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'application/json',
            'Accept-Language': 'en-US,en;q=0.9'
        })
    
    def load_data(self):
        """Load movies CSV and SVD model"""
        try:
            # Get the base directory (project root)
            base_dir = settings.BASE_DIR
            
            # Load movies CSV
            movies_path = os.path.join(base_dir, 'ml-20m', 'movies.csv')
            self.movies_df = pd.read_csv(movies_path)
            
            # Create a list of movie titles for search
            self.movie_titles = self.movies_df['title'].tolist()
            
            print(f"✅ Loaded {len(self.movies_df)} movies")
            
            # Try to load SVD model
            try:
                model_path = os.path.join(base_dir, 'svd_model.pkl')
                with open(model_path, 'rb') as f:
                    self.svd_model = pickle.load(f)
                print(f"✅ Loaded SVD model successfully")
            except Exception as model_error:
                print(f"⚠️ Could not load SVD model: {model_error}")
                print("📝 Using fallback recommendation system")
                self.svd_model = None
            
        except Exception as e:
            print(f"❌ Error loading data: {e}")
            # Fallback to sample data for development
            self.movies_df = pd.DataFrame({
                'movieId': [1, 2, 3, 4, 5],
                'title': ['The Shawshank Redemption (1994)', 'The Godfather (1972)', 'The Dark Knight (2008)', 'Pulp Fiction (1994)', 'Forrest Gump (1994)'],
                'genres': ['Drama', 'Crime|Drama', 'Action|Crime|Drama', 'Crime|Drama', 'Comedy|Drama|Romance']
            })
            self.movie_titles = self.movies_df['title'].tolist()
            self.svd_model = None
    
    def extract_movie_year(self, title):
        """Extract year from movie title like 'Movie Name (1994)'"""
        import re
        match = re.search(r'\((\d{4})\)', title)
        return match.group(1) if match else None
    
    def clean_movie_title(self, title):
        """Remove year from title for TMDB search"""
        import re
        return re.sub(r'\s*\(\d{4}\)', '', title).strip()
    
    def create_genre_card_placeholder(self, title, genres):
        """Create a genre-themed illustrated card for movies without posters"""
        
        # Genre to card mapping
        genre_mapping = {
            'action': ['Action', 'Adventure', 'Thriller'],
            'romance': ['Romance', 'Romantic'],
            'sci-fi': ['Sci-Fi', 'Science Fiction', 'Sci-fi'],
            'comedy': ['Comedy', 'Humor'],
            'fantasy': ['Fantasy', 'Magic', 'Fairy Tale'],
            'horror': ['Horror', 'Scary'],
            'drama': ['Drama'],
            'crime': ['Crime', 'Mystery', 'Detective'],
            'animation': ['Animation', 'Animated'],
            'documentary': ['Documentary'],
            'family': ['Family', 'Children'],
            'musical': ['Musical', 'Music'],
            'war': ['War', 'Military'],
            'western': ['Western'],
            'sport': ['Sport', 'Sports'],
            'biography': ['Biography', 'Biographical']
        }
        
        # Find the best matching genre
        selected_card = 'default'
        
        if genres and len(genres) > 0:
            for genre in genres:
                genre_lower = genre.lower()
                for card_type, genre_list in genre_mapping.items():
                    if any(g.lower() in genre_lower or genre_lower in g.lower() for g in genre_list):
                        selected_card = card_type
                        break
                if selected_card != 'default':
                    break
        
        # Return the static file URL for the genre card
        return f"/static/movapp/images/genre-cards/{selected_card}.svg"
    
    def search_tmdb_movie(self, title, genres=None):
        """Search for movie on TMDB with robust error handling and genre card fallback"""
        try:
            # Clean the title for better search results
            clean_title = self.clean_movie_title(title)
            year = self.extract_movie_year(title)
            
            # TMDB search endpoint
            search_url = f"{self.tmdb_base_url}/search/movie"
            params = {
                'api_key': self.tmdb_api_key,
                'query': clean_title,
                'language': 'en-US'
            }
            
            # Add year to search if available
            if year:
                params['year'] = year
            
            # Make request with timeout
            response = self.session.get(search_url, params=params, timeout=2)
            
            if response.status_code == 200:
                data = response.json()
                if data['results']:
                    # Get the first (most relevant) result
                    movie = data['results'][0]
                    poster_path = movie.get('poster_path')
                    
                    if poster_path:
                        return f"{self.tmdb_image_base_url}{poster_path}"
                        
        except requests.exceptions.ConnectionError:
            print(f"🎨 Connection issue for '{title}' - Using genre card")
        except requests.exceptions.Timeout:
            print(f"🎨 Timeout for '{title}' - Using genre card")
        except requests.exceptions.RequestException:
            print(f"🎨 Request issue for '{title}' - Using genre card")
        except Exception:
            print(f"🎨 Error for '{title}' - Using genre card")
        
        # Return genre-specific card for any error
        return self.create_genre_card_placeholder(title, genres)
    
    def search_movies(self, query, limit=10):
        """Search for movies by title"""
        if not query or len(query) < 2:
            return []
        
        query = query.lower()
        matches = []
        
        for title in self.movie_titles:
            if query in title.lower():
                matches.append(title)
                if len(matches) >= limit:
                    break
        
        return matches
    
    def get_movie_details(self, title):
        """Get movie details including ID and genres"""
        movie_row = self.movies_df[self.movies_df['title'] == title]
        if not movie_row.empty:
            movie = movie_row.iloc[0]
            return {
                'movieId': movie['movieId'],
                'title': movie['title'],
                'genres': movie['genres'].split('|') if pd.notna(movie['genres']) else ['Unknown']
            }
        return None
    
    def get_movie_id(self, title):
        """Get movie ID from title"""
        movie_details = self.get_movie_details(title)
        return movie_details['movieId'] if movie_details else None
    
    def get_enhanced_recommendations(self, selected_movies, num_recommendations=20):
        """Generate enhanced recommendations with ratings, genres, and posters/genre cards"""
        if not self.svd_model:
            # Return enhanced sample recommendations if model not loaded
            sample_recommendations = [
                {'title': 'The Shawshank Redemption (1994)', 'predicted_rating': 4.8, 'genres': ['Drama']},
                {'title': 'The Godfather (1972)', 'predicted_rating': 4.7, 'genres': ['Crime', 'Drama']},
                {'title': 'The Dark Knight (2008)', 'predicted_rating': 4.6, 'genres': ['Action', 'Crime', 'Drama']},
                {'title': 'Pulp Fiction (1994)', 'predicted_rating': 4.5, 'genres': ['Crime', 'Drama']},
                {'title': 'Forrest Gump (1994)', 'predicted_rating': 4.4, 'genres': ['Comedy', 'Drama', 'Romance']},
                {'title': 'Inception (2010)', 'predicted_rating': 4.3, 'genres': ['Action', 'Sci-Fi', 'Thriller']},
                {'title': 'The Matrix (1999)', 'predicted_rating': 4.2, 'genres': ['Action', 'Sci-Fi']},
                {'title': 'Goodfellas (1990)', 'predicted_rating': 4.1, 'genres': ['Biography', 'Crime', 'Drama']},
                {'title': 'The Lord of the Rings: The Return of the King (2003)', 'predicted_rating': 4.0, 'genres': ['Adventure', 'Drama', 'Fantasy']},
                {'title': 'Star Wars: Episode IV - A New Hope (1977)', 'predicted_rating': 3.9, 'genres': ['Action', 'Adventure', 'Fantasy']}
            ]
            
            print("🎬 Fetching movie posters (with genre card protection)...")
            for i, rec in enumerate(sample_recommendations[:num_recommendations]):
                print(f"📽️ Processing {i+1}/{min(num_recommendations, len(sample_recommendations))}: {rec['title']}")
                rec['poster_url'] = self.search_tmdb_movie(rec['title'], rec['genres'])
                time.sleep(0.1)  # Small delay to avoid overwhelming TMDB
            
            return sample_recommendations[:num_recommendations]
        
        try:
            # Get movie IDs for selected movies
            selected_movie_ids = []
            for title in selected_movies:
                movie_id = self.get_movie_id(title)
                if movie_id:
                    selected_movie_ids.append(movie_id)
            
            if not selected_movie_ids:
                return []
            
            # Create a temporary user ID that doesn't exist in the dataset
            temp_user_id = 999999
            
            # Get all movie IDs
            all_movie_ids = self.movies_df['movieId'].unique()
            
            print("🤖 Generating recommendations with SVD model...")
            
            # Predict ratings for all movies for this temporary user
            predictions = []
            for movie_id in all_movie_ids:
                if movie_id not in selected_movie_ids:  # Don't recommend already selected movies
                    try:
                        pred = self.svd_model.predict(temp_user_id, movie_id)
                        
                        # Get movie details
                        movie_row = self.movies_df[self.movies_df['movieId'] == movie_id]
                        if not movie_row.empty:
                            movie = movie_row.iloc[0]
                            movie_data = {
                                'movieId': movie_id,
                                'title': movie['title'],
                                'predicted_rating': round(pred.est, 1),
                                'genres': movie['genres'].split('|') if pd.notna(movie['genres']) else ['Unknown']
                            }
                            predictions.append(movie_data)
                    except Exception as pred_error:
                        continue
            
            # Sort by predicted rating and get top recommendations
            predictions.sort(key=lambda x: x['predicted_rating'], reverse=True)
            top_predictions = predictions[:num_recommendations]
            
            print("🎬 Fetching movie posters (with genre card protection)...")
            
            # Fetch posters for top recommendations with progress indication
            for i, movie_data in enumerate(top_predictions):
                print(f"📽️ Processing {i+1}/{len(top_predictions)}: {movie_data['title']}")
                movie_data['poster_url'] = self.search_tmdb_movie(movie_data['title'], movie_data['genres'])
                time.sleep(0.1)  # Small delay to avoid overwhelming TMDB
            
            print("✅ Recommendations ready!")
            return top_predictions
            
        except Exception as e:
            print(f"Error generating enhanced recommendations: {e}")
            # Return sample recommendations as fallback
            return self.get_enhanced_recommendations(selected_movies, num_recommendations)

# Global instance to be used across views
movie_data_loader = MovieDataLoader()
