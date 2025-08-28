import requests
import sys
from urllib.parse import urlparse
import os

def debug_print(*args, **kwargs):
    """Print debug information to stderr"""
    print(*args, file=sys.stderr, **kwargs)

def download_playlist(url):
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.text
    except requests.RequestException as e:
        print(f"Error downloading {url}: {e}")
        return None

def extract_streams(playlist_content, url):
    if not playlist_content:
        debug_print(f"No content received from {url}")
        return set()
    
    lines = [line.strip() for line in playlist_content.split('\n') if line.strip()]
    debug_print(f"Processing {len(lines)} lines from {url}")
    
    streams = set()
    i = 0
    while i < len(lines):
        line = lines[i]
        if line.startswith('#EXTINF'):
            if i + 1 < len(lines) and not lines[i+1].startswith('#'):
                stream_url = lines[i+1].strip()
                if stream_url and (stream_url.startswith('http://') or stream_url.startswith('https://')):
                    streams.add((line, stream_url))
                    i += 2
                    continue
                else:
                    debug_print(f"Skipping invalid URL at line {i+2}: {stream_url}")
        i += 1
    
    debug_print(f"Extracted {len(streams)} valid streams from {url}")
    return streams

def merge_playlists(urls):
    all_streams = set()
    
    for url in urls:
        debug_print(f"\nProcessing {url}...")
        content = download_playlist(url)
        if content:
            streams = extract_streams(content, url)
            debug_print(f"  - Found {len(streams)} valid streams in {url}")
            all_streams.update(streams)
            debug_print(f"  - Total unique streams so far: {len(all_streams)}")
    
    return all_streams
    
    return all_streams

def save_merged_playlist(streams, output_file):
    debug_print(f"\nSaving {len(streams)} streams to {output_file}")
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("#EXTM3U\n")
        for extinf, url in sorted(streams, key=lambda x: x[0].lower()):
            f.write(f"{extinf}\n{url}\n")
    debug_print(f"Successfully saved {output_file}")
    
    # Verify the file was written correctly
    try:
        with open(output_file, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            debug_print(f"File contains {len(lines)} lines")
            if len(lines) > 1:
                debug_print("First few lines:")
                for line in lines[:4]:
                    debug_print(line.strip())
    except Exception as e:
        debug_print(f"Error reading back the output file: {e}")

def main():
    playlist_urls = [
        "https://www.apsattv.com/uslg.m3u",
        "https://www.apsattv.com/calg.m3u",
        "https://www.apsattv.com/nzlg.m3u"
    ]
    
    output_file = "merged_playlist.m3u"
    
    print("Starting to merge playlists...")
    try:
        merged_streams = merge_playlists(playlist_urls)
        
        print(f"\nTotal unique streams found: {len(merged_streams)}")
        print(f"Saving to {output_file}...")
        save_merged_playlist(merged_streams, output_file)
        
        # Verify the output file
        if os.path.exists(output_file):
            with open(output_file, 'r', encoding='utf-8') as f:
                lines = f.readlines()
                if len(lines) <= 1:
                    print("\nWARNING: Output file was created but appears to be empty or only contains the header.")
                    print("Check the debug output above for any errors.")
                else:
                    print(f"\nSuccess! Merged playlist saved to {output_file}")
                    print(f"Total entries: {len(merged_streams)}")
        else:
            print("\nERROR: Failed to create output file. Check file permissions and disk space.")
            
    except Exception as e:
        print(f"\nERROR: An error occurred: {str(e)}", file=sys.stderr)
        import traceback
        debug_print("\nTraceback:")
        debug_print(traceback.format_exc())
        sys.exit(1)

if __name__ == "__main__":
    main()
