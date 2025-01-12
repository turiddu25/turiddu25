#!/usr/bin/env python3

import os
import re
import requests
import json

###############################################################################
# Configuration - FILL THESE IN!
###############################################################################
CF_API_TOKEN = os.environ.get("CF_API_TOKEN", "").strip()

# For Modrinth, set your actual project slugs (from the URL)
MODRINTH_COBBLEPASS_SLUG = "cobble-pass"  # e.g., from https://modrinth.com/mod/cobble-pass
MODRINTH_SDEXREWARDS_SLUG = "cobblemon-simpledexrewards"


# For CurseForge, set your numeric project IDs (verify these are the correct IDs from your project's management page)
CF_COBBLEPASS_ID = 1176631    # Replace with the actual numeric ID for CobblePass
CF_SDEXREWARDS_ID = 1174859   # Replace with the actual numeric ID for SimpleDexRewards


###############################################################################
# API Endpoints
###############################################################################

MODRINTH_API_BASE = "https://api.modrinth.com/v2/project/"
CURSEFORGE_API_BASE = "https://api.curseforge.com/v1/mods/"

###############################################################################
# Fetch Functions
###############################################################################

def get_modrinth_downloads(slug: str) -> int:
    """Fetch total downloads from Modrinth by project slug."""
    url = MODRINTH_API_BASE + slug
    print(f"Fetching Modrinth downloads from: {url}")
    resp = requests.get(url)
    resp.raise_for_status()
    data = resp.json()
    # The v2 API returns a "downloads" field
    return data.get("downloads", 0)

def get_curseforge_downloads(project_id: int) -> int:
     """
#     Fetch total downloads from CurseForge by numeric project ID
#     using the modern v1 API.
     """
     headers = {
         "X-Api-Token": CF_API_TOKEN,
         "Accept": "application/json"
     }
     url = f"{CURSEFORGE_API_BASE}{project_id}"
     print(f"Fetching CurseForge downloads from: {url}")
     resp = requests.get(url, headers=headers)
     print("Response status:", resp.status_code)
     print("Response body:", resp.text)
     resp.raise_for_status()  # This will raise an HTTPError if the status is 4xx/5xx
     data = resp.json()  # Expected structure: { "data": { "id": ..., "downloadCount": ..., ... } }
     return int(data["data"]["downloadCount"])

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
    cobblepass_cf_downloads = get_curseforge_downloads(CF_COBBLEPASS_ID)
    cobblepass_total = cobblepass_modrinth_downloads + cobblepass_cf_downloads
    
    # SimpleDexRewards
    sdex_modrinth_downloads = get_modrinth_downloads(MODRINTH_SDEXREWARDS_SLUG)
    sdex_cf_downloads = get_curseforge_downloads(CF_SDEXREWARDS_ID)
    sdex_total = sdex_modrinth_downloads + sdex_cf_downloads
    
    # 3) Replace the placeholders in the README with the updated numbers
    content = re.sub(
        r"(<!-- COBBLEPASS_DOWNLOADS_PLACEHOLDER -->)(.*?)(<!-- /COBBLEPASS_DOWNLOADS_PLACEHOLDER -->)",
        f"\\1\n{cobblepass_total}\n\\3",
        content,
        flags=re.DOTALL
    )
    content = re.sub(
        r"(<!-- SIMPLEDEXREWARDS_DOWNLOADS_PLACEHOLDER -->)(.*?)(<!-- /SIMPLEDEXREWARDS_DOWNLOADS_PLACEHOLDER -->)",
        f"\\1\n{sdex_total}\n\\3",
        content,
        flags=re.DOTALL
    )
    
    # 4) Write the updated content back to the README
    with open("README.md", "w", encoding="utf-8") as f:
        f.write(content)

if __name__ == "__main__":
    update_readme()
