import streamlit as st
import yt_dlp
import os

def get_video_info(url):
    # Options for yt_dlp to extract info without downloading
    ydl_opts = {
        'quiet': True,
        'no_download': True,
    }
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            return {
                'title': info.get('title', 'Untitled Video'),
                'thumbnail': info.get('thumbnail', None),
                'duration': info.get('duration', None),
                'url': url
            }
    except Exception as e:
        st.error(f"❌ Error fetching video info: {str(e)}")
        return None

def download_facebook_video(url):
    # Options for yt_dlp to download the video
    ydl_opts = {
        'outtmpl': 'downloads/%(title)s.%(ext)s',
        'format': 'best',
        'quiet': True,
    }
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info)
        return filename, info.get('title', 'downloaded_video')
    except Exception as e:
        st.error(f"❌ Error downloading video: {str(e)}")
        return None, None

def main():
    st.title("📥 Facebook Video Downloader")

    url = st.text_input("Paste Facebook Video URL:")

    if url:
        with st.spinner("Fetching video information..."):
            video_info = get_video_info(url)
        
        if video_info:
            # Display video preview
            st.subheader("Video Preview")
            if video_info['thumbnail']:
                st.image(video_info['thumbnail'], use_column_width=True)
            st.write(f"**Title**: {video_info['title']}")
            if video_info['duration'] is not None:
                duration = int(video_info['duration'])  # Convert to integer
                st.write(f"**Duration**: {duration // 60}:{duration % 60:02d} minutes")
            else:
                st.write("**Duration**: Not available")
            
            # Ask user if they want to download
            if st.button("Download Video"):
                with st.spinner("Downloading video..."):
                    os.makedirs("downloads", exist_ok=True)
                    filepath, title = download_facebook_video(url)
                    if filepath:
                        with open(filepath, "rb") as f:
                            st.success(f"Downloaded: {title}")
                            st.video(filepath)
                            st.download_button(
                                label="Save Video",
                                data=f,
                                file_name=os.path.basename(filepath),
                                mime="video/mp4"
                            )
            else:
                st.info("Click 'Download Video' to proceed with downloading.")
    else:
        st.warning("Please enter a valid Facebook video URL.")

if __name__ == "__main__":
    main()
