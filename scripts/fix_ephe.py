import os
import sys
import urllib.request
import ssl
from pathlib import Path

# Base directory
BASE_DIR = Path(__file__).resolve().parent.parent
EPHE_DIR = BASE_DIR / "ephe"

# GitHub mirror for Swiss Ephemeris files
# Using aloistr/swisseph which is the official repo
BASE_URL = "https://github.com/aloistr/swisseph/raw/master/ephe"

def log(msg):
    print(msg, flush=True)

def get_ssl_context():
    try:
        import certifi
        return ssl.create_default_context(cafile=certifi.where())
    except ImportError:
        return ssl.create_default_context()

def download_file(filename):
    url = f"{BASE_URL}/{filename}"
    dest = EPHE_DIR / filename
    
    log(f"Downloading {filename}...")
    try:
        context = get_ssl_context()
        with urllib.request.urlopen(url, context=context) as response, open(dest, 'wb') as out_file:
            data = response.read()
            out_file.write(data)
            
        # Verify it's not a small HTML file (corruption check)
        if dest.stat().st_size < 10000:
            with open(dest, 'r', errors='ignore') as f:
                content = f.read(100)
                if "<html" in content.lower() or "<!doctype" in content.lower():
                    log(f"Error: Downloaded file {filename} seems to be HTML (404?). Deleting.")
                    dest.unlink()
                    return False
        
        log(f"Successfully downloaded {filename} ({dest.stat().st_size} bytes)")
        return True
    except Exception as e:
        log(f"Failed to download {filename}: {e}")
        if dest.exists():
            dest.unlink()
        return False

def main():
    if not EPHE_DIR.exists():
        EPHE_DIR.mkdir(parents=True)
        
    # 1. Identify and remove corrupted files
    log("Scanning for corrupted files...")
    corrupted_count = 0
    for f in EPHE_DIR.glob("*.se1"):
        # Files that are exactly 2629 bytes or very small are likely corrupted HTML
        if f.stat().st_size < 3000:
            try:
                with open(f, 'r', errors='ignore') as f_obj:
                    header = f_obj.read(50)
                    if "<html" in header.lower() or "<!doctype" in header.lower():
                        log(f"Removing corrupted file: {f.name}")
                        f.unlink()
                        corrupted_count += 1
            except Exception as e:
                log(f"Error checking {f.name}: {e}")
    
    log(f"Removed {corrupted_count} corrupted files.")
    
    # 2. List of files we likely need
    # We need sepl (planets) and semo (moon) files
    # Ranges: 
    # _00 to _96 (0 to 9600 AD? No, numbering is century based usually but let's check)
    # Actually:
    # sepl_00.se1 -> 0 AD - 600 AD
    # sepl_06.se1 -> 600 AD - 1200 AD
    # sepl_12.se1 -> 1200 AD - 1800 AD
    # sepl_18.se1 -> 1800 AD - 2400 AD
    # sepl_24.se1 -> 2400 AD - 3000 AD
    # ...
    # sepl_78.se1 -> 7800 AD - 8400 AD (Needed for 8000 CE)
    #
    # Also negative years:
    # seplm06.se1 -> -600 to 0
    # seplm12.se1 -> -1200 to -600
    
    # Let's try to download the missing ones that were corrupted
    # We'll focus on the ones that were likely deleted
    
    # Generate list of likely files
    prefixes = ["sepl", "semo"]
    
    # Positive years: 00 to 168 (covers up to 17400 CE)
    # sepl_168.se1 covers 16800-17400
    suffixes = [f"{i:02d}" for i in range(0, 174, 6)]
    
    # Negative years: m06 to m138 (covers back to 13800 BCE)
    # seplm138.se1 covers -13800 to -13200
    suffixes_m = [f"m{i:02d}" for i in range(6, 144, 6)]
    
    all_suffixes = suffixes + suffixes_m
    
    for prefix in prefixes:
        for suffix in all_suffixes:
            filename = f"{prefix}_{suffix}.se1"
            if "m" in suffix:
                filename = f"{prefix}{suffix}.se1"
                
            file_path = EPHE_DIR / filename
            if not file_path.exists():
                log(f"Missing {filename}, attempting download...")
                download_file(filename)
            else:
                # log(f"Found {filename}")
                pass

if __name__ == "__main__":
    main()
