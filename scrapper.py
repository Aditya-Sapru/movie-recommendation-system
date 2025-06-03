import requests
from bs4 import BeautifulSoup
import pandas as pd
import time # Import time for adding delays
import random # Import random for rotating User-Agents

# Base URL for IMDb (useful for constructing full movie URLs)
IMDB_BASE_URL = "https://www.imdb.com"
TOP_250_URL = "https://www.imdb.com/chart/top"

# A list of common User-Agent strings to rotate through.
# This helps in mimicking different browsers and can reduce blocking.
USER_AGENTS = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/114.0',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.5.1 Safari/605.1.15',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Edge/125.0.0.0',
]

print(f"Attempting to fetch Top 250 movies from: {TOP_250_URL}")

movies_data = [] # List to store all movie dictionaries

try:
    # Select a random User-Agent for the initial request
    headers = {
        'User-Agent': random.choice(USER_AGENTS),
        'Accept-Language': 'en-US,en;q=0.9',
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
    }

    # Make the request to the Top 250 page with the added headers
    response = requests.get(TOP_250_URL, headers=headers)
    
    # Raise an HTTPError for bad responses (4xx or 5xx)
    response.raise_for_status() 
    
    soup = BeautifulSoup(response.text, 'html.parser')

    # Movies are typically found in 'li' elements with the 'ipc-metadata-list-summary-item' class
    movie_items = soup.select("li.ipc-metadata-list-summary-item")

    print(f"Found {len(movie_items)} movie items on the main page.")

    if not movie_items:
        print("No movie items found with the new selector. The HTML structure might have changed again or the request was blocked.")
        print("Response content (first 500 chars):", response.text[:500]) # Print part of response for debugging

    # Iterate through each movie on the Top 250 list
    for i, item in enumerate(movie_items):
        title = "N/A"
        year = "N/A"
        rating = 0.0
        description = "N/A" # Initialize description
        movie_full_url = "N/A" # Initialize URL

        try:
            # Extract Title and its relative URL
            title_element = item.select_one('h3.ipc-title__text')
            if title_element:
                title_parts = title_element.text.split('. ', 1)
                if len(title_parts) > 1:
                    title = title_parts[1].strip()
                else:
                    title = title_element.text.strip() # Fallback if no ranking number
                
                # Get the relative URL for the movie's detail page
                link_element = item.select_one('a.ipc-title-link')
                if link_element and 'href' in link_element.attrs:
                    movie_relative_url = link_element['href']
                    movie_full_url = f"{IMDB_BASE_URL}{movie_relative_url.split('?')[0]}" # Remove query params
            else:
                print(f"Warning: Could not find title for an item. Skipping to next.")
                continue # Skip this item if title or link is not found

            # Extract Year
            metadata_elements = item.select_one('div.cli-title-metadata')
            if metadata_elements:
                # Year is typically within a span that has a specific class for the year
                # The class 'sc-b090f09b-8' is a common dynamic class for such elements.
                # If this changes, you might need to inspect the page again.
                year_span = metadata_elements.find('span', class_='sc-b090f09b-8') 
                if year_span:
                    year = year_span.text.strip()
                else:
                    # Fallback: if the specific year span class isn't found, try to get the first span
                    # in the metadata div, as year is usually the first piece of info.
                    all_spans = metadata_elements.find_all('span')
                    if all_spans:
                        year = all_spans[0].text.strip() 
                    else:
                        print(f"Warning: Could not find year in metadata for '{title}'.")

            # Extract Rating
            rating_element = item.select_one('span.ipc-rating-star--rating')
            if rating_element:
                # The text usually includes the rating and the count (e.g., "9.2 (2.8M)")
                # We split by '(' to get only the rating number
                rating_text = rating_element.text.split('(')[0].strip() 
                try:
                    rating = float(rating_text)
                except ValueError:
                    print(f"Warning: Could not convert rating '{rating_text}' to float for '{title}'. Setting to 0.0.")
                    rating = 0.0
            else:
                print(f"Warning: Could not find rating for '{title}'. Setting to 0.0.")
                rating = 0.0

            # --- Scrape Description from Individual Movie Page ---
            if movie_full_url != "N/A":
                print(f"  [{i+1}/{len(movie_items)}] Fetching description for: {title} ({year})...")
                # Add a longer delay between requests to individual movie pages to avoid detection
                time.sleep(random.uniform(1.0, 2.5)) # Random delay between 1 and 2.5 seconds

                try:
                    # Use a fresh set of headers for each individual movie page request
                    movie_headers = {
                        'User-Agent': random.choice(USER_AGENTS),
                        'Accept-Language': 'en-US,en;q=0.9',
                        'Accept-Encoding': 'gzip, deflate, br',
                        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
                        'Connection': 'keep-alive',
                        'Upgrade-Insecure-Requests': '1',
                    }
                    movie_response = requests.get(movie_full_url, headers=movie_headers)
                    movie_response.raise_for_status()
                    movie_soup = BeautifulSoup(movie_response.text, 'html.parser')

                    # --- UPDATED SELECTORS FOR MOVIE DESCRIPTION based on user's snippet ---
                    description_element = movie_soup.find('div', class_='ipc-html-content-inner-div', role='presentation')
                    
                    # Fallback if the above specific selector doesn't work (e.g., if it's within a data-testid container)
                    if not description_element:
                        plot_container = movie_soup.find('div', {'data-testid': 'plot-l'})
                        if plot_container:
                            description_element = plot_container.find('span', class_='ipc-html-content-inner-div')
                    
                    if not description_element:
                        plot_container_xl = movie_soup.find('span', {'data-testid': 'plot-xl'})
                        if plot_container_xl:
                            description_element = plot_container_xl

                    if description_element:
                        description = description_element.text.strip()
                    else:
                        print(f"    Warning: Description element not found for '{title}' on its page with current selectors.")

                except requests.exceptions.RequestException as e:
                    print(f"    Error fetching description for {title} from {movie_full_url}: {e}")
                except AttributeError:
                    print(f"    Could not find description elements for {title} at {movie_full_url}. (HTML structure might have changed)")
                except Exception as e:
                    print(f"    An unexpected error occurred while getting description for {title}: {e}")

        except AttributeError as e:
            print(f"Error parsing a movie item (AttributeError): {e}. Skipping this item.")
            continue
        except ValueError as e:
            print(f"Error converting data for a movie item (ValueError): {e}. Skipping this item.")
            continue
        except IndexError as e:
            print(f"Error with index (e.g., splitting title or rating) for a movie item (IndexError): {e}. Skipping this item.")
            continue
        except Exception as e:
            print(f"An unexpected error occurred during item parsing for '{title}': {e}. Skipping this item.")
            continue
        
        movies_data.append({
            "title": title,
            "year": year,
            "rating": rating,
            "description": description,
            "url": movie_full_url # Also good to store the URL
        })

    df = pd.DataFrame(movies_data)
    
    # Check if the DataFrame is empty before saving
    if not df.empty:
        df.to_csv("movies.csv", index=False)
        print(f"Successfully scraped {len(movies_data)} movies and saved to movies.csv")
    else:
        print("No movie data was extracted. The DataFrame is empty. CSV file not created.")

except requests.exceptions.HTTPError as errh:
    print(f"HTTP Error: {errh}")
    print(f"Response content (first 500 chars): {response.text[:500]}")
except requests.exceptions.ConnectionError as errc:
    print(f"Error Connecting: {errc}")
except requests.exceptions.Timeout as errt:
    print(f"Timeout Error: {errt}")
except requests.exceptions.RequestException as err:
    print(f"An unexpected error occurred: {err}")
except Exception as e:
    print(f"An unexpected error occurred during scraping: {e}")
