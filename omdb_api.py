import os
import requests
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.getenv("API_KEY")

def fetch_movie(title: str):
    """
    Fetch exact movie information from OMDb API.
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
            "genre": data.get("Genre", "N/A"),
            "plot": data.get("Plot", "N/A"),
            "imdb_id": data.get("imdbID", "")
        }
        
    except requests.exceptions.RequestException as e:
        print(f"Error fetching movie  {e}")
        return None
    except (ValueError, KeyError) as e:
        print(f"Error parsing movie  {e}")
        return None

def search_movies(search_term: str, max_results: int = 10):
    """
    Search for movies by title (returns multiple similar results).
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
                "imdb_id": movie_data.get("imdbID", ""),
                "type": movie_data.get("Type", "")
            })
        
        return movies
        
    except requests.exceptions.RequestException as e:
        print(f"Error searching movies: {e}")
        return []
    except (ValueError, KeyError) as e:
        print(f"Error parsing search results: {e}")
        return []

def get_movie_details_by_id(imdb_id: str):
    """
    Get detailed movie information by IMDB ID.
    """
    if not API_KEY:
        raise ValueError("API_KEY not found in environment variables")
    
    if not imdb_id:
        return None
    
    try:
        url = f"http://www.omdbapi.com/?apikey={API_KEY}&i={imdb_id}"
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
            "title": data.get("Title", ""),
            "year": year,
            "rating": rating,
            "poster": data.get("Poster", ""),
            "director": data.get("Director", "N/A"),
            "genre": data.get("Genre", "N/A"),
            "plot": data.get("Plot", "N/A"),
            "imdb_id": data.get("imdbID", ""),
            "runtime": data.get("Runtime", "N/A"),
            "actors": data.get("Actors", "N/A"),
            "released": data.get("Released", "N/A")
        }
        
    except requests.exceptions.RequestException as e:
        print(f"Error fetching movie details: {e}")
        return None
    except (ValueError, KeyError) as e:
        print(f"Error parsing movie details: {e}")
        return None