from datetime import datetime
import os
import tomllib
import subprocess

from git import Repo
import single

# Gets the current path
current_path = os.path.dirname(
    os.path.realpath(__file__)).parent()
public_path = os.path.join(current_path, "public")

# Creates the public folder if it doesn't exist
if not os.path.exists(public_path):
    os.makedirs(public_path)

# Creates the rss folder if it doesn't exist
rss_path = os.path.join(public_path, "rss")
if not os.path.exists(rss_path):
    os.makedirs(rss_path)

# Creates the path to the config file
config_path = os.path.join(current_path, "config.toml")

# Creates the path to the index.html file
homepage_path = os.path.join(public_path, "index.html")

# Creates an object that points to the GIT Repository
repo = Repo(current_path)
repo_origin = repo.remotes.origin
repo_origin.pull()

# Loads the config file with the feed list
with open(config_path, "rb") as f:
    config = tomllib.load(f)
feeds = []
for feed in config["feed"]:
    feeds.append(feed)

# Parse each feed
for feed in feeds:
    parser = single.RaiParser(feed["url"], rss_path)
    parser.process(skip_programmi=False, skip_film=True, date_ok=False)
    rss_file = feed["url"].split("/")[-1]
    rss_file_path = os.path.join(rss_path, rss_file + ".xml")
    repo.index.add(rss_file_path)
    #breakpoint()

# Write a simple HTML page
with open(homepage_path, "w", encoding="utf8") as f:
    f.write(
        """<!DOCTYPE html>
        <html lang="en">
        <head>
        <title>Feeds</title>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">        
        <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/@picocss/pico@2/css/pico.min.css"/>
        </head>
        <body>
        <div class="container">
        <h1>Feed List</h1>
        <ul>
        """)
    for feed in feeds:
        rss_file = feed["url"].split("/")[-1]
        title = feed.get("title", rss_file)        
        f.write(f'<li><a href="rss/{rss_file}.xml">{title}</a></li>')
    f.write(
        """
        </ul>
        </div>
        </body>
        </html>
        """)
repo.index.add(homepage_path)

# Create a git commit message
today = datetime.now().strftime("%d-%m-%Y %H:%M")
repo.index.commit(today)
repo_origin.push(refspec='main')
#subprocess.run(["git", "add", "public/*"], cwd=current_path)
#subprocess.run(["git", "commit", "-m", today], cwd=current_path)
#subprocess.run(["git", "push", "origin", "main"], cwd=current_path)
