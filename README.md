# Movie Recommendation System

A professional, ML-powered movie recommender with advanced analytics and user-friendly exports.

---

## Table of Contents

- [Features](#features)
- [Requirements](#requirements)
- [Quickstart](#quickstart)
- [Usage](#usage)
- [Export Options](#export-options)
- [Analytics Dashboard](#analytics-dashboard)
- [FAQs](faq)
- [Project Structure](#project-structure-)
- [Author](#author)

---

## Features

- **Personalized Movie Recommendations** using collaborative filtering (SVD) on the MovieLens 20M dataset.
- **Dynamic Poster Loading**: Genre-based illustrated cards with real poster loading.
- **Advanced Filtering**: Filter by genre, year, rating, and sort order.
- **Confidence Scores & Explanations**: ML confidence metrics with human-readable insights.
- **Infinite Scroll**: Load recommendations seamlessly.
- **Professional Exports**: Download recommendations as CSV or PDF.
- **Interactive Analytics Dashboard**: Visualize preferences and recommendation patterns.
- **No Database Required**: Uses Pandas and pre-trained models for fast results.
- **Intelligent Caching**: Optimized performance for repeated queries.

---

## Requirements

- **Python 3.11**
- **conda** (for environment management)
- **Git** (to clone the repository)

---

## Quickstart

### 1. Clone the Repository

```bash
git clone https://github.com/Nitin-Nandan/CodeClauseInternship_MovieRecommendationSystem.git
```

```bash
cd CodeClauseInternship_MovieRecommendationSystem
```

### 2. Create and Activate the Conda Environment

```bash
conda env create -f environment.yml
```

```bash
conda activate movie_rec
```

### 3. Prepare Data & Models

#### Download the MovieLens 20M Dataset:
1. Visit [MovieLens 20M Dataset](https://grouplens.org/datasets/movielens/20m/)
2. Download `ml-20m.zip`
3. Extract the zip file.
4. Place the extracted `ml-20m` folder in the project root directory.

**Required Structure:** <br>
movie-recommendation-system/ <br>
└── ml-20m/ <br>
├── movies.csv <br>
└── ratings.csv <br>

#### Get the Pre-trained SVD Model:
- **Option 1: Download Pre-trained Model**  
  Download [`svd_model.pkl`](https://drive.google.com/file/d/1Ihgls0cMU7SA7ByHBYbBQcEzyutRJEBd/view?usp=sharing) and place it in the project root directory.

- **Option 2: Train the Model Yourself**  
  Use the included Jupyter notebook (`train_model.ipynb`) to generate your own `svd_model.pkl`.

### 4. Run the App

```bash
python manage.py runserver
```

Open your browser to: [http://127.0.0.1:8000](http://127.0.0.1:8000)

---

## Usage

1. **Select Movies**: Choose at least 3 movies from the search bar.
2. **Apply Filters**: Refine by genre, year, rating, or sorting.
3. **Get Recommendations**: Click the button to generate your list.
4. **Scroll**: Load more recommendations dynamically.
5. **Export**: Download results as CSV or PDF.
6. **Analytics**: Explore insights in the dashboard.

---

## Export Options

- **CSV**: Export all recommendations or current view.
- **PDF**: Generate professional reports for all or displayed results.

---

## Analytics Dashboard

- **Genre Preferences**: Pie chart of favorite genres.
- **Confidence Distribution**: Bar chart of recommendation confidence.
- **Rating Trends**: Line chart of predicted ratings.
- **Era Analysis**: Polar chart of movie release decades.

---

## FAQs

**Q: Do I need to set up a database?**  
A: No. The system uses Pandas and pre-trained models.

**Q: Some posters are missing.**  
A: Genre-based cards appear if posters are unavailable.

**Q: How do I export only visible movies?**  
A: Use the "Current" option in the export panel.

**Q: Can I run this on macOS/Linux?**  
A: Yes. Follow the same conda setup steps.

**Q: Missing package errors?**  
A: Ensure you activated the environment and ran `conda env create -f environment.yml`.

**Q: Can I retrain the model?**  
A: Yes. Use the MovieLens dataset and scikit-learn.

---

## Project Structure <br>

movie-recommendation-system/ <br>
├── ml-20m/ # Dataset <br>
├── movapp/ # Django app <br>
│ ├── static/ # CSS/JS/images <br>
│ ├── templates/ # HTML templates <br>
│ ├── data_loader.py # ML/data logic <br>
│ ├── views.py # App views <br>
│ ├── export_views.py # CSV/PDF exports <br>
│ └── analytics_views.py # Analytics endpoints <br>
├── environment.yml # Conda environment <br>
├── manage.py # Django CLI <br>
└── README.md # Documentation <br>

---

## Author

### Nitin Nandan <br> - Project Creator & Maintainer

***This project was developed as part of the CodeClause Internship Program.***

---

**Ready to explore personalized movie recommendations!** 🎬🔍