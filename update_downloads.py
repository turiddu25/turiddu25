#!/usr/bin/env python3

import os
import re
import requests
import json

###############################################################################
# Configuration - FILL THESE IN!
###############################################################################

# CurseForge token will be read from an environment variable "CF_API_TOKEN"
# (You will store this token as a GitHub Secret)
CF_API_TOKEN = os.environ.get("CF_API_TOKEN", "")

# For Modrinth, set your actual project slugs
MODRINTH_COBBLEPASS_SLUG = "cobble-pass"  # e.g. "cobble-pass"
MODRINTH_SDEXREWARDS_SLUG = "cobblemon-simpledexrewards"

# For CurseForge, set your numeric project IDs
CF_COBBLEPASS_ID = 1176631    # <-- Replace with the actual ID
CF_SDEXREWARDS_ID = 1174859   # <-- Replace with the actual ID

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
    resp = requests.get(url)
    resp.raise_for_status()
    data = resp.json()
    return data.get("downloads", 0)

def get_curseforge_downloads(project_id: int) -> int:
    """
    Fetch total downloads from CurseForge by numeric project ID
    using the modern v1 API (https://api.curseforge.com).
    """
    headers = {
        "X-Api-Token": CF_API_TOKEN
    }
    url = f"{CURSEFORGE_API_BASE}{project_id}"
    resp = requests.get(url, headers=headers)
    resp.raise_for_status()
    data = resp.json()  # { "data": { "id": X, "downloadCount": 42, ... } }
    return int(data["data"]["downloadCount"])

###############################################################################
# Main - Update README
###############################################################################

def update_readme():
    """Fetch downloads, sum them, and replace placeholders in README.md."""
    
    # 1) Read current README
    with open("README.md", "r", encoding="utf-8") as f:
        content = f.read()
    
    # 2) Get combined download counts
    # CobblePass
    cobblepass_modrinth_downloads = get_modrinth_downloads(MODRINTH_COBBLEPASS_SLUG)
    cobblepass_cf_downloads = get_curseforge_downloads(CF_COBBLEPASS_ID)
    cobblepass_total = cobblepass_modrinth_downloads + cobblepass_cf_downloads
    
    # SimpleDexRewards
    sdex_modrinth_downloads = get_modrinth_downloads(MODRINTH_SDEXREWARDS_SLUG)
    sdex_cf_downloads = get_curseforge_downloads(CF_SDEXREWARDS_ID)
    sdex_total = sdex_modrinth_downloads + sdex_cf_downloads
    
    # 3) Replace placeholders in the README
    #    Looks for blocks:
    #      <!-- COBBLEPASS_DOWNLOADS_PLACEHOLDER --> ... <!-- /COBBLEPASS_DOWNLOADS_PLACEHOLDER -->
    #      <!-- SIMPLEDEXREWARDS_DOWNLOADS_PLACEHOLDER --> ... <!-- /SIMPLEDEXREWARDS_DOWNLOADS_PLACEHOLDER -->
    
    # CobblePass
    content = re.sub(
        r"(<!-- COBBLEPASS_DOWNLOADS_PLACEHOLDER -->)(.*?)(<!-- /COBBLEPASS_DOWNLOADS_PLACEHOLDER -->)",
        f"\\1\n{cobblepass_total}\n\\3",
        content,
        flags=re.DOTALL
    )
    
    # SimpleDexRewards
    content = re.sub(
        r"(<!-- SIMPLEDEXREWARDS_DOWNLOADS_PLACEHOLDER -->)(.*?)(<!-- /SIMPLEDEXREWARDS_DOWNLOADS_PLACEHOLDER -->)",
        f"\\1\n{sdex_total}\n\\3",
        content,
        flags=re.DOTALL
    )
    
    # 4) Write the updated README back
    with open("README.md", "w", encoding="utf-8") as f:
        f.write(content)

if __name__ == "__main__":
    update_readme()
