import os
import yt_dlp
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import pandas as pd
from datetime import datetime
import requests
import subprocess
import pyperclip
from tqdm import tqdm
from urllib.parse import urlparse
import re
import uuid

class YouTubeVideoDownloader:
    def __init__(self, use_selenium=True, cookies_path=None, cookies_file=None):
        self.use_selenium = use_selenium
        self.cookies_path = cookies_path
        self.cookies_file = cookies_file
        self.driver = None
        self.ydl_opts = {
            'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
            'noplaylist': True,
            'quiet': True,
            'no_warnings': True,
            'merge_output_format': 'mp4',
        }
        if cookies_file and os.path.exists(cookies_file):
            self.ydl_opts['cookiefile'] = cookies_file
        if use_selenium:
            self._init_selenium()

    def _init_selenium(self):
        """Initialize Selenium WebDriver."""
        chrome_options = Options()
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--enable-javascript")
        chrome_options.add_argument(
            "--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        if self.cookies_path:
            chrome_options.add_argument(f"--user-data-dir={self.cookies_path}")
        try:
            self.driver = webdriver.Chrome(options=chrome_options)
            self.driver.execute_cdp_cmd('Network.enable', {})
            self.driver.execute_cdp_cmd('Page.enable', {})
        except Exception as e:
            print(f"Failed to initialize Selenium driver: {e}")
            self.use_selenium = False

    def close(self):
        """Close Selenium WebDriver."""
        if self.driver:
            self.driver.quit()

    def extract_video_info(self, url):
        """Extract video information using yt-dlp and Selenium."""
        video_info = {"url": url}
        try:
            with yt_dlp.YoutubeDL(self.ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)
                video_info.update({
                    "video_id": info.get("id", ""),
                    "title": info.get("title", "Unknown Title"),
                    "channel": info.get("uploader", "Unknown Channel"),
                    "view_count": str(info.get("view_count", 0)),
                    "formats": [{
                        "url": fmt.get("url", ""),
                        "quality": fmt.get("format_note", "unknown"),
                        "resolution": f"{fmt.get('width', 0)}x{fmt.get('height', 0)}",
                        "fps": fmt.get("fps", 0),
                        "content_length": fmt.get("filesize", 0),
                        "mime_type": fmt.get("ext", "mp4")
                    } for fmt in info.get("formats", []) if fmt.get("ext") == "mp4" and fmt.get("vcodec") != "none"]
                })
        except Exception as e:
            error_msg = str(e).lower()
            if "sign in" in error_msg or "members-only" in error_msg:
                video_info["error"] = "This is a members-only video. Please provide a cookies file or log in."
            else:
                video_info["error"] = f"yt-dlp extraction failed: {str(e)}"

        # Use Selenium for restricted content if needed
        if "error" in video_info and self.use_selenium and self.driver:
            try:
                self.driver.get(url)
                time.sleep(5)  # Wait for page load
                # Check for restricted content
                try:
                    error_message = self.driver.find_element(By.CSS_SELECTOR, "yt-formatted-string.ytd-player-error-message-renderer")
                    if "private" in error_message.text.lower() or "member" in error_message.text.lower():
                        return {"error": "This video is private or members-only. Please provide a cookies file or log in."}
                except:
                    pass
                # Extract title and channel
                try:
                    title = WebDriverWait(self.driver, 5).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, "h1.title yt-formatted-string"))
                    ).text
                except:
                    title = "Unknown Title"
                try:
                    channel = self.driver.find_element(By.CSS_SELECTOR, "#channel-name a").text
                except:
                    channel = "Unknown Channel"
                video_info.update({
                    "title": title,
                    "channel": channel,
                    "video_id": self._extract_video_id(url),
                    "view_count": "0"
                })
                # Retry yt-dlp with cookies if available
                if self.cookies_file:
                    with yt_dlp.YoutubeDL(self.ydl_opts) as ydl:
                        info = ydl.extract_info(url, download=False)
                        video_info["formats"] = [{
                            "url": fmt.get("url", ""),
                            "quality": fmt.get("format_note", "unknown"),
                            "resolution": f"{fmt.get('width', 0)}x{fmt.get('height', 0)}",
                            "fps": fmt.get("fps", 0),
                            "content_length": fmt.get("filesize", 0),
                            "mime_type": fmt.get("ext", "mp4")
                        } for fmt in info.get("formats", []) if fmt.get("ext") == "mp4" and fmt.get("vcodec") != "none"]
            except Exception as e:
                video_info["error"] = f"Selenium extraction failed: {str(e)}"
        return video_info

    def _extract_video_id(self, url):
        """Extract YouTube video ID from URL."""
        video_id_match = re.search(r"(?:v=|youtu\.be/|embed/|shorts/)([0-9A-Za-z_-]{11})", url)
        if video_id_match:
            return video_id_match.group(1)
        if "youtu.be" in url:
            path = urlparse(url).path
            video_id = path.strip("/").split("?")[0]
            if len(video_id) == 11 and re.match(r"[0-9A-Za-z_-]{11}", video_id):
                return video_id
        return None

    def get_mp4_urls(self, video_info):
        """Filter playable MP4 URLs."""
        if "error" in video_info:
            return []
        mp4_urls = []
        for fmt in video_info.get("formats", []):
            if fmt["mime_type"] == "mp4" and fmt["url"]:
                mp4_urls.append({
                    "url": fmt["url"],
                    "quality": fmt["quality"],
                    "resolution": fmt["resolution"],
                    "fps": fmt["fps"],
                    "size_mb": round(fmt["content_length"] / (1024 * 1024), 2) if fmt["content_length"] else 0
                })
        return sorted(mp4_urls, key=lambda x: self._get_quality_score(x["quality"]), reverse=True)

    def _get_quality_score(self, quality):
        """Assign a score to quality for sorting."""
        if not quality:
            return 0
        quality = str(quality).lower()
        if "2160p" in quality or "4k" in quality:
            return 5
        elif "1440p" in quality or "2k" in quality:
            return 4
        elif "1080p" in quality:
            return 3
        elif "720p" in quality:
            return 2
        elif "480p" in quality:
            return 1
        return 0

    def download_video(self, url, filename=None, output_path="youtube_video"):
        """Download video from URL to youtube_video folder."""
        if not url:
            print("No URL provided for download.")
            return False
        if not os.path.exists(output_path):
            os.makedirs(output_path)
        if not filename:
            filename = f"youtube_{datetime.now().strftime('%Y%m%d_%H%M%S')}.mp4"
        if not filename.lower().endswith('.mp4'):
            filename += '.mp4'
        file_path = os.path.join(output_path, filename)
        try:
            print(f"\nDownloading '{filename}' to '{output_path}'...")
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                "Referer": "https://www.youtube.com/"
            }
            with requests.get(url, headers=headers, stream=True) as response:
                response.raise_for_status()
                total_size = int(response.headers.get('content-length', 0))
                with open(file_path, 'wb') as f, tqdm(
                    desc=filename,
                    total=total_size,
                    unit='B',
                    unit_scale=True,
                    unit_divisor=1024,
                ) as progress_bar:
                    for chunk in response.iter_content(chunk_size=8192):
                        if chunk:
                            f.write(chunk)
                            progress_bar.update(len(chunk))
            print(f"\nDownload completed: {file_path}")
            return file_path
        except Exception as e:
            print(f"Download failed: {str(e)}")
            if os.path.exists(file_path):
                os.remove(file_path)
            return False

    def play_in_external_player(self, url, player_path=None):
        """Play video URL in an external player."""
        if not url:
            print("No URL provided for playback.")
            return False
        try:
            if player_path:
                subprocess.run([player_path, url], check=True)
            else:
                import webbrowser
                webbrowser.open(url)
            print("Playing video in external player...")
            return True
        except Exception as e:
            print(f"Failed to play video: {str(e)}")
            return False

    def save_to_csv(self, video_info, filename=None):
        """Save video info to CSV."""
        if "error" in video_info:
            print("No valid video info to save.")
            return
        if not filename:
            filename = f"youtube_video_info_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        data = {
            "Video ID": video_info.get("video_id", ""),
            "Title": video_info.get("title", ""),
            "Channel": video_info.get("channel", ""),
            "View Count": video_info.get("view_count", "0"),
            "URL": video_info.get("url", ""),
            "Formats": "; ".join([f"{fmt['quality']} ({fmt['resolution']})" for fmt in video_info.get("formats", [])])
        }
        df = pd.DataFrame([data])
        os.makedirs("youtube_video", exist_ok=True)
        df.to_csv(os.path.join("youtube_video", filename), index=False, encoding='utf-8-sig')
        print(f"Video info saved to youtube_video/{filename}")

def main():
    print("YouTube Video Downloader and URL Extractor")
    print("1. Extract and download single video")
    print("2. Access members-only content")
    choice = input("Select an option (1/2): ")

    use_selenium = False
    cookies_path = None
    cookies_file = None

    if choice == "2":
        use_selenium = True
        print("\nMembers-only content requires authentication.")
        cookies_file = input("Enter path to cookies file (optional, press Enter to skip): ").strip() or None
        if not cookies_file:
            cookies_path = input("Enter browser profile path for saved cookies (optional): ").strip() or None
            if not cookies_path:
                print("No cookies provided. You'll need to log in manually.")
    elif choice == "1":
        cookies_file = input("Enter path to cookies file for authentication (optional, press Enter to skip): ").strip() or None
        selenium_option = input("Use Selenium for better URL extraction? (y/n): ").lower()
        if selenium_option == 'y':
            use_selenium = True
            cookies_path = input("Enter browser profile path for saved cookies (optional): ").strip() or None

    downloader = YouTubeVideoDownloader(use_selenium=use_selenium, cookies_path=cookies_path, cookies_file=cookies_file)

    try:
        if choice == "2" and use_selenium and not cookies_file and not cookies_path:
            print("\nLogging into YouTube...")
            downloader.driver.get("https://www.youtube.com/signin")
            print("Please log in manually in the browser. Press Enter when done...")
            input()
            # Save cookies for future use
            cookies_file = os.path.join("youtube_video", "youtube_cookies.txt")
            os.makedirs("youtube_video", exist_ok=True)
            with open(cookies_file, "w") as f:
                f.write("# Netscape HTTP Cookie File\n")
                for cookie in downloader.driver.get_cookies():
                    f.write(f"{cookie['domain']}\tTRUE\t{cookie['path']}\t{cookie['secure']}\t{cookie['expiry'] if 'expiry' in cookie else 0}\t{cookie['name']}\t{cookie['value']}\n")
            print(f"Cookies saved to {cookies_file}")

        url = input("Enter YouTube video URL: ")
        print("\nExtracting video information...")
        video_info = downloader.extract_video_info(url)

        print("\n--- Video Information ---")
        if "error" in video_info:
            print(f"Error: {video_info['error']}")
            if "members-only" in video_info["error"]:
                print("To download members-only videos, provide a cookies file exported from your browser.")
                print("You can export cookies using a browser extension like 'EditThisCookie'.")
            return
        print(f"Title: {video_info.get('title', 'Unknown')}")
        print(f"Channel: {video_info.get('channel', 'Unknown')}")
        print(f"View Count: {video_info.get('view_count', 'Unknown')}")

        mp4_urls = downloader.get_mp4_urls(video_info)
        if mp4_urls:
            print("\nAvailable MP4 Formats:")
            for i, mp4 in enumerate(mp4_urls):
                size_info = f", Size: {mp4['size_mb']}MB" if mp4['size_mb'] > 0 else ""
                print(f"{i+1}. Quality: {mp4['quality']}, Resolution: {mp4['resolution']}, FPS: {mp4['fps']}{size_info}")
            action = input("\nSelect action (1: Download, 2: Play in external player, 3: Copy URL): ")
            if action in ["1", "2", "3"]:
                format_idx = int(input(f"Select MP4 format (1-{len(mp4_urls)}): ")) - 1
                if 0 <= format_idx < len(mp4_urls):
                    selected_url = mp4_urls[format_idx]["url"]
                    if action == "1":
                        custom_filename = input("Enter filename (default: auto-generated): ").strip()
                        if not custom_filename:
                            title = video_info.get('title', 'video').replace('/', '_').replace('\\', '_')
                            custom_filename = f"{title}.mp4"
                        downloader.download_video(selected_url, custom_filename)
                    elif action == "2":
                        player_path = input("Enter player path (default: system default): ").strip() or None
                        downloader.play_in_external_player(selected_url, player_path)
                    elif action == "3":
                        try:
                            pyperclip.copy(selected_url)
                            print("URL copied to clipboard.")
                        except ImportError:
                            print("pyperclip not installed. Install with 'pip install pyperclip'.")
                        print(f"URL: {selected_url}")
                else:
                    print("Invalid format number.")
        else:
            print("\nNo playable MP4 URLs found.")

        save_option = input("\nSave video info to CSV? (y/n): ").lower()
        if save_option == 'y':
            downloader.save_to_csv(video_info)

    finally:
        downloader.close()

if __name__ == "__main__":
    main()