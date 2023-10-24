# IDS tutoring session 2: web scraping

This is the repository containing everything from the live demo.

The goal was to scrape 100 newest stories from [Hacker News](https://news.ycombinator.com/newest) using:
- the [API](https://github.com/HackerNews/API) - implemented in `api_scraper.py`
- Selenium to automate a web browser - implemented in `selenium_scraper.py`

Requirements:
- Get 100 newest stories.
- Not all stories are relevant, we want only those that lead to external sites (have outgoing links). Those that don't are usually discussions and we aren't interested in that.

This way we can showcase how much less work is using an API as opposed to doing browser automation, and why we should always look for any available APIs first.

Results of both methods are available in `hacker_news_api.csv` and `hacker_news_selenium.csv`. The results are not exactly the same between the API and Selenium method simply because new stories are published in the time the API scraper finishes and the Selenium scraper starts.