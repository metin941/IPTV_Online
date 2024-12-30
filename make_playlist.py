#!/usr/bin/python3

import os
import re
import requests
from urllib.parse import urlparse, parse_qs
import urllib3
import logging
import time

# Enable logging for HTTP requests made via the 'requests' library
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger()

EPG_LIST = open('epglist.txt', "r")  # for a clean code

class Channel:
    def __init__(self, group, md_line):
        self.group = group
        md_line = md_line.strip()
        parts = md_line.split("|")
        self.number = parts[1].strip()
        self.name = parts[2].strip()
        self.url = parts[3].strip()
        self.url = self.url[self.url.find("(")+1:self.url.rfind(")")]
        self.logo = parts[4].strip()
        self.logo = self.logo[self.logo.find('src="')+5:self.logo.rfind('"')]
        if len(parts) > 6:
            self.epg = parts[5].strip()
        else:
            self.epg = None

        # Extract token if possible
        self.token = self.extract_token(self.url)
        if self.token:
            self.url += f"nimblesessionid={self.token}"

    def extract_token(self, url):
        """Extract the token from the URL."""
        try:
            urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
            
            # Log the URL and request details
            logger.debug(f"Sending GET request to: {url}")
            
            response = requests.get(url, verify=False)
            
            # Log request details
            logger.debug(f"Request Method: GET")
            logger.debug(f"Request URL: {url}")
            logger.debug(f"Request Headers: {response.request.headers}")
            logger.debug(f"Request Body: None (GET does not have a body)")

            # Log response details
            logger.debug(f"Response Status Code: {response.status_code}")
            logger.debug(f"Response Body: {response.text[:100]}...")  # Printing part of the response body for brevity

            response.raise_for_status()
            m3u8_data = response.text
            for line in m3u8_data.splitlines():
                if "nimblesessionid" in line:
                    parsed_url = urlparse(line.strip())
                    query_params = parse_qs(parsed_url.query)
                    token = query_params.get("nimblesessionid", [None])[0]
                    logger.debug(f"Extracted nimblesessionid token: {token}")
                    return token
            return None
        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching M3U8 playlist: {e}")
            return None

    def to_m3u_line(self):
        if self.epg is None:
            return (f'#EXTINF:-1 tvg-name="{self.name}" tvg-logo="{self.logo}" group-title="{self.group}",{self.name}\n{self.url}')
        else:
            return (f'#EXTINF:-1 tvg-name="{self.name}" tvg-logo="{self.logo}" tvg-id="{self.epg}" group-title="{self.group}",{self.name}\n{self.url}')

    def fetch_url_with_token(self):
        """Fetch the URL with the extracted token and handle errors."""
        full_url = f"{self.url}?nimblesessionid={self.token}"
        headers = {'User-Agent': 'python-requests/2.32.3'}

        logger.debug(f"Sending GET request to: {full_url}")
        response = requests.get(full_url, headers=headers, verify=False)

        # Log request details
        logger.debug(f"Request Method: GET")
        logger.debug(f"Request URL: {full_url}")
        logger.debug(f"Request Headers: {headers}")
        logger.debug(f"Request Body: None (GET does not have a body)")

        # Log response details
        logger.debug(f"Response Status Code: {response.status_code}")
        logger.debug(f"Response Body: {response.text[:100]}...")  # Only print part of the body for debugging

        if response.status_code == 200:
            logger.debug("Request successful.")
        elif response.status_code == 403:
            logger.error("Token is invalid or expired.")
        elif response.status_code == 401:
            logger.error("Unauthorized access, check token or permissions.")
        else:
            logger.error(f"Error: {response.status_code}, {response.text}")

def main():
    dir_playlists = 'playlists'
    if not os.path.isdir(dir_playlists):
        os.mkdir(dir_playlists)
    
    with open("playlist.m3u8", "w", encoding='utf-8') as playlist:
        processed_epg_list = ", ".join(EPG_LIST).replace('\n', '')
        head_playlist = f'#EXTM3U x-tvg-url="{processed_epg_list}"'
        print(f'#EXTM3U x-tvg-url="{processed_epg_list}"', file=playlist)
        os.chdir("lists")
        
        for filename in sorted(os.listdir(".")):
            if filename == "README.md" or not filename.endswith(".md"):
                continue
            with open(filename, encoding='utf-8') as markup_file:
                file_country = os.path.join("..", dir_playlists, "playlist_" + filename[:-3:] + ".m3u8")
                playlist_country = open(file_country, "w", encoding='utf-8')
                playlist_country.write(head_playlist + "\n")
                group = filename.replace(".md", "").title()
                logger.info(f"Generating {group}")
                for line in markup_file:
                    if "<h1>" in line.lower() and "</h1>" in line.lower():
                        group = re.sub('<[^<>]+>', '', line.strip())
                    if not "[>]" in line:
                        continue
                    channel = Channel(group, line)
                    print(channel.to_m3u_line(), file=playlist)
                    print(channel.to_m3u_line(), file=playlist_country)

                    # Example of how to fetch the URL with token after it's added to the URL
                    if channel.token:
                        channel.fetch_url_with_token()

                playlist_country.close()

if __name__ == "__main__":
    main()
