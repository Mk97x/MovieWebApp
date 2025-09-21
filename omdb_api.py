import os
import requests
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.getenv("API_KEY")

def fetch_movie(title: str):
    """
    Fetch movie information from OMDb API.
    
    Args:
        title (str): The movie title to search for
        
    Returns:
        dict: Dictionary with title, year, rating, poster or None if not found
    """
    if not API_KEY:
        raise ValueError("API_KEY not found in environment variables")
    
    if not title or not title.strip():
        return None
    
    try:
        url = f"http://www.omdbapi.com/?apikey={API_KEY}&t={title.strip()}"
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        if data.get("Response") != "True":
            return None

        # Handle cases where some fields might be missing or N/A
        year_str = data.get("Year", "N/A")
        year = int(year_str[:4]) if year_str != "N/A" and year_str[:4].isdigit() else None
        
        rating_str = data.get("imdbRating", "N/A")
        rating = float(rating_str) if rating_str != "N/A" and rating_str.replace('.', '').isdigit() else None
        
        return {
            "title": data.get("Title", title),
            "year": year,
            "rating": rating,
            "poster": data.get("Poster", ""),
            "director": data.get("Director", "N/A"),
            "genre": data.get("Genre", "N/A")
        }
        
    except requests.exceptions.RequestException as e:
        print(f"Error fetching movie data: {e}")
        return None
    except (ValueError, KeyError) as e:
        print(f"Error parsing movie data: {e}")
        return None

def search_movies(search_term: str, max_results: int = 5):
    """
    Search for movies by title (returns multiple results).
    
    Args:
        search_term (str): The search term
        max_results (int): Maximum number of results to return
        
    Returns:
        list: List of movie dictionaries or empty list if none found
    """
    if not API_KEY:
        raise ValueError("API_KEY not found in environment variables")
    
    if not search_term or not search_term.strip():
        return []
    
    try:
        url = f"http://www.omdbapi.com/?apikey={API_KEY}&s={search_term.strip()}&type=movie"
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        if data.get("Response") != "True":
            return []

        movies = []
        for movie_data in data.get("Search", [])[:max_results]:
            movies.append({
                "title": movie_data.get("Title", ""),
                "year": movie_data.get("Year", ""),
                "poster": movie_data.get("Poster", ""),
                "imdb_id": movie_data.get("imdbID", "")
            })
        
        return movies
        
    except requests.exceptions.RequestException as e:
        print(f"Error searching movies: {e}")
        return []
    except (ValueError, KeyError) as e:
        print(f"Error parsing search results: {e}")
        return []

# Test function
if __name__ == "__main__":
    # Test the fetch_movie function
    movie = fetch_movie("The Matrix")
    if movie:
        print(f"Found movie: {movie['title']} ({movie['year']})")
        print(f"Rating: {movie['rating']}")
    else:
        print("Movie not found")