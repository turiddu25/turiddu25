#!/usr/bin/env python3

import os
import re
import requests
from bs4 import BeautifulSoup

###############################################################################
# Configuration
###############################################################################

# For Modrinth, set your actual project slugs (from the URL)
MODRINTH_COBBLEPASS_SLUG = "cobble-pass"
MODRINTH_SDEXREWARDS_SLUG = "cobblemon-simpledexrewards"

# For CurseForge, set your project slugs (from the URL)
CF_COBBLEPASS_SLUG = "cobblemon-cobblepass"
CF_SDEXREWARDS_SLUG = "cobblemon-simpledexrewards"

###############################################################################
# Fetch Functions
###############################################################################

def get_modrinth_downloads(slug: str) -> int:
    """Fetch total downloads from Modrinth by project slug."""
    url = f"https://api.modrinth.com/v2/project/{slug}"
    print(f"Fetching Modrinth downloads from: {url}")
    try:
        resp = requests.get(url)
        resp.raise_for_status()
        data = resp.json()
        return data.get("downloads", 0)
    except requests.exceptions.RequestException as e:
        print(f"Failed to fetch Modrinth downloads for {slug}: {e}")
        return 0

def scrape_curseforge_downloads(slug: str) -> int:
    """Scrape total downloads from CurseForge by project slug."""
    url = f"https://www.curseforge.com/minecraft/mc-mods/{slug}"
    print(f"Scraping CurseForge downloads from: {url}")
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        resp = requests.get(url, headers=headers)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "html.parser")
        
        downloads_dt = soup.find('dt', string=lambda text: text and 'Downloads' in text)
        if downloads_dt:
            download_dd = downloads_dt.find_next_sibling('dd')
            if download_dd:
                return int(download_dd.text.replace(",", "").strip())
        
        print(f"Could not find download count for {slug}.")
        return 0
    except Exception as e:
        print(f"Failed to scrape CurseForge downloads for {slug}: {e}")
        return 0

###############################################################################
# Main - Update README
###############################################################################

def update_readme():
    """Fetch downloads from both sources, combine them, and update README placeholders."""
    try:
        with open("README.md", "r", encoding="utf-8") as f:
            content = f.read()
    except FileNotFoundError:
        print("Error: README.md not found. Please ensure the script is in the correct directory.")
        return

    # Get combined download counts
    cobblepass_total = get_modrinth_downloads(MODRINTH_COBBLEPASS_SLUG) + scrape_curseforge_downloads(CF_COBBLEPASS_SLUG)
    sdex_total = get_modrinth_downloads(MODRINTH_SDEXREWARDS_SLUG) + scrape_curseforge_downloads(CF_SDEXREWARDS_SLUG)

    # --- START: CORRECTED CODE ---
    # This helper function replaces the content between the placeholder tags.
    def get_updated_content(existing_content, placeholder_name, total_downloads):
        # Using an f-string to build the pattern on a single line avoids indentation errors.
        # This safer regex uses a negative lookahead `(?!)((?:(?!)"
        pattern = re.compile(pattern_string, re.IGNORECASE)

        # The new content to insert, matching your README's formatting.
        new_inner_content = f"\n\n\n      {total_downloads:,}\n\n    "
        
        # We replace the middle part (group 2) and put back the comment tags (groups 1 and 3).
        replacement_string = f"\\1{new_inner_content}\\3"
        
        return pattern.sub(replacement_string, existing_content)
    # --- END: CORRECTED CODE ---

    content = get_updated_content(content, "COBBLEPASS_DOWNLOADS_PLACEHOLDER", cobblepass_total)
    content = get_updated_content(content, "SIMPLEDEXREWARDS_DOWNLOADS_PLACEHOLDER", sdex_total)
    
    with open("README.md", "w", encoding="utf-8") as f:
        f.write(content)

    print("\nREADME update complete!")
    print(f"CobblePass Total Downloads: {cobblepass_total:,}")
    print(f"SimpleDexRewards Total Downloads: {sdex_total:,}")

if __name__ == "__main__":
    update_readme()
