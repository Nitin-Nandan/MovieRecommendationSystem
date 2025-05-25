import pandas as pd
import pickle
import os
import numpy as np
from django.conf import settings

class MovieDataLoader:
    def __init__(self):
        self.movies_df = None
        self.svd_model = None
        self.movie_titles = []
        self.load_data()
    
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
                'title': ['The Shawshank Redemption', 'The Godfather', 'The Dark Knight', 'Pulp Fiction', 'Forrest Gump'],
                'genres': ['Drama', 'Crime|Drama', 'Action|Crime|Drama', 'Crime|Drama', 'Comedy|Drama|Romance']
            })
            self.movie_titles = self.movies_df['title'].tolist()
            self.svd_model = None
    
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
        """Generate enhanced recommendations with ratings and genres"""
        if not self.svd_model:
            # Return enhanced sample recommendations if model not loaded
            sample_recommendations = [
                {'title': 'The Shawshank Redemption', 'predicted_rating': 4.8, 'genres': ['Drama']},
                {'title': 'The Godfather', 'predicted_rating': 4.7, 'genres': ['Crime', 'Drama']},
                {'title': 'The Dark Knight', 'predicted_rating': 4.6, 'genres': ['Action', 'Crime', 'Drama']},
                {'title': 'Pulp Fiction', 'predicted_rating': 4.5, 'genres': ['Crime', 'Drama']},
                {'title': 'Forrest Gump', 'predicted_rating': 4.4, 'genres': ['Comedy', 'Drama', 'Romance']},
                {'title': 'Inception', 'predicted_rating': 4.3, 'genres': ['Action', 'Sci-Fi', 'Thriller']},
                {'title': 'The Matrix', 'predicted_rating': 4.2, 'genres': ['Action', 'Sci-Fi']},
                {'title': 'Goodfellas', 'predicted_rating': 4.1, 'genres': ['Biography', 'Crime', 'Drama']},
                {'title': 'The Lord of the Rings', 'predicted_rating': 4.0, 'genres': ['Adventure', 'Drama', 'Fantasy']},
                {'title': 'Star Wars', 'predicted_rating': 3.9, 'genres': ['Action', 'Adventure', 'Fantasy']}
            ]
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
                            predictions.append({
                                'movieId': movie_id,
                                'title': movie['title'],
                                'predicted_rating': round(pred.est, 1),
                                'genres': movie['genres'].split('|') if pd.notna(movie['genres']) else ['Unknown']
                            })
                    except Exception as pred_error:
                        continue
            
            # Sort by predicted rating and return top recommendations
            predictions.sort(key=lambda x: x['predicted_rating'], reverse=True)
            return predictions[:num_recommendations]
            
        except Exception as e:
            print(f"Error generating enhanced recommendations: {e}")
            # Return sample recommendations as fallback
            return self.get_enhanced_recommendations(selected_movies, num_recommendations)

# Global instance to be used across views
movie_data_loader = MovieDataLoader()
