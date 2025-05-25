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
        self._safe_user_id = None  # Cache for safe user ID
        # TMDB API configuration
        self.tmdb_api_key = "74cdb9b204e5c6f95ffc62fb7ea57b13"  # Your API key
        self.tmdb_base_url = "https://api.themoviedb.org/3"
        self.tmdb_image_base_url = "https://image.tmdb.org/t/p/w500"
        self.setup_session()
        self.load_data()
    
    def setup_session(self):
        """Setup requests session with retry logic"""
        retry_strategy = Retry(
            total=2,
            backoff_factor=0.5,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["HEAD", "GET", "OPTIONS"]
        )
        
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session = requests.Session()
        self.session.mount("https://", adapter)
        self.session.mount("http://", adapter)
        
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'application/json',
            'Accept-Language': 'en-US,en;q=0.9'
        })
    
    def load_data(self):
        """Load movies CSV and SVD model"""
        try:
            base_dir = settings.BASE_DIR
            
            # Load movies CSV
            movies_path = os.path.join(base_dir, 'ml-20m', 'movies.csv')
            self.movies_df = pd.read_csv(movies_path)
            self.movie_titles = self.movies_df['title'].tolist()
            
            print(f"✅ Loaded {len(self.movies_df)} movies")
            
            # Load SVD model
            try:
                model_path = os.path.join(base_dir, 'svd_model.pkl')
                with open(model_path, 'rb') as f:
                    self.svd_model = pickle.load(f)
                print(f"✅ Loaded SVD model successfully")
            except Exception as model_error:
                print(f"⚠️ Could not load SVD model: {model_error}")
                self.svd_model = None
            
        except Exception as e:
            print(f"❌ Error loading data: {e}")
            # Fallback to sample data
            self.movies_df = pd.DataFrame({
                'movieId': [1, 2, 3, 4, 5],
                'title': ['The Shawshank Redemption (1994)', 'The Godfather (1972)', 'The Dark Knight (2008)', 'Pulp Fiction (1994)', 'Forrest Gump (1994)'],
                'genres': ['Drama', 'Crime|Drama', 'Action|Crime|Drama', 'Crime|Drama', 'Comedy|Drama|Romance']
            })
            self.movie_titles = self.movies_df['title'].tolist()
            self.svd_model = None
    
    def get_safe_temp_user_id(self):
        """Get a safe temporary user ID that doesn't exist in the dataset"""
        if self._safe_user_id is None:
            try:
                # Load ratings to find max user ID
                ratings_path = os.path.join(settings.BASE_DIR, 'ml-20m', 'ratings.csv')
                max_user_id = pd.read_csv(ratings_path, usecols=['userId'])['userId'].max()
                self._safe_user_id = max_user_id + 1
                print(f"🔒 Using safe temporary user ID: {self._safe_user_id}")
            except Exception as e:
                print(f"⚠️ Could not determine max user ID: {e}")
                self._safe_user_id = -1  # Fallback to negative ID
        
        return self._safe_user_id
    
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
        
        return f"/static/movapp/images/genre-cards/{selected_card}.svg"
    
    def search_tmdb_movie(self, title, genres=None):
        """Search for movie on TMDB with robust error handling and genre card fallback"""
        try:
            clean_title = self.clean_movie_title(title)
            year = self.extract_movie_year(title)
            
            search_url = f"{self.tmdb_base_url}/search/movie"
            params = {
                'api_key': self.tmdb_api_key,
                'query': clean_title,
                'language': 'en-US'
            }
            
            if year:
                params['year'] = year
            
            response = self.session.get(search_url, params=params, timeout=2)
            
            if response.status_code == 200:
                data = response.json()
                if data['results']:
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
    
    def extract_user_preferences(self, selected_movies):
        """Extract user preferences from selected movies"""
        user_genres = set()
        selected_details = []
        
        print(f"🎭 Analyzing user preferences from: {selected_movies}")
        
        for title in selected_movies:
            details = self.get_movie_details(title)
            if details:
                selected_details.append(details)
                user_genres.update(details['genres'])
        
        print(f"📊 User prefers genres: {list(user_genres)}")
        return {
            'preferred_genres': user_genres,
            'selected_details': selected_details
        }
    
    def find_similar_movies_by_content(self, selected_movies, user_preferences):
        """Find candidate movies similar to selected movies by content"""
        preferred_genres = user_preferences['preferred_genres']
        candidate_movies = []
        
        print(f"🔍 Finding movies similar to user preferences...")
        
        for _, movie in self.movies_df.iterrows():
            # Skip already selected movies
            if movie['title'] in selected_movies:
                continue
                
            movie_genres = set(movie['genres'].split('|')) if pd.notna(movie['genres']) else set()
            
            # Calculate genre similarity
            genre_overlap = len(preferred_genres.intersection(movie_genres))
            
            if genre_overlap > 0:  # Movie has at least one matching genre
                candidate_movies.append({
                    'movieId': movie['movieId'],
                    'title': movie['title'],
                    'genres': list(movie_genres),
                    'genre_similarity': genre_overlap
                })
        
        print(f"📽️ Found {len(candidate_movies)} candidate movies with genre overlap")
        return candidate_movies
    
    def get_enhanced_recommendations(self, selected_movies, num_recommendations=20):
        """Generate personalized recommendations using Hybrid Content-Based + SVD approach"""
        
        if not self.svd_model:
            print("⚠️ SVD model not available, using fallback recommendations")
            return self.get_fallback_recommendations(selected_movies, num_recommendations)
        
        try:
            print(f"🎬 Generating personalized recommendations for: {selected_movies}")
            
            # Step 1: Extract user preferences from selected movies
            user_preferences = self.extract_user_preferences(selected_movies)
            
            if not user_preferences['preferred_genres']:
                print("⚠️ Could not extract user preferences, using fallback")
                return self.get_fallback_recommendations(selected_movies, num_recommendations)
            
            # Step 2: Find candidate movies with similar content
            candidate_movies = self.find_similar_movies_by_content(selected_movies, user_preferences)
            
            if not candidate_movies:
                print("⚠️ No similar movies found, using fallback")
                return self.get_fallback_recommendations(selected_movies, num_recommendations)
            
            # Step 3: Use SVD to predict ratings for candidate movies
            temp_user_id = self.get_safe_temp_user_id()
            svd_predictions = []
            
            print(f"🤖 Using SVD model to predict ratings for {len(candidate_movies)} candidates...")
            
            for movie in candidate_movies:
                try:
                    pred = self.svd_model.predict(temp_user_id, movie['movieId'])
                    
                    # Boost rating based on genre similarity
                    genre_boost = movie['genre_similarity'] * 0.3  # 0.3 points per matching genre
                    adjusted_rating = min(pred.est + genre_boost, 5.0)  # Cap at 5.0
                    
                    svd_predictions.append({
                        'movieId': movie['movieId'],
                        'title': movie['title'],
                        'predicted_rating': round(adjusted_rating, 1),
                        'genres': movie['genres'],
                        'genre_similarity': movie['genre_similarity']
                    })
                except Exception as pred_error:
                    continue
            
            # Step 4: Sort by predicted rating and return top recommendations
            svd_predictions.sort(key=lambda x: x['predicted_rating'], reverse=True)
            top_predictions = svd_predictions[:num_recommendations]
            
            print(f"✨ Generated {len(top_predictions)} personalized recommendations")
            
            # Fetch posters for recommendations
            print("🎨 Fetching movie posters...")
            for i, movie_data in enumerate(top_predictions):
                print(f"📽️ Processing {i+1}/{len(top_predictions)}: {movie_data['title']}")
                movie_data['poster_url'] = self.search_tmdb_movie(movie_data['title'], movie_data['genres'])
                time.sleep(0.1)
            
            print("🎯 Personalized recommendations ready!")
            return top_predictions
            
        except Exception as e:
            print(f"❌ Error generating personalized recommendations: {e}")
            return self.get_fallback_recommendations(selected_movies, num_recommendations)
    
    def get_fallback_recommendations(self, selected_movies, num_recommendations):
        """Fallback recommendations when personalization fails"""
        print("🔄 Using fallback recommendation system")
        
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
        
        for i, rec in enumerate(sample_recommendations[:num_recommendations]):
            rec['poster_url'] = self.search_tmdb_movie(rec['title'], rec['genres'])
        
        return sample_recommendations[:num_recommendations]

# Global instance to be used across views
movie_data_loader = MovieDataLoader()
