# ytdlqueue
ytdlqueue is a Python script to enqueue and download videos, using yt-dlp.

# Usage
Add video to .ytdlqueue and start downloading with 
`./ytdlqueue.py URL`

This creates a text file `.ytdlqueue` with urls to use in succession.

Call without URL to resume a stopped download session. `ytdlqueue` will ensure only one download session is running at a time.

# Caveats
`ytdlqueue` does not take any additional options. Set up the file in ~/.config/yt-dlp/config to pass options to yt-dlp.

____
