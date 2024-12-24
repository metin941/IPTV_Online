import requests
import urllib3
from urllib.parse import urlparse, parse_qs

# Suppress InsecureRequestWarning
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# M3U8 URL
url = "https://ymkaya.xyz:48234/tv/kinonova/playlist.m3u8"

try:
    response = requests.get(url, verify=False)  # Disable SSL verification (not recommended for production)
    response.raise_for_status()
    m3u8_data = response.text
    print("M3U8 Playlist Data:")
    print(m3u8_data)

    # Look for the token in the URL (example: chunks.m3u8?nimblesessionid=304431)
    lines = m3u8_data.splitlines()
    for line in lines:
        if "nimblesessionid" in line:
            # Extract the URL with the token
            segment_url = line.strip()
            # Parse the query string
            parsed_url = urlparse(segment_url)
            query_params = parse_qs(parsed_url.query)
            
            # Extract the token (nimblesessionid)
            token = query_params.get("nimblesessionid", [None])[0]
            if token:
                print(f"Found token: {token}")
            else:
                print("Token not found.")

except requests.exceptions.RequestException as e:
    print(f"Error fetching M3U8 playlist: {e}")
