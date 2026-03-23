## Project Overview
This project analyzes the video game market using data collected from multiple sources, our main goal is to find out which game characteristics are connected to popularity and market performance.

Our project combines:
- scraping from gaming stores
- API-based data collection
- data cleaning and integration
- exploratory data analysis (EDA)

## Business Problem
For indie developers, publishers and investors it is important to understand which features of a game are linked to stronger audience response.

Our key research question is:
*Which game characteristics are most strongly associated with popularity?*

The project is aimed at turning raw platform data into something more useful for business decisions:
- how to position a game
- which features may attract more player attention
- what patterns can be seen in successful or visible titles

## Data Sources
We used multiple data sources:
### 1. Steam
*Role in the project:* main source for large-scale game data collection through scraping
Collected fields in the Steam part of the project:
- title
- price
- tags
- description
- number of reviews
- release date
- developer
- platform-related fields
- review labels/review summaries

### 2. RAWG API
*Role in the project:* additional source collected through API requests with an API key
Fields collected from RAWG:
- RAWG id
- game name
- release date
- rating
- ratings count
- Metacritic score
- playtime
- genres
- platforms count
- achievements count
- ESRB rating
- website
- review-related information
- developers
- reference tables for genres and platforms

### 3. GOG
*Role in the project:* additional scraping source using Selenium
Fields collected from GOG:
- title
- price
- rating
- reviews count
- genre
- tags
- developer
- year
- description
- URL

The main idea of the merge is:
- collect game data from stores/platforms
- normalize game names and other fields
- enrich the base table with metadata from API and supplementary sources
- prepare one final dataset for EDA

## Project Workflow
In our case, the workflow is:
1. Collect store-level data for games
2. Collect structured metadata from RAWG API
3. Use Selenium where interaction/dynamic content is needed
4. Clean dates, prices, text fields, and game names
5. Prepare a merged analytical dataset
6. Study popularity-related patterns through EDA

## Repository Structure
The current repository contains the following main parts:
- src/collect.py — runs the RAWG API collection pipeline
- src/rawg_client.py — handles API requests and authentication
- src/r1_genres.py to src/r6_developers.py — separate RAWG request modules
- src/gog_selenium.py — Selenium-based GOG scraping pipeline
- src/steam_scraping.ipynb — Steam scraping notebook
- src/Data-engeneering.ipynb — data cleaning, merging, and feature engineering notebook
- src/EDA.ipynb — exploratory data analysis notebook
- data/raw/gog_data.csv — raw GOG scraping result
- data/raw/steam_games_dataset.csv — raw Steam scraping result
- data/Processed/FULL_dataset_full.csv — full merged dataset
- data/Processed/EDA_dataset.csv — final analytical dataset used in EDA
- config/logging.cfg and config/logging_config.ini — logging configuration files

## Tools and Libraries
We used the following tools in the project:
- requests
- BeautifulSoup
- Selenium
- pandas
- dotenv
- logging
- tenacity
- tqdm
- webdriver-manager

Why these tools were used:
- requests and BeautifulSoup are the main scraping/parsing tools required by the assignment
- Selenium was added to manage dynamic platform interaction
- dotenv keeps the API key out of the public code
- logging was added for better monitoring and reproducibility
- tenacity helps with retry logic
- pandas is used to clean and save datasets

## API Collection
The API part is based on RAWG API, this part of the project satisfies the requirement of using:
- a separate portal for API collection
- an API key
- multiple different API requests

The API pipeline includes at least the following request groups:
- genres
- platforms
- game list pages
- game details
- game reviews
- developers

Output files created by the RAWG pipeline include:
- rawg_games.csv
- rawg_reviews.csv
- rawg_genres.csv
- rawg_platforms.csv
- rawg_developers.csv

## Scraping Collection
The scraping side of the project is based on store/platform data

### Steam
Steam is the main scraping source in the overall project idea and was used during the working stage of the project to collect large-scale game data with text fields and review-based information.

The Steam scraping notebook is stored in:
- src/steam_scraping.ipynb
The raw Steam dataset is stored in:
- data/raw/steam_games_dataset.csv

The Steam scraping dataset contains 11250 rows and includes fields such as:
- app id
- name
- release date/year
- price
- positive review percentage
- total reviews
- review label
- short description
- tags
- genres
- developer

### GOG
The current integrated repository contains a Selenium-based GOG scraper
What it does:
- opens GOG catalogue pages
- collects game URLs
- visits individual game pages
- extracts structured information from product pages
- saves results to data/raw/gog_data.csv
This file contains store-level game information collected through Selenium pipeline.

## Dataset Logic
The final analytical idea of the dataset is:
*one row = one game*

The final analytical dataset combines:
- store-level data
- API enrichment data
- textual fields
- review/rating information
- engineered variables for analysis

The project includes at least one textual feature, which is a mandatory requirement of the assignment:
- description
- and also tags

## Final Datasets
The project currently contains two processed datasets:
### 1. data/Processed/EDA_dataset.csv
This is the *final analytical dataset* used in the project
Current shape:
- **11196 rows**
- **28 columns**

It contains the main variables selected for exploratory data analysis and interpretation
### 2. data/Processed/FULL_dataset_full.csv
This is the full merged version of the dataset.
Current shape:
- **11196 rows**
- **46 columns**
It contains a wider set of merged and engineered features from all available sources

## Main Feature Groups
The project works with several groups of features:
### Store-level features
- title/name
- price
- release date/year
- developer
- genre
- tags
- URL

### Review and popularity-related features
- number of reviews
- positive review share
- review labels/summaries
- platform rating
- ratings count

### API enrichment features
- Metacritic
- playtime
- achievements count
- ESRB rating
- platforms count
- website
- RAWG metadata tables

### Textual features
- description
- tags

These features were chosen because they are directly connected to the business question and can potentially explain differences in visibility or popularity

## Target Variable
The project focuses on *game popularity*.
At the working stage, we considered popularity through:
- number of reviews
- rating-based indicators
- merged popularity-related metrics

In the final EDA notebook, the main analytical target is:
- popularity_score_v2

This variable is based on:
- Steam review volume
- Steam positive review percentage
- normalized price information

In the data engineering notebook popularity_score_v2 is built as a popularity proxy using review count, review quality, and price, and then converted into a percentile-based score.
This follows directly from the project idea discussed by the team:
the target variable should represent some kind of game response or visibility in the market.

## Data Cleaning
Data cleaning is an important part of the project, we use cleaning steps such as:
- date normalization
- price normalization
- text cleanup
- duplicate handling
- title normalization for merging
- regex-based cleaning where needed

This is important because data from different platforms is not fully consistent:
- names may differ
- editions/DLCs may create matching problems
- review formats vary
- price formats differ across sources

## Missing Values
Missing values are expected in this project, especially after merging multiple sources, the main reasons are:
1. Not every game is available or matched across all platforms
2. Different sources expose different metadata
3. Some enrichment fields exist only in RAWG or only in store pages
4. Store/platform naming differences make exact matching harder

So in the merged version of the dataset missing values are especially likely in:
- API-only enrichment columns
- cross-platform rating fields
- metadata that is source-specific
- fields unavailable for some games or platforms

## EDA
EDA is documented in:
- src/EDA.ipynb
The final EDA notebook uses:
- data/Processed/EDA_dataset.csv

The notebook includes:
- general overview of the dataset
- missing values check
- target distribution
- outlier check
- genre analysis
- price analysis
- correlation matrix
- text analysis of descriptions
- year-based analysis
- hypotheses and conclusions

## EDA Summary
Based on the current EDA notebook, the main observations are:
- lower-priced games tend to be more associated with higher popularity
- higher steam_positive_pct is positively related to popularity
- free games show a higher median popularity than paid games, but their outcomes are less stable
- some less saturated genres have higher average popularity than the most common genres
- description length has only a weak relationship with popularity

## Limitations
The project has several natural limitations, which are important when interpreting the final results:
- game names are not always identical across platforms
- cross-platform matching is not perfect
- platform metrics are proxies, not full business performance measures
- different platforms provide different levels of detail
