from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
import pandas as pd
from pprint import pprint

URL = "https://news.ycombinator.com/newest"
N_STORIES = 100

service = Service()
options = webdriver.ChromeOptions()
# options.add_argument("--headless=new")
driver = webdriver.Chrome(service=service, options=options)

# Navigate to the webpage you want to scrape
driver.get(URL)

stories = []
story = {}
skip = False # flag to skip the rows if a story is a discussion (doesn't lead to an external URL).
while len(stories) < N_STORIES:
    # Get the table with story rows
    # NOTE: we have to get this table again every time we press More (go to the next page), since the reference to the table on the previous page is no longer valid.
    table = driver.find_element(By.CSS_SELECTOR, "#hnmain > tbody > tr:nth-child(3) > td > table > tbody") # show how to get selectors from Chrome devtools
    
    # Iterate over the rows in the table and act based on the class name of the row
    for row in table.find_elements(By.TAG_NAME, "tr"): # notice how I used table as the root element for the search and not `driver.find_element`
        class_name = row.get_attribute("class")
        match class_name:
            case "athing": # get the title and url
                story["title"] = row.find_element(By.CLASS_NAME, "titleline").find_element(By.TAG_NAME, "a").text
                story["url"] = row.find_element(By.CLASS_NAME, "titleline").find_element(By.TAG_NAME, "a").get_attribute("href")
                # Check if an element inside title has the class 'sitebit` - if it doesn't, it's a discussion and we want to skip it.
                if len(row.find_elements(By.CLASS_NAME, "sitebit")) == 0:
                    skip = True
            case "": # get the time, score, and by
                story["time"] = row.find_element(By.CLASS_NAME, "age").get_attribute("title")
                story["score"] = int(row.find_element(By.CLASS_NAME, "score").text.split(" ")[0])
                story["by"] = row.find_element(By.CLASS_NAME, "hnuser").text
            case "spacer": # this is the spacer between stories, save the current story and reset the story dictionary for the next story
                # If the story isn't skipped, we can add it to the list of stories.
                if not skip:
                    stories.append(story)
                    pprint(story)
                # Reset the story dictionary and skip flag
                story = {}
                skip = False            
            case "morespace": # the space between the stories and the More button, when this is reached, we are done with this page and need to click the More button
                break
    
    # Click the More button to load the next page
    # NOTE: after testing, this works even without scrolling to the button first. I'm not exactly sure why (probably because it's a link and we can just go to that link instead of it being a button).
    # NOTE: At any time if you get "Element not interactable" error, try scrolling to the element first.
    more_button = driver.find_element(By.LINK_TEXT, 'More')
    more_button.click()

# Save to csv
df = pd.DataFrame(stories[:N_STORIES])
df = df[['title', 'time', 'by', 'score', 'url']]
df.to_csv('hacker_news_selenium.csv', index=False)


# Close the webdriver
driver.quit()
