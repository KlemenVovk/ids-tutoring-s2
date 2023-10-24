# We will be scraping https://news.ycombinator.com/newest
# We want 100 newest stories
# Not all entries are stories, some are discussions (we want just those that lead to external sites)

import requests
import pandas as pd
from pprint import pprint

API_URL = "https://hacker-news.firebaseio.com/v0" # mention versioning
N_STORIES = 100 # You should start with a small number, because during debugging you're constantly re-running the script and that's not nice to the API.

# Get the newest story IDs
response = requests.get(API_URL + '/newstories.json')
story_ids = response.json()
print(story_ids)

# Since not every story will be saved (some are just discussions and we need to skip them), we'll use a while loop.
stories = []
i = 0
while i < N_STORIES:
    id = story_ids.pop(0)
    response = requests.get(API_URL + f'/item/{id}.json')
    story = response.json()
    if 'url' not in story: # skip stories without urls (these are discussions...)
        continue
    i += 1
    pprint(story) # NOTE: pprint
    stories.append(story)

# Get the title, time, by, score, and url.
df = pd.DataFrame(stories)
df = df[['title', 'time', 'by', 'score', 'url']]
df['time'] = pd.to_datetime(df['time'], unit='s') # parse time (API returns UNIX epoch time - seconds since 1.1.1970)
df.to_csv('hacker_news_api.csv', index=False) # NOTE: index=False