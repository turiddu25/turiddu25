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
        resp = requests.get(url)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "html.parser")
        # Find the element containing the download count
        download_element = soup.find("li", class_="detail-downloads").find("span")
        return int(download_element.text.replace(",", "").strip())
    except Exception as e:
        print(f"Failed to scrape CurseForge downloads for {slug}: {e}")
        return 0

###############################################################################
# Main - Update README
###############################################################################

def update_readme():
    """Fetch downloads from both sources, combine them, and update README placeholders."""
    # 1) Read the current README file
    with open("README.md", "r", encoding="utf-8") as f:
        content = f.read()

    # 2) Get combined download counts for each mod
    # CobblePass
    cobblepass_modrinth_downloads = get_modrinth_downloads(MODRINTH_COBBLEPASS_SLUG)
    cobblepass_cf_downloads = scrape_curseforge_downloads(CF_COBBLEPASS_SLUG)
    cobblepass_total = cobblepass_modrinth_downloads + cobblepass_cf_downloads

    # SimpleDexRewards
    sdex_modrinth_downloads = get_modrinth_downloads(MODRINTH_SDEXREWARDS_SLUG)
    sdex_cf_downloads = scrape_curseforge_downloads(CF_SDEXREWARDS_SLUG)
    sdex_total = sdex_modrinth_downloads + sdex_cf_downloads

    # 3) Replace the placeholders in the README with the updated numbers
    content = re.sub(
        r"(<!-- COBBLEPASS_DOWNLOADS_PLACEHOLDER -->)(.*?)(<!-- /COBBLEPASS_DOWNLOADS_PLACEHOLDER -->)",
        f"\\1\n    {cobblepass_total}\n\\3",
        content,
        flags=re.DOTALL,
    )
    content = re.sub(
        r"(<!-- SIMPLEDEXREWARDS_DOWNLOADS_PLACEHOLDER -->)(.*?)(<!-- /SIMPLEDEXREWARDS_DOWNLOADS_PLACEHOLDER -->)",
        f"\\1\n    {sdex_total}\n\\3",
        content,
        flags=re.DOTALL,
    )

    # 4) Write the updated content back to the README
    with open("README.md", "w", encoding="utf-8") as f:
        f.write(content)

if __name__ == "__main__":
    update_readme()
