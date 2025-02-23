<img src="https://r2cdn.perplexity.ai/pplx-full-logo-primary-dark%402x.png" class="logo" width="120"/>

# Random Metal Tools

---

Random Metal Tools is a comprehensive Streamlit application designed for metal music enthusiasts and researchers. This app provides a collection of tools to explore and discover metal bands, albums, and releases across various subgenres.

## Features

### Random Metal

- Retrieves a random entry from a curated CSV file of metal records.
- Displays band name, album title, genre, and album artwork.
- Provides a Spotify link when available.


### Random Metal Bandcamp

- Searches for a random band on Metal-Archives.
- Finds a record by that band on Bandcamp.
- Embeds the Bandcamp player for easy listening.


### Random Recent Release

- Scrapes the latest metal releases from Metalstorm.
- Retrieves random releases from the first 3 pages of new releases.
- Provides album information, artwork, and links to Spotify and Bandcamp when available.


### Random By Genres

- Allows users to select a specific metal subgenre.
- Fetches random bands from the chosen subgenre using Last.fm's API.
- Displays band and album information with Spotify and Bandcamp links when available.


### Last.fm Manual Scrobbler

- Enables users to log in to their Last.fm account.
- Allows manual scrobbling of albums.
- Provides additional features like showing artist information, album tracklists, and similar artists.


## Installation

1. Clone the repository:

```
git clone https://github.com/yourusername/random-metal-tools.git
```

2. Install the required dependencies:

```
pip install -r requirements.txt
```

3. Set up your API credentials:
    - Create a `.env` file in the root directory.
    - Add your Spotify and Last.fm API credentials:

```
SPOTIFY_CLIENT_ID=your_spotify_client_id
SPOTIFY_CLIENT_SECRET=your_spotify_client_secret
LASTFM_API_KEY=your_lastfm_api_key
LASTFM_API_SECRET=your_lastfm_api_secret
```


## Usage

Run the Streamlit app:

```
streamlit run app_main4.py
```

Navigate through the different tools using the sidebar menu.

## Data Sources

- Metal records: `metal_records.csv`
- 2025 metal releases: `releases2025.csv`


## Contributing

Contributions to Random Metal Tools are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

<div style="text-align: center">⁂</div>

[^1]: https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/49261571/333ffbfd-f22b-42b1-a41b-82bfa130d0e5/app_main4.py

[^2]: https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/collection_8f79228a-d8a8-409d-a005-757ea916a2eb/a51ba2ed-27cb-43d1-9999-ddf76ed63a70/metal_records.csv

[^3]: https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/collection_8f79228a-d8a8-409d-a005-757ea916a2eb/041815d4-9474-493e-98f9-df8dde665cdd/releases2025.csv

