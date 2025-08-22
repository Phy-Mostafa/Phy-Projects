import streamlit as st
import yt_dlp
import os

def download_facebook_video(url):
    # Options for yt_dlp
    ydl_opts = {
        'outtmpl': 'downloads/%(title)s.%(ext)s',
        'format': 'best',
        'quiet': True,
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        filename = ydl.prepare_filename(info)
    return filename, info.get('title', 'downloaded_video')

def main():
    st.title("📥 Facebook Video Downloader")

    url = st.text_input("Paste Facebook Video URL:")

    if st.button("Download"):
        if url:
            with st.spinner("Downloading video..."):
                try:
                    os.makedirs("downloads", exist_ok=True)
                    filepath, title = download_facebook_video(url)
                    with open(filepath, "rb") as f:
                        st.success(f"Downloaded: {title}")
                        st.download_button(label="Download Video",
                                           data=f,
                                           file_name=os.path.basename(filepath),
                                           mime="video/mp4")
                except Exception as e:
                    st.error(f"❌ Error: {str(e)}")
        else:
            st.warning("Please enter a valid Facebook video URL.")

if __name__ == "__main__":
    main()
