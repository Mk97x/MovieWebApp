from flask import Flask, render_template, request, redirect, url_for
from models import db, User, Movie
from data_manager import DataManager
from omdb_api import fetch_movie, search_movies, get_movie_details_by_id
import os


app = Flask(__name__)
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{os.path.join(basedir, 'data/movies.db')}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

data_manager = DataManager() 

@app.route('/')
def index():
    """Display the main page with list of all users"""
    users = data_manager.get_users()
    users_with_counts = []
    for user in users:
        movies = data_manager.get_movies(user.id)
        users_with_counts.append({
            'user': user,
            'movie_count': len(movies)
        })
    return render_template('index.html', users_with_counts=users_with_counts)

@app.route('/users', methods=['POST'])
def create_user():
    """Create a new user from form data and redirect to main page"""
    name = request.form.get('name')
    if name and name.strip():
        data_manager.create_user(name.strip())
    return redirect(url_for('index'))

@app.route('/users/<int:user_id>/movies')
def user_movies(user_id):
    """Display all movies for a specific user"""
    user = data_manager.get_user_by_id(user_id)
    if user:
        movies = data_manager.get_movies(user_id)
        return render_template('user_movies.html', user=user, movies=movies)
    return "User not found", 404



@app.route('/users/<int:user_id>/movies/<int:movie_id>/update', methods=['POST'])
def update_movie(user_id, movie_id):
    """
    Update an existing movie's details
    Gets updated movie information from form and updates the database
    """
    # Get form data
    title = request.form.get('title')
    director = request.form.get('director')
    year = request.form.get('year')
    rating = request.form.get('rating')
    
    if title and director and year:
        movie_data = {
            'title': title,
            'director': director,
            'year': int(year),
            'rating': float(rating) if rating else None
        }
        data_manager.update_movie(movie_id, movie_data)
    
    return redirect(url_for('user_movies', user_id=user_id))

@app.route('/users/<int:user_id>/movies/<int:movie_id>/delete', methods=['POST'])
def delete_movie(user_id, movie_id):
    """
    Delete a movie from user's favorites
    Removes the specified movie from the database
    """
    data_manager.delete_movie(movie_id)
    return redirect(url_for('user_movies', user_id=user_id))

@app.route('/users/<int:user_id>/movies/add')
def add_movie_form(user_id):
    """Display form for adding a new movie to a user's collection"""
    user = data_manager.get_user_by_id(user_id)
    if user:
        return render_template('add_movie.html', user=user)
    return "User not found", 404

@app.route('/users/<int:user_id>/movies/<int:movie_id>/edit')
def edit_movie_form(user_id, movie_id):
    """Display form for editing an existing movie"""
    user = data_manager.get_user_by_id(user_id)
    movie = data_manager.get_movie_by_id(movie_id)
    if user and movie:
        return render_template('edit_movie.html', user=user, movie=movie)
    return "User or movie not found", 404

@app.route('/users/<int:user_id>/delete', methods=['POST'])
def delete_user(user_id):
    """Delete a user and all their movies"""
    data_manager.delete_user(user_id)
    return redirect(url_for('index'))

@app.route('/movies/search')
def search_movies_route():
    """Search for movies using OMDb API"""
    search_term = request.args.get('title')
    user_id = request.args.get('user_id')
    movies = []
    if search_term:
        movies = search_movies(search_term, 10)
    return render_template('search_movies.html', movies=movies, search_term=search_term, user_id=user_id)

@app.route('/movies/details/<imdb_id>')
def movie_details(imdb_id):
    """Show detailed movie information"""
    movie_data = get_movie_details_by_id(imdb_id)
    if movie_data:
        return render_template('movie_details.html', movie=movie_data)
    return "Movie not found", 404

@app.route('/users/<int:user_id>/movies/add_from_omdb/<imdb_id>')
def add_movie_from_omdb(user_id, imdb_id):
    """Add a movie to user's favorites using OMDb data"""
    user = data_manager.get_user_by_id(user_id)
    if not user:
        return "User not found", 404
        
    movie_data = get_movie_details_by_id(imdb_id)
    if movie_data:
        movie_info = {
            'title': movie_data['title'],
            'director': movie_data['director'],
            'year': movie_data['year'] or 0,
            'rating': movie_data['rating']
        }
        data_manager.add_movie(movie_info, user_id)
    
    return redirect(url_for('user_movies', user_id=user_id))

@app.route('/users/<int:user_id>/movies', methods=['POST'])
def add_movie(user_id):
    """Add movie to user's favorites - try OMDb first, then fallback to manual input"""
    title = request.form.get('title')
    
    if title:
        movie_data = fetch_movie(title)
        
        if movie_data:
            movie_info = {
                'title': movie_data['title'],
                'director': movie_data['director'],
                'year': movie_data['year'] or 0,
                'rating': movie_data['rating']
            }
        else:
            movie_info = {
                'title': title,
                'director': request.form.get('director', 'Unknown'),
                'year': int(request.form.get('year', 0)),
                'rating': float(request.form.get('rating')) if request.form.get('rating') else None
            }
        
        data_manager.add_movie(movie_info, user_id)
    
    return redirect(url_for('user_movies', user_id=user_id))

if __name__ == '__main__':
    with app.app_context():
        db.create_all()

    app.run(debug=True, host='0.0.0.0', port=5000)