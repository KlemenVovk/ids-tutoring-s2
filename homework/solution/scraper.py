from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
import time
from pprint import pprint
import pandas as pd
import json

# TESTED WORKING AS OF 2023-10-31

URL = "https://www.imdb.com/"

service = Service()
options = webdriver.ChromeOptions()
driver = webdriver.Chrome(service=service, options=options)
# fix the window size so that the website doesn't change layout depending on the window size
driver.set_window_size(1200, 1000)

# Navigate to the IMDB homepage
driver.get(URL)

# scroll down to the bottom of the page (our element only appears when we scroll down)
driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
# give the page time to load
time.sleep(3)

# Find the div that has the top-box-office class (the section of the page we want)
top_box_office = driver.find_element(By.CLASS_NAME, "top-box-office")
# NOTE: notice how we took the top_box_office element as the root to search for the link.
# This narrows down the search space (there is hopefully only one title inside the top box office section) and is therefore less error prone.
link = top_box_office.find_element(By.CLASS_NAME, "ipc-title-link-wrapper")

# get the link url and navigate to it
# NOTE: we could also just click the link with link.click() BUT this means that the link has to be in the viewport (visible on the screen) else you will get an element is not clickable error.
link_url = link.get_attribute("href")
print(f"Top box office chart Link: {link_url}")
driver.get(link_url)

# get all links with class ipc-title-link-wrapper
links_elements = driver.find_elements(By.CLASS_NAME, "ipc-title-link-wrapper")
# NOTE: this selects also some links that are not titles. We know that each movie leads to a https://www.imdb.com/title/... url so we can filter out the links that don't start like that.
links = [link.get_attribute("href") for link in links_elements if link.get_attribute("href").startswith("https://www.imdb.com/title/")]
assert len(links) == 10 # we are looking for exactly 10 movies, so this needs to hold. assert statements are a good way to continuously check that your code is working as expected.

# Now we have the links to the 10 movies we want to scrape. We can now loop over them and scrape the data we want.
movies = []
for link in links:
    print(f"Scraping movie: {link}")

    driver.get(link)
    time.sleep(3)
    movie = {}
    # TITLE
    # get the title (has an attribute data-testid="hero__pageTitle")
    title_h1 = driver.find_element(By.CSS_SELECTOR, "[data-testid='hero__pageTitle']")    
    movie["title"] = title_h1.text
    print(f"Title: {movie['title']}")

    # YEAR AND DURATION
    # title, year and duration are all in 1 div. Title is in h1, year and duration are in ul
    # the idea is to get the parent of the title element (so that div is the parent of h1 and ul) and then get the ul element from there
    title_parent = title_h1.find_element(By.XPATH, "..") # two dots just mean to go up one level in the html tree (so the parent, you could do ../../.. to go up 3 levels)
    year_pg_duration_list = title_parent.find_element(By.TAG_NAME, "ul") # could also use: title_h1.find_element(By.XPATH, "./following-sibling::ul"), but I tried to use as little XPath as possible as you weren't really introduced to it...
    movie["year"] = year_pg_duration_list.find_elements(By.TAG_NAME, "li")[0].text # NOTE: we could also use find_element here as by default it finds the FIRST element that matches the selector
    duration = year_pg_duration_list.find_elements(By.TAG_NAME, "li")[-1].text
    # the duration is of form "1h 59m" so we need to convert it to minutes
    hours, minutes = duration.split("h")
    movie["duration"] = int(hours) * 60 + int(minutes[:-1]) # we need to remove the "m" at the end of minutes

    # RATING
    # get rating - the div has property data-testid="hero-rating-bar__aggregate-rating__score"
    rating = driver.find_element(By.CSS_SELECTOR, "[data-testid='hero-rating-bar__aggregate-rating__score']").text
    # the rating is of form "5.6\n/10" so we need to split it and take the first part
    movie["rating"] = float(rating.split("\n")[0])

    # TAGS
    # get tags class ipc-chip__text
    tags = driver.find_elements(By.CLASS_NAME, "ipc-chip__text")
    movie["tags"] = [tag.text for tag in tags if len(tag.text) > 0]

    # PLOT
    # get plot - property data-testid="plot-xl"
    # NOTE: this is a nice example of responsive website design (appears differently on mobile and on web)
    # There are 3 elements containing the plot, and the correct one is displayed depending on the screen size.
    # So on mobile the one with plot-xs_to_m is displayed, and on larger screens the one with plot-l or plot-xl is displayed.
    # Selenium can copy text directly only from the one that is displayed!
    movie["plot"] = driver.find_element(By.CSS_SELECTOR, "[data-testid='plot-l']").text
    print("Result:")
    pprint(movie)
    movies.append(movie)

# Save as json
with open("movies.json", "w") as f:
    json.dump(movies, f)

# Save as csv
df = pd.DataFrame(movies)
# If you save directly to csv then the tags will get saved as "['tag1', 'tag2', ...]" which is clunky to work with for whoever uses the csv.
# Let's convert the tags to a simple | separated string and save that instead.
df["tags"] = df["tags"].apply(lambda tags: "|".join(tags))
df.to_csv("movies.csv", index=False)


# Close the webdriver
driver.quit()