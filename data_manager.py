from models import db, User, Movie

class DataManager:
    def create_user(self, name):
        """Add a new user to the database"""
        new_user = User(name=name)
        db.session.add(new_user)
        db.session.commit()
        return new_user

    def get_users(self):
        """Returns a list of all users in the database"""
        return User.query.all()

    def get_user_by_id(self, user_id):
        """Returns a specific user by ID"""
        return User.query.get(user_id)

    def get_movies(self, user_id):
        """Returns a list of all movies for a specific user"""
        return Movie.query.filter_by(user_id=user_id).all()

    def get_movie_by_id(self, movie_id):
        """Returns a specific movie by ID"""
        return Movie.query.get(movie_id)

    def add_movie(self, movie_data, user_id):
        """
        Add a new movie to a user's favorites
        movie_data should be a dictionary containing movie information
        """
        new_movie = Movie(
            title=movie_data['title'],
            director=movie_data['director'],
            year=movie_data['year'],
            rating=movie_data.get('rating'),
            user_id=user_id
        )
        db.session.add(new_movie)
        db.session.commit()
        return new_movie

    def update_movie(self, movie_id, movie_data):
        """Update the details of a specific movie in the database"""
        movie = Movie.query.get(movie_id)
        if movie:
            movie.title = movie_data.get('title', movie.title)
            movie.director = movie_data.get('director', movie.director)
            movie.year = movie_data.get('year', movie.year)
            movie.rating = movie_data.get('rating', movie.rating)
            db.session.commit()
            return movie
        return None

    def delete_movie(self, movie_id):
        """Remove a movie from the user's favorites list"""
        movie = Movie.query.get(movie_id)
        if movie:
            db.session.delete(movie)
            db.session.commit()
            return True
        return False

    def delete_user(self, user_id):
        """Delete a user and all their movies"""
        user = User.query.get(user_id)
        if user:
            # First delete all movies of the user
            Movie.query.filter_by(user_id=user_id).delete()
            # Then delete the user
            db.session.delete(user)
            db.session.commit()
            return True
        return False