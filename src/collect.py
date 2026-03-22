import pandas as pd
import logging
import logging.config

logging.config.fileConfig('config/logging.cfg')
logger = logging.getLogger('rawg_api')

from rawg_client import RAWGClient
from r1_genres import get_genres
from r2_platforms import get_platforms
from r3_games import get_games_page
from r4_info import get_game_details
from r5_reviews import get_game_reviews
from r6_developers import get_developers


def collect_all_games(client, target=3000):
    all_games = []
    all_reviews = []
    seen_ids = set()
    page = 1
    while len(all_games) < target:
        data = get_games_page(client, page=page)
        if not data or not data.get('results'):
            break
        for game in data['results']:
            if len(all_games) >= target:
                break
            game_id = game['id']
            if game_id in seen_ids:
                continue
            seen_ids.add(game_id)
            details = get_game_details(client, game_id)
            reviews_list, aggregated = get_game_reviews(client, game_id)
            all_reviews.extend(reviews_list)
            all_games.append({
                'rawg_id': game_id,
                'name': game.get('name'),
                'released': game.get('released'),
                'rawg_rating': game.get('rating'),
                'ratings_count': game.get('ratings_count'),
                'metacritic': game.get('metacritic'),
                'playtime': game.get('playtime'),
                'genres': '/'.join([g['name'] for g in game.get('genres', [])]),
                'platforms_count': len(game.get('platforms', [])),
                'description': details.get('description_raw', '') if details else '',
                'achievements_count': details.get('achievements_count', 0) if details else 0,
                'esrb_rating': (details.get('esrb_rating') or {}).get('name') if details else None,
                'website': details.get('website', '') if details else '',
                'reviews_count': aggregated['reviews_count'],
                'reviews_avg_rating': aggregated['reviews_avg_rating'],
                'reviews_positive_pct': aggregated['reviews_positive_pct']
            })
            if len(all_games) > 0 and len(all_games) % 500 == 0:
                pd.DataFrame(all_games).to_csv(
                    'data/raw/rawg_games_temp.csv', index=False)
                pd.DataFrame(all_reviews).to_csv(
                    'data/raw/rawg_reviews_temp.csv', index=False)
                logger.info(f"Intermediate save: {len(all_games)} games, "f"{len(all_reviews)} reviews")
        if not data.get('next'):
            logger.info(f"No more pages at page {page}")
            break
        page += 1
    df_games = pd.DataFrame(all_games).drop_duplicates('rawg_id')
    df_games.to_csv('data/raw/rawg_games.csv', index=False)
    logger.info(f"Collection complete. Total games: {len(df_games)}")
    df_reviews = pd.DataFrame(all_reviews).drop_duplicates('review_id')
    df_reviews.to_csv('data/raw/rawg_reviews.csv', index=False)
    logger.info(f"Total reviews saved: {len(df_reviews)}")
    return df_games, df_reviews


client = RAWGClient()
genres = get_genres(client)
pd.DataFrame(genres).to_csv('data/raw/rawg_genres.csv', index=False)
logger.info(f"Genres saved: {len(genres)}")
platforms = get_platforms(client)
pd.DataFrame(platforms).to_csv('data/raw/rawg_platforms.csv', index=False)
logger.info(f"Platforms saved: {len(platforms)}")
devs = get_developers(client)
if devs:
    pd.DataFrame(devs['results']).to_csv(
        'data/raw/rawg_developers.csv', index=False)
    logger.info("Developers saved")
df_games, df_reviews = collect_all_games(client, target=3000)
logger.info(f"Done! Games: {len(df_games)}, Reviews: {len(df_reviews)}")
logger.info(f"Games dataset preview:\n{df_games.head().to_string()}")