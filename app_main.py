import streamlit as st
import pandas as pd
import random
import requests
from bs4 import BeautifulSoup
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import pylast
import time
import os

# Spotify API credentials
spotify_client_id = os.getenv("spotify_client_id")
spotify_client_secret = os.getenv("spotify_client_secret")

# Last.fm API credentials
API_KEY = os.getenv("API_KEY")
API_SECRET = os.getenv("API_SECRET")

# Initialize Spotify client
sp = spotipy.Spotify(auth_manager=SpotifyClientCredentials(client_id=spotify_client_id, client_secret=spotify_client_secret))

# Set page config
st.set_page_config(page_title="Random Metal Tools by PepHoRRoR", page_icon="🤘", layout="wide")

# Load CSS
def load_css():
    with open("style.css") as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

load_css()

# Sidebar for navigation
st.sidebar.title("Random Metal Tools")
app_mode = st.sidebar.selectbox("Choose the App", ["Random Metal", "Random Bandcamp", "Random New Release", "Random by Genres", "Last.fm Manual Scrobbler"])

# Random Metal functionality
def random_metal():
    st.title("Random Metal")

    # Load the metal records data
    df = pd.read_csv('metal_records.csv')

    if st.button("Get Random Metal Album"):
        # Select a random row from the dataframe
        random_album = df.sample(n=1).iloc[0]

        # Display album information
        st.subheader(f"{random_album['Band']} - {random_album['Album']}")
        st.write(f"{random_album['Genre'].lower()}")

        # Display album cover
        st.image(random_album['Image URL'], width=300)

        # Create Spotify links
        spotify_url = random_album['Spotify URL']

        if spotify_url and spotify_url != 'Not found':
            st.markdown(f'<a class="spotify-link" href="{spotify_url}" target="_blank" class="spotify-link">Listen on Spotify</a>', unsafe_allow_html=True)

# Random Bandcamp functionality
def random_bandcamp():
    st.title("Random Metal from Bandcamp")

    if 'iframe' not in st.session_state:
        st.session_state['iframe'] = None

    if st.button("Get Random Metal Album from Bandcamp"):
        with st.spinner("Finding a metal bandcamp..."):
            st.session_state['iframe'] = get_random_metal_band_iframe()

    if st.session_state['iframe']:
        st.components.v1.html(st.session_state['iframe'], width=450, height=450)

# Random Recent Release functionality
def random_recent_release():
    st.title("Random New Release")

    # Initialize session state variables
    if 'random_album' not in st.session_state:
        st.session_state.random_album = None
        st.session_state.spotify_url = None
        st.session_state.spotify_image = None
        st.session_state.bandcamp_url = None

    def get_spotify_data(album_info):
        parts = album_info.split(' - ')
        if len(parts) < 2:
            return None, None
        band_name = parts[0]
        record_name = ' - '.join(parts[1:])
        results = sp.search(q=f"artist:{band_name} album:{record_name}", type='album')
        if results['albums']['items']:
            album = results['albums']['items'][0]
            spotify_url = album['external_urls']['spotify']
            spotify_artist = album['artists'][0]['name']
            spotify_album = album['name']
            if spotify_artist.lower() == band_name.lower() and spotify_album.lower() == record_name.lower():
                image_url = album['images'][0]['url'] if album['images'] else None
                return spotify_url, image_url
        return None, None

    def get_bandcamp_album_url(album_info):
        parts = album_info.split(' - ')
        if len(parts) < 2:
            return None
        band_name = parts[0]
        record_name = ' - '.join(parts[1:])
        search_query = f"{band_name} {record_name}".replace(" ", "+")
        search_url = f"https://bandcamp.com/search?q={search_query}&item_type=a"
        response = requests.get(search_url)
        if response.status_code != 200:
            return None
        soup = BeautifulSoup(response.content, 'html.parser')
        result_info = soup.find('li', class_='searchresult data-search')
        if result_info:
            album_url_tag = result_info.find('a', href=True)
            if album_url_tag:
                album_url = album_url_tag['href']
                url_modificada = album_url.split("?from")[0]
                return url_modificada
        return None

    def scrape_metalstorm(url):
        response = requests.get(url)
        soup = BeautifulSoup(response.content, 'html.parser')
        rows = soup.find_all('tr')
        data = []
        for row in rows:
            date_cell = row.find('td', class_='dark')
            if date_cell:
                date = date_cell.text.strip()
                album_info = row.find('div', class_='col-md-7').find('a').text.strip()
                album_type = row.find('div', class_='col-md-1').find('span').text.strip()
                genre = row.find('div', class_='col-md-4').text.strip()
                data.append({"Date": date, "Album": album_info.title(), "Type": album_type, "Genre": genre.title()})
        return data

    def get_random_album():
        urls = [
            'https://metalstorm.net/events/new_releases.php?page=1',
            'https://metalstorm.net/events/new_releases.php?page=2',
            'https://metalstorm.net/events/new_releases.php?page=3'
        ]
        all_data = []
        for url in urls:
            all_data.extend(scrape_metalstorm(url))

        while True:
            random_album = random.choice(all_data)
            spotify_url, spotify_image = get_spotify_data(random_album['Album'])
            bandcamp_url = get_bandcamp_album_url(random_album['Album'])
            if spotify_url or bandcamp_url:
                return random_album, spotify_url, spotify_image, bandcamp_url

    # Add a clear, visible button
    if st.button("Get Random New Release"):
        st.session_state.random_album, st.session_state.spotify_url, st.session_state.spotify_image, st.session_state.bandcamp_url = get_random_album()

    # Check if we have an album in the session state, if not, get one
    if st.session_state.random_album is None:
        st.session_state.random_album, st.session_state.spotify_url, st.session_state.spotify_image, st.session_state.bandcamp_url = get_random_album()

    if st.session_state.random_album:
        album = st.session_state.random_album
        spotify_url = st.session_state.spotify_url
        spotify_image = st.session_state.spotify_image
        bandcamp_url = st.session_state.bandcamp_url

        st.write(f"**Release Date:** {album['Date']}")
        st.write(f"{album['Album']} {album['Type']}")
        #st.write(f"{album['Type']}")
        st.write(f"{album['Genre']}")

        if spotify_image:
            st.image(spotify_image, caption="Album Cover", width=300)

        if spotify_url:
            st.markdown(f'<a href="{spotify_url}" target="_blank" class="spotify-link">Listen on Spotify</a>', unsafe_allow_html=True)
        if bandcamp_url:
            st.markdown(f'<a href="{bandcamp_url}" target="_blank" class="bandcamp-link">Listen on Bandcamp</a>', unsafe_allow_html=True)

        spreadsheet_releases = "https://docs.google.com/spreadsheets/d/1z7wGG2_NUJGli_wf3FUG_MYsPmtQRTleeXy7EaOtIMg/edit?usp=sharing"
        st.markdown(f'<a href="{spreadsheet_releases}" target="_blank">2025 Metal Releases</a>', unsafe_allow_html=True)

# Last.fm Scrobbler functionality
def lastfm_scrobbler():
    st.title("Last.fm Manual Scrobbler")

    if 'network' not in st.session_state:
        st.subheader("Login to Last.fm")
        username = st.text_input("Enter your Last.fm username:")
        password = st.text_input("Enter your Last.fm password:", type="password")
        if st.button("Login"):
            if username and password:
                try:
                    network = initialize_network(username, password)
                    st.session_state.network = network
                    st.success("Login successful!")
                except pylast.WSError:
                    st.error("Login failed. Please check your credentials and try again.")
            else:
                st.warning("Please enter both username and password.")

    if 'network' in st.session_state:
        artist_name = st.text_input("Enter the artist name:")
        album_name = st.text_input("Enter the album name:")

        if st.button("Search Album"):
            if artist_name and album_name:
                album = search_album(st.session_state.network, artist_name, album_name)
                if album:
                    st.session_state.album = album
                    st.success(f"Found: {album.artist.name} - {album.title}")
                else:
                    st.error("No album found. Please check your input and try again.")
            else:
                st.warning("Please enter both artist name and album name.")

    if 'album' in st.session_state:
        option = st.selectbox(
            "What would you like to do?",
            ("Scrobble to Last.fm", "Show artist information", "Show album tracklist", "Show similar artists")
        )

        if st.button("Execute"):
            if option == "Scrobble to Last.fm":
                result = scrobble_album(st.session_state.network, st.session_state.album)
                st.success(result)
            elif option == "Show artist information":
                info = show_artist_info(st.session_state.album)
                st.info(info)
            elif option == "Show album tracklist":
                tracklist = show_tracklist(st.session_state.album)
                st.text(tracklist)
            elif option == "Show similar artists":
                similar = show_similar_artists(st.session_state.album)
                st.text(similar)

# Random by Genres
def lastfm_genre_explorer():
    st.title("Random by Genre")

    genre_choices = [
        "Heavy Metal", "Thrash Metal", "Death Metal", "Black Metal", "Doom Metal",
        "Power Metal", "Progressive Metal", "Grindcore", "Folk Metal", "Industrial Metal",
        "Nu Metal", "Metalcore"
    ]

    chosen_genre = st.selectbox("Choose a Metal Subgenre:", genre_choices)

    if 'genre_data' not in st.session_state:
        st.session_state.genre_data = {
            'band': None,
            'album': None,
            'spotify_url': None,
            'spotify_image': None,
            'bandcamp_url': None
        }

    def get_random_band_by_genre(genre):
        """
        Finds a random band on Last.fm for a given genre. Excludes the top 25 most popular bands.
        Requires the band to have a tag that *exactly* matches the chosen genre.
        """
        # Initialize Last.fm network using your API key
        try:
            network = pylast.LastFMNetwork(api_key=API_KEY, api_secret=API_SECRET)
        except pylast.WSError as e:
            st.error(f"Error initializing Last.fm network: {e}")
            return None

        page = 1
        max_tries = 5  # Limit the number of page attempts
        genre = genre.lower()

        while page <= max_tries:  # Try with more pages if no result is found
            try:
                tag = network.get_tag(genre)  # Get the tag object
                top_bands = tag.get_top_artists(limit=100)  # Limit retrieved bands

                artists = [band.item for band in top_bands]  # Extract Artist objects

                random_artist = random.choice(artists)

                return random_artist

            except pylast.NetworkError as e:
                st.error(f"Network error: {e}")
                return None

    def get_random_album_by_band(artist):
        """
        Gets a random album from the band.
        """
        try:
            # Initialize Last.fm network using your API key
            network = pylast.LastFMNetwork(api_key=API_KEY, api_secret=API_SECRET)

            albums = artist.get_top_albums(limit=10)  # Limit number of albums fetched
            if not albums:
                st.info(f"No albums found for {artist.name}")
                return None
            return random.choice(albums).item
        except pylast.NetworkError as e:
            st.error(f"Network error: {e}")
            return None

    def get_spotify_data(artist_name, album_name):
        """
        Searches Spotify for an album by a given artist and album name.
        Returns the Spotify URL and image URL if found, otherwise None.
        """
        try:
            results = sp.search(q=f"artist:{artist_name} album:{album_name}", type='album', limit=1)  # Limit results to 1
            if results['albums']['items']:
                album = results['albums']['items'][0]
                spotify_url = album['external_urls']['spotify']
                image_url = album['images'][0]['url'] if album['images'] else None
                return spotify_url, image_url
            else:
                return None, None
        except spotipy.SpotifyException as e:
            st.error(f"Spotify error: {e}")
            return None, None

    def get_bandcamp_album_url(artist_name, album_name):
        """
        Searches Bandcamp for an album and returns the URL.
        """
        search_query = f"{artist_name} {album_name}".replace(" ", "+")
        search_url = f"https://bandcamp.com/search?q={search_query}&item_type=a"
        try:
            response = requests.get(search_url)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, 'html.parser')
            result_info = soup.find('li', class_='searchresult data-search')
            if result_info:
                album_url_tag = result_info.find('a', href=True)
                if album_url_tag:
                    album_url = album_url_tag['href']
                    url_modificada = album_url.split("?from")[0]
                    return url_modificada
            return None  # Return None if no album found
        except requests.exceptions.RequestException as e:
            st.error(f"Bandcamp search error: {e}")
            return None

    def get_new_album_data():
        band = get_random_band_by_genre(chosen_genre)
        if band:
            album = get_random_album_by_band(band)
            if album:
                spotify_url, spotify_image = get_spotify_data(band.name, album.title)
                bandcamp_url = get_bandcamp_album_url(band.name, album.title)
                return {
                    'band': band,
                    'album': album,
                    'spotify_url': spotify_url,
                    'spotify_image': spotify_image,
                    'bandcamp_url': bandcamp_url
                }
        return {
            'band': None,
            'album': None,
            'spotify_url': None,
            'spotify_image': None,
            'bandcamp_url': None
        }

    if st.button("Get Random Album"):
        with st.spinner(f"Finding a random album for {chosen_genre}..."):
            st.session_state.genre_data = get_new_album_data()

    if st.session_state.genre_data['band']:
        band = st.session_state.genre_data['band']
        album = st.session_state.genre_data['album']
        spotify_url = st.session_state.genre_data['spotify_url']
        spotify_image = st.session_state.genre_data['spotify_image']
        bandcamp_url = st.session_state.genre_data['bandcamp_url']

        st.subheader("Album Information:")
        st.write(f"**Band:** {band.name}")
        st.write(f"**Album:** {album.title}")

        if spotify_image:
            st.image(spotify_image, caption="Album Cover", width=300)

        if spotify_url:
            st.markdown(f'<a href="{spotify_url}" target="_blank" class="spotify-link">Listen on Spotify</a>', unsafe_allow_html=True)
        if bandcamp_url:
            st.markdown(f'<a href="{bandcamp_url}" target="_blank" class="bandcamp-link">Listen on Bandcamp</a>', unsafe_allow_html=True)
    else:
        st.info("Click 'Get Random Album' to find a random album in the chosen genre.")


# VARIABLES
RANDOM_MA_URL = "https://www.metal-archives.com/band/random"

# FUNCTIONS
def fetch_band_info(url):
    # OBTIENE INFORMACIÓN DE RANDOM ARTIST DE METAL-ARCHIVES
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')
    band_name_tag = soup.find('h1', class_='band_name')
    band_name = band_name_tag.text.strip() if band_name_tag else "Unknown"
    link = soup.find('h1', class_='band_name').find('a')
    url = link['href']

    details = {}
    for section in ['float_left', 'float_right']:
        info_section = soup.find('dl', class_=section)
        if info_section:
            for dt, dd in zip(info_section.find_all('dt'), info_section.find_all('dd')):
                details[dt.text.strip().strip(':')] = dd.text.strip()

    return {
        'Band Name': band_name,
        'Country of Origin': details.get('Country of origin', 'Unknown'),
        'Location': details.get('Location', 'Unknown'),
        'Genre': details.get('Genre', 'Unknown'),
        'Lyrical Themes': details.get('Themes', 'Unknown'),
        'Current Label': details.get('Current Label', 'Unknown'),
        'Status': details.get('Status', 'Unknown'),
        'M-A url': url
    }

def get_bandcamp_album_url(name):
    """
    Gets the Bandcamp album URL for a given band name.
    Args:
        name (str): The name of the band.
    Returns:
        str: The Bandcamp album URL, or an error message if not found.
    """
    search_query = f"{name}".replace(" ", "+")
    search_url = f"https://bandcamp.com/search?q={search_query}&item_type=a"  # item_type=a for albums
    try:
        response = requests.get(search_url)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')
        result_info = soup.find('li', class_='searchresult data-search')
        if result_info:
            album_url_tag = result_info.find('a', href=True)
            if album_url_tag:
                album_url = album_url_tag['href']
                url_modificada = album_url.split("?from")[0]
                return url_modificada
            else:
                return "Error: Album URL not found."
        else:
            return "Error: No search results found."
    except requests.exceptions.RequestException as e:
        # print(f"Error fetching Bandcamp search results: {e}")
        return "Error: Unable to fetch search results."

def extract_band_and_album_name(soup):
    """
    Extracts the band and album name from the Bandcamp page HTML.
    Args:
        soup (BeautifulSoup): The BeautifulSoup object representing the HTML content.
    Returns:
        tuple: A tuple containing the band name and album name. Returns None for either if not found.
    """
    try:
        album_name = soup.find('h2', class_='trackTitle').text.strip()
        band_name_element = soup.find('h3', style='margin:0px;').find('a')  # find the tag inside the h3 tag
        band_name = band_name_element.text.strip() if band_name_element else None  # extract the text
        return band_name, album_name
    except Exception as e:
        # print(f"Error extracting band and album name: {e}")
        return None, None

def extract_tags(soup):
    """
    Extracts the tags from the Bandcamp page HTML.
    Args:
        soup (BeautifulSoup): The BeautifulSoup object representing the HTML content.
    Returns:
        list: A list of strings representing the tags. Returns an empty list if no tags are found.
    """
    try:
        tag_elements = soup.find_all('a', class_='tag')
        tags = [tag.text.strip() for tag in tag_elements]
        return tags
    except Exception as e:
        # print(f"Error extracting tags: {e}")
        return []

def generate_embed_code(soup, url, album, band):
    """
    Generates a simple embed code for the album. This is a placeholder.
    """
    try:
        meta_tag = soup.find('meta', property='og:video')
        if meta_tag:
            url_embed = meta_tag['content']
            iframe = f'<iframe src="{url_embed}" width="400" height="400" seamless frameborder="0"></iframe>' #ORIGINAL
            #iframe = f'{album} by {band}'
            #iframe = iframe.replace('size-large/tracklist=true/artwork-small',
            #                        'linkcol=0f91ff/bgcol=333333/minimal=true/transparent=true')
            return iframe
        else:
            return None
    except Exception as e:
        # print(f"Error extracting embedded URL: {e}")
        return None

def main_bandcamp(url):
    """
    Fetches the HTML content from the specified URL, extracts the band name, album name,
    and tags using BeautifulSoup, and returns extracted information.
    """
    try:
        response = requests.get(url)
        response.raise_for_status()  # Raise HTTPError for bad responses (4xx or 5xx)
        html_content = response.text
    except requests.exceptions.RequestException as e:
        # print(f"Error fetching URL: {e}")
        return None, None, None, None

    soup = BeautifulSoup(html_content, 'html.parser')

    # Extract the band and album name
    band_name, album_name = extract_band_and_album_name(soup)

    # Extract the tags
    tags = extract_tags(soup)

    # Extract the embedded iframe
    iframe = generate_embed_code(soup, url, album_name, band_name)
    print(iframe)

    if not band_name or not album_name:
        #print("Could not extract band and/or album name.")
        return None, None, None, None

    return band_name, album_name, tags, iframe

def is_metal_band(tags):
    """
    Checks if the band is metal based on the tags.
    Args:
        tags (list): A list of tags.
    Returns:
        bool: True if the band is metal, False otherwise.
    """
    for tag in tags:
        if "metal" in tag.lower() or "grind" in tag.lower() or "death" in tag.lower() or "thrash" in tag.lower():
            return True
    return False

def get_random_metal_band_iframe():
    """
    Finds a random metal band on Metal-Archives, searches for it on Bandcamp,
    and extracts the embed code if it's a metal band.
    """
    while True:
        # print("Searching for a metal band...")
        random_band = fetch_band_info(RANDOM_MA_URL)
        if not random_band:
            # print("Failed to fetch band info. Retrying in 5 seconds...")
            time.sleep(5)
            continue

        # print(f"Found band on Metal-Archives: {random_band['Band Name']}")
        url_bandcamp = get_bandcamp_album_url(random_band['Band Name'])
        if "Error" in url_bandcamp or url_bandcamp is None:
            # print(f"Bandcamp search failed: {url_bandcamp}. Retrying...")
            time.sleep(2)
            continue

        # print(f"Found Bandcamp URL: {url_bandcamp}")
        bandcamp_name, bandcamp_album, bandcamp_tags, bandcamp_iframe = main_bandcamp(url_bandcamp)

        if not bandcamp_name or not bandcamp_album or not bandcamp_tags:
            # print("Failed to extract Bandcamp info. Retrying...")
            time.sleep(2)
            continue

        if is_metal_band(bandcamp_tags):
            # print("IT IS A METAL BAND!")
            embed_code = bandcamp_iframe
            # print("Embed Code:")
            # print(embed_code)
            return embed_code
        else:
            # print("Not a metal band. Retrying...")
            time.sleep(2)

def initialize_network(username, password):
    password_hash = pylast.md5(password)
    return pylast.LastFMNetwork(api_key=API_KEY, api_secret=API_SECRET,
                                 username=username, password_hash=password_hash)

def search_album(network, artist_name, album_name):
    results = network.search_for_album(album_name)
    if results:
        albums = results.get_next_page()
        if albums:
            closest_match = next((album for album in albums
                                   if album.artist.name.lower() == artist_name.lower()),
                                  albums[0])
            return closest_match
    return None

def scrobble_album(network, album):
    tracks = album.get_tracks()
    current_time = int(time.time())
    for track in tracks:
        network.scrobble(artist=album.artist.name, title=track.title, timestamp=current_time)
        current_time -= 300  # Subtract 5 minutes for each track
    return f"Scrobbled all tracks from {album.artist.name} - {album.title} to Last.fm"

def show_artist_info(album):
    artist = album.artist
    return f"Artist: {artist.name}\nBio: {artist.get_bio_summary()}"

def show_tracklist(album):
    tracks = [f"- {track.title}" for track in album.get_tracks()]
    return f"Tracklist for {album.artist.name} - {album.title}:\n" + "\n".join(tracks)

def show_similar_artists(album):
    similar = album.artist.get_similar()
    artists = [f"- {artist.name} (similarity: {similarity:.2f})" for artist, similarity in similar[:5]]
    return f"Similar artists to {album.artist.name}:\n" + "\n".join(artists)

# Main app logic
if app_mode == "Random Metal":
    random_metal()
elif app_mode == "Random Bandcamp":
    random_bandcamp()
elif app_mode == "Random New Release":
    random_recent_release()
elif app_mode == "Last.fm Manual Scrobbler":
    lastfm_scrobbler()
elif app_mode == "Random by Genres":
    lastfm_genre_explorer()
