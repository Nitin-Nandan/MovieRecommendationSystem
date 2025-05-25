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
        self.tmdb_api_key = "74cdb9b204e5c6f95ffc62fb7ea57b13"  # Replace with your actual API key
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
    
    def create_glitch_placeholder(self, title):
        """Create a glitched data URL placeholder for movies without posters"""
        clean_title = self.clean_movie_title(title)
        year = self.extract_movie_year(title) or "????"
        
        # Random glitch messages
        glitch_messages = [
            "POSTER CORRUPTED",
            "SIGNAL LOST",
            "DATA BREACH",
            "MEMORY ERROR",
            "FRAME DAMAGED",
            "TRANSMISSION FAILED",
            "DIGITAL GHOST",
            "PIXEL DECAY"
        ]
        
        # Random glitch colors for Star Wars theme
        glitch_colors = [
            "ff0040,00ff40,4000ff",  # RGB split
            "ff4040,40ff40,4040ff",  # Lighter RGB
            "dc143c,00ff00,0080ff",  # Sith red, green, blue
            "ff6b6b,4ecdc4,45b7d1"   # Soft glitch colors
        ]
        
        message = random.choice(glitch_messages)
        colors = random.choice(glitch_colors).split(',')
        
        # Create a data URL with SVG glitch effect
        svg_content = f'''
        <svg width="500" height="750" xmlns="http://www.w3.org/2000/svg">
            <defs>
                <filter id="glitch">
                    <feColorMatrix type="matrix" values="1 0 0 0 0  0 0 0 0 0  0 0 0 0 0  0 0 0 1 0"/>
                    <feOffset dx="2" dy="1" result="r"/>
                    <feColorMatrix type="matrix" values="0 0 0 0 0  0 1 0 0 0  0 0 0 0 0  0 0 0 1 0" in="SourceGraphic" result="g"/>
                    <feOffset dx="-1" dy="2" result="g"/>
                    <feColorMatrix type="matrix" values="0 0 0 0 0  0 0 0 0 0  0 0 1 0 0  0 0 0 1 0" in="SourceGraphic" result="b"/>
                    <feOffset dx="1" dy="-1" result="b"/>
                    <feBlend mode="screen" in="r" in2="g" result="rg"/>
                    <feBlend mode="screen" in="rg" in2="b"/>
                </filter>
                <pattern id="noise" patternUnits="userSpaceOnUse" width="100" height="100">
                    <rect width="100" height="100" fill="#{colors[0]}20"/>
                    <rect x="20" y="10" width="60" height="5" fill="#{colors[1]}40"/>
                    <rect x="10" y="40" width="80" height="3" fill="#{colors[2]}30"/>
                    <rect x="30" y="70" width="40" height="4" fill="#{colors[0]}50"/>
                </pattern>
            </defs>
            
            <!-- Background -->
            <rect width="500" height="750" fill="url(#noise)"/>
            <rect width="500" height="750" fill="#1a1a1a" opacity="0.8"/>
            
            <!-- Glitch bars -->
            <rect x="0" y="100" width="500" height="8" fill="#{colors[0]}" opacity="0.7"/>
            <rect x="0" y="200" width="500" height="12" fill="#{colors[1]}" opacity="0.6"/>
            <rect x="0" y="350" width="500" height="6" fill="#{colors[2]}" opacity="0.8"/>
            <rect x="0" y="500" width="500" height="10" fill="#{colors[0]}" opacity="0.5"/>
            <rect x="0" y="650" width="500" height="7" fill="#{colors[1]}" opacity="0.7"/>
            
            <!-- Movie reel icon -->
            <circle cx="250" cy="200" r="40" fill="none" stroke="#{colors[2]}" stroke-width="3" opacity="0.6"/>
            <circle cx="235" cy="185" r="8" fill="#{colors[2]}" opacity="0.6"/>
            <circle cx="265" cy="185" r="8" fill="#{colors[2]}" opacity="0.6"/>
            <circle cx="235" cy="215" r="8" fill="#{colors[2]}" opacity="0.6"/>
            <circle cx="265" cy="215" r="8" fill="#{colors[2]}" opacity="0.6"/>
            
            <!-- Title -->
            <text x="250" y="300" text-anchor="middle" fill="#{colors[0]}" font-family="monospace" font-size="16" font-weight="bold" filter="url(#glitch)">
                {clean_title[:25]}
            </text>
            <text x="250" y="325" text-anchor="middle" fill="#{colors[1]}" font-family="monospace" font-size="14">
                ({year})
            </text>
            
            <!-- Glitch message -->
            <text x="250" y="400" text-anchor="middle" fill="#{colors[2]}" font-family="monospace" font-size="12" font-weight="bold">
                {message}
            </text>
            
            <!-- Loading animation -->
            <text x="250" y="450" text-anchor="middle" fill="#{colors[0]}" font-family="monospace" font-size="10">
                LOADING...
                <animate attributeName="opacity" values="1;0;1" dur="1.5s" repeatCount="indefinite"/>
            </text>
            
            <!-- Static lines -->
            <line x1="50" y1="500" x2="450" y2="505" stroke="#{colors[1]}" stroke-width="1" opacity="0.4"/>
            <line x1="80" y1="520" x2="420" y2="518" stroke="#{colors[2]}" stroke-width="1" opacity="0.5"/>
            <line x1="120" y1="540" x2="380" y2="542" stroke="#{colors[0]}" stroke-width="1" opacity="0.3"/>
            
            <!-- Bottom text -->
            <text x="250" y="600" text-anchor="middle" fill="#{colors[1]}" font-family="monospace" font-size="8" opacity="0.7">
                POSTER SIGNAL INTERRUPTED
            </text>
            <text x="250" y="620" text-anchor="middle" fill="#{colors[2]}" font-family="monospace" font-size="8" opacity="0.6">
                ATTEMPTING RECONSTRUCTION...
            </text>
        </svg>
        '''
        
        # Convert SVG to data URL
        import base64
        svg_bytes = svg_content.encode('utf-8')
        svg_base64 = base64.b64encode(svg_bytes).decode('utf-8')
        return f"data:image/svg+xml;base64,{svg_base64}"
    
    def search_tmdb_movie(self, title):
        """Search for movie on TMDB with robust error handling and glitch fallback"""
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
            print(f"🎰 Connection glitch for '{title}' - Creating glitch placeholder")
        except requests.exceptions.Timeout:
            print(f"🎰 Timeout glitch for '{title}' - Creating glitch placeholder")
        except requests.exceptions.RequestException:
            print(f"🎰 Request glitch for '{title}' - Creating glitch placeholder")
        except Exception:
            print(f"🎰 Unknown glitch for '{title}' - Creating glitch placeholder")
        
        # Return glitch placeholder for any error
        return self.create_glitch_placeholder(title)
    
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
        """Generate enhanced recommendations with ratings, genres, and posters/glitch placeholders"""
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
            
            print("🎬 Fetching movie posters (with glitch protection)...")
            for i, rec in enumerate(sample_recommendations[:num_recommendations]):
                print(f"📽️ Processing {i+1}/{min(num_recommendations, len(sample_recommendations))}: {rec['title']}")
                rec['poster_url'] = self.search_tmdb_movie(rec['title'])
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
            
            print("🎬 Fetching movie posters (with glitch protection)...")
            
            # Fetch posters for top recommendations with progress indication
            for i, movie_data in enumerate(top_predictions):
                print(f"📽️ Processing {i+1}/{len(top_predictions)}: {movie_data['title']}")
                movie_data['poster_url'] = self.search_tmdb_movie(movie_data['title'])
                time.sleep(0.1)  # Small delay to avoid overwhelming TMDB
            
            print("✅ Recommendations ready!")
            return top_predictions
            
        except Exception as e:
            print(f"Error generating enhanced recommendations: {e}")
            # Return sample recommendations as fallback
            return self.get_enhanced_recommendations(selected_movies, num_recommendations)

# Global instance to be used across views
movie_data_loader = MovieDataLoader()
