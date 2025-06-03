@echo off
echo Starting Movie Recommendation System...
call conda activate movie_rec_env
python manage.py runserver
pause
