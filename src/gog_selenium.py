from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import csv
import time
import random
import re
import logging
import logging.config
import os
from concurrent.futures import ThreadPoolExecutor, as_completed
from tenacity import retry, stop_after_attempt, wait_fixed
from tqdm import tqdm

logging.config.fileConfig("config/logging_config.ini")
logger=logging.getLogger(__name__)

options=webdriver.ChromeOptions()
options.add_argument("--headless")
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")

path=ChromeDriverManager().install()
def create_browser():
    return webdriver.Chrome(service=Service(path),options=options)
browser=create_browser()

def get_game_urls():
    urls=[]
    seen_urls=set()
    page=1
    while page<= 300:
        url=f"https://www.gog.com/en/games?page={page}&sort=rating&order=desc"
        logger.info(f"Collect page {page}")

        try:
            browser.get(url)
            time.sleep(3)
            soup=BeautifulSoup(browser.page_source, "html.parser")
            games=soup.find_all("a", href=re.compile(r"/en/game/"))
            if not games:
                logger.warning(f"Page {page} is empty, stop")
                break
            for game in games:
                href=game.get("href", "")
                if href and "/en/game/" in href:
                    full_url=f"https://www.gog.com{href}" if not href.startswith("http") else href
                    if full_url not in seen_urls:
                        seen_urls.add(full_url)
                        urls.append(full_url)
            logger.info(f"Page {page}, total urls: {len(urls)}")
            page+=1
            time.sleep(random.uniform(2, 3))

        except Exception as e:
            logger.error("Error on catalog page %s, restart browser", page, exc_info=True)
            try:
                browser.quit()
            except:
                pass
            globals()["browser"]=webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)                                     
            time.sleep(5)
    return urls

def restart_browser():
    global browser
    try:
        browser.quit()
    except:
        pass
    options=webdriver.ChromeOptions()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    browser = webdriver.Chrome(service=Service(ChromeDriverManager().install()),options=options)
    logger.info("browser restarted successfully")

@retry(stop=stop_after_attempt(3), wait=wait_fixed(5), reraise=True) 

def scrape_game(url):
    local_browser=create_browser()
    try:
        local_browser.get(url)
        time.sleep(3)
        try:
            age_button=local_browser.find_element(By.XPATH,"//button[contains(text(),'Continue')]")
            age_button.click()
            logger.info(f"Age confirmation: {url}")
            time.sleep(2)
        except:
            pass 
        soup=BeautifulSoup(local_browser.page_source, "html.parser")
        title_tag=soup.find(class_="productcard-basics__title")
        title=title_tag.text.strip() if title_tag else ""
        if not title:
            logger.warning(f"Empty page")
            return None
        price="0"
        rating = ""
        reviews_count = "0"
        year=""
        developer=""
        script_tag= soup.find("script", type="application/ld+json")
        if script_tag:
            import json
            try:
                data= json.loads(script_tag.string)
                offers= data.get("offers", [])
                if isinstance(offers, dict):
                    offers= [offers]
                for offer in offers:
                    if isinstance(offer, dict) and offer.get("priceCurrency") == "USD":
                        price= str(offer.get("price", "0"))
                        break
                if price== "0" and offers:
                    price= str(offers[0].get("price", "0"))

                if "aggregateRating" in data:
                    rating= str(data["aggregateRating"].get("ratingValue", ""))
                    reviews_count= str(data["aggregateRating"].get("ratingCount", "0"))
                release= data.get("releaseDate", "")
                if release:
                    match= re.search(r"\d{4}", release)
                    if match:
                        year= match.group()

                dev_tag=soup.find("a", href=re.compile(r"developers="))
                developer=dev_tag.text.strip() if dev_tag else ""
            except:
                pass
        genre_tags=soup.find_all("a", href=re.compile(r"/games\?genres="))
        genre=", ".join([g.text.strip() for g in genre_tags[:3]])
        
        tag_elements=soup.find_all("a", href=re.compile(r"/games/tags/"))
        tags=", ".join([t.text.strip() for t in tag_elements[:7]])
        desc_tag=soup.find(class_="description")
        description=re.sub(r"\s+", " ", desc_tag.get_text(separator=" ").strip()[:500]) if desc_tag else ""
        logger.info(f"Collect: %s | rate: %s | reviews: %s", title, rating, reviews_count)
        
        return {"title": title,
            "price": price,
            "rating": rating,
            "reviews_count": reviews_count,
            "genre": genre,
            "tags": tags,
            "developer": developer,
            "year": year,
            "description": description,
            "url": url}

    except Exception as e:
        logger.error(f"collection error{url}-restart browser", exc_info=True)
        return None
    finally:
        try:
            local_browser.quit()
        except Exception:
            pass

os.makedirs("data/raw", exist_ok=True)
logger.info("start GOG Selenium scrap")

logger.info("1:collecting urls of games")
urls=get_game_urls()
logger.info(f"Urls found: {len(urls)}")

logger.info("2:collecting data of games")
ordered_results=[None]*len(urls)
completed=0
success=0
failed=0
start_time=time.time()
with ThreadPoolExecutor(max_workers=6) as executor:
    future_to_index= {}
    for i, url in enumerate(urls):
        future_to_index[executor.submit(scrape_game, url)] = i
    for future in tqdm(as_completed(future_to_index), total=len(future_to_index)):
        index = future_to_index[future]
        try:
            data = future.result()
        except Exception:
            logger.error(f"worker error on {urls[index]}", exc_info=True)
            data = None
        if data:
            ordered_results[index]=data

results=sorted([result for result in ordered_results if result], key=lambda x: x["title"])
browser.quit()
logger.info(f"3:save {len(results)} games")
with open("data/raw/gog_data.csv", "w", newline="", encoding="utf-8") as f:
    if results:
        writer=csv.DictWriter(f, fieldnames=results[0].keys())
        writer.writeheader()
        writer.writerows(results)
logger.info("done; data in data/raw/gog_data.csv")