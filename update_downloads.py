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
    resp = requests.get(url)
    resp.raise_for_status()
    data = resp.json()
    return data.get("downloads", 0)

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
    # 1) Read the current README file
    try:
        with open("README.md", "r", encoding="utf-8") as f:
            content = f.read()
    except FileNotFoundError:
        print("Error: README.md not found. Please ensure the script is in the correct directory.")
        return

    # 2) Get combined download counts for each mod
    cobblepass_modrinth_downloads = get_modrinth_downloads(MODRINTH_COBBLEPASS_SLUG)
    cobblepass_cf_downloads = scrape_curseforge_downloads(CF_COBBLEPASS_SLUG)
    cobblepass_total = cobblepass_modrinth_downloads + cobblepass_cf_downloads

    sdex_modrinth_downloads = get_modrinth_downloads(MODRINTH_SDEXREWARDS_SLUG)
    sdex_cf_downloads = scrape_curseforge_downloads(CF_SDEXREWARDS_SLUG)
    sdex_total = sdex_modrinth_downloads + sdex_cf_downloads

    # --- START: CORRECTED CODE ---
    # This safer regex pattern prevents matching across other HTML comments,
    # avoiding the file corruption issue.
    # It looks for the start comment, then matches any character (`[\s\S]`)
    # as long as it's not the beginning of another comment (`(?!)[\s\S]*?()"
    sdex_pattern = r"()[\s\S]*?()"

    content = re.sub(cobblepass_pattern, create_replacement_string(cobblepass_total), content)
    content = re.sub(sdex_pattern, create_replacement_string(sdex_total), content)
    # --- END: CORRECTED CODE ---

    # 4) Write the updated content back to the README
    with open("README.md", "w", encoding="utf-8") as f:
        f.write(content)

    print("\nREADME update complete!")
    print(f"CobblePass Total Downloads: {cobblepass_total:,}")
    print(f"SimpleDexRewards Total Downloads: {sdex_total:,}")


if __name__ == "__main__":
    update_readme()
