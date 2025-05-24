import pandas as pd
import pickle
import os
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
            
            # Load SVD model
            model_path = os.path.join(base_dir, 'svd_model.pkl')
            with open(model_path, 'rb') as f:
                self.svd_model = pickle.load(f)
            
            print(f"✅ Loaded {len(self.movies_df)} movies")
            print(f"✅ Loaded SVD model successfully")
            
        except Exception as e:
            print(f"❌ Error loading data: {e}")
            # Fallback to sample data for development
            self.movies_df = pd.DataFrame({
                'movieId': [1, 2, 3],
                'title': ['Sample Movie 1', 'Sample Movie 2', 'Sample Movie 3'],
                'genres': ['Action', 'Comedy', 'Drama']
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
    
    def get_movie_id(self, title):
        """Get movie ID from title"""
        movie_row = self.movies_df[self.movies_df['title'] == title]
        if not movie_row.empty:
            return movie_row.iloc[0]['movieId']
        return None
    
    def get_recommendations(self, selected_movies, num_recommendations=10):
        """Generate recommendations based on selected movies"""
        if not self.svd_model:
            # Return sample recommendations if model not loaded
            return [
                'The Shawshank Redemption',
                'The Godfather',
                'The Dark Knight',
                'Pulp Fiction',
                'Forrest Gump'
            ]
        
        try:
            # Get movie IDs for selected movies
            movie_ids = []
            for title in selected_movies:
                movie_id = self.get_movie_id(title)
                if movie_id:
                    movie_ids.append(movie_id)
            
            if not movie_ids:
                return []
            
            # Create a temporary user ID (find max user ID + 1)
            # For now, we'll use a large number to avoid conflicts
            temp_user_id = 999999
            
            # Get all movie IDs
            all_movie_ids = self.movies_df['movieId'].unique()
            
            # Predict ratings for all movies for this temporary user
            predictions = []
            for movie_id in all_movie_ids:
                if movie_id not in movie_ids:  # Don't recommend already selected movies
                    try:
                        pred = self.svd_model.predict(temp_user_id, movie_id)
                        predictions.append((movie_id, pred.est))
                    except:
                        continue
            
            # Sort by predicted rating and get top recommendations
            predictions.sort(key=lambda x: x[1], reverse=True)
            top_movie_ids = [pred[0] for pred in predictions[:num_recommendations]]
            
            # Convert movie IDs back to titles
            recommended_titles = []
            for movie_id in top_movie_ids:
                title_row = self.movies_df[self.movies_df['movieId'] == movie_id]
                if not title_row.empty:
                    recommended_titles.append(title_row.iloc[0]['title'])
            
            return recommended_titles
            
        except Exception as e:
            print(f"Error generating recommendations: {e}")
            # Return sample recommendations as fallback
            return [
                'The Shawshank Redemption',
                'The Godfather', 
                'The Dark Knight',
                'Pulp Fiction',
                'Forrest Gump'
            ]

# Global instance to be used across views
movie_data_loader = MovieDataLoader()
