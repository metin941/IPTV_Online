import requests
import sys

def extract_link_from_m3u8(file_path, channel_name):
    """Extracts the link for a specific channel from the M3U8 file."""
    try:
        with open(file_path, "r") as file:
            lines = file.readlines()

        # Loop through lines to find the channel name and the associated URL
        for i in range(len(lines)):
            if f'tvg-name="{channel_name}"' in lines[i]:  # Check for the channel name
                if i + 1 < len(lines):
                    # Extract the URL from the next line
                    return lines[i + 1].strip()  # Remove any extra whitespace

        print(f"Channel '{channel_name}' not found in the playlist.")
        return None
    except FileNotFoundError:
        print(f"File not found: {file_path}")
        return None


def is_m3u8_playable(url):
    """Checks if the M3U8 URL is playable by verifying if it returns a valid response."""
    try:
        # Send a GET request to the M3U8 URL with SSL verification disabled
        response = requests.get(url, timeout=10, verify=False)

        # Check if the response is valid and contains #EXTM3U
        if response.status_code == 200 and "#EXTM3U" in response.text:
            print("The M3U8 link is playable.")
            return True
        else:
            print("The M3U8 link is not playable or invalid.")
            return False
    except requests.exceptions.RequestException as e:
        print(f"Error checking M3U8 URL: {e}")
        return False


# Example usage
playlist_path = "playlist.m3u8"  # Assuming the playlist file is in the same directory
channel_name = "BNT1"  # Define the channel name here

# Extract the M3U8 URL from the playlist
m3u8_url = extract_link_from_m3u8(playlist_path, channel_name)

if m3u8_url:
    # Check if the extracted M3U8 URL is playable
    if is_m3u8_playable(m3u8_url):
        print(f"The stream for {channel_name} is Playable.")
    else:
        print(f"The stream for {channel_name} is Not Playable.")
        sys.exit(1)  # Exit with a non-zero status if the stream is not playable
else:
    print(f"Could not extract the URL for {channel_name}.")
    sys.exit(1)  # Exit with a non-zero status if the URL could not be extracted 
