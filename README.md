UpdateWeeklyLinks
=================
Reddit - Update the two "weekly" links in /r/books header that point to the weekly "recommendation" and "what are you reading threads.

Requirements:

    PRAW library.
    Must be a moderator.
    

Usage:

    Edit USERNAME, PASSWORD and SUBREDDIT vars in UpdateWeeklyLinks.py.
    Run get-wiki-banned.py

This script is scheduled run shortly after AutoModerator posts a "weekly" post.  The script will run until it finds a "weekly" post, then it updates the /r/books header and exits.
