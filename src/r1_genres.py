import logging
logger = logging.getLogger('rawg_api')


def get_genres(client):
    logger.info("Request 1: fetching genres list")
    data = client._get('genres', {'page_size': 20})
    if data:
        genres = [{'id': g['id'],
                   'name': g['name'],
                   'slug': g['slug'],
                   'games_count': g['games_count']}
                  for g in data.get('results', [])]
        logger.info(f"Request 1 complete: {len(genres)} genres fetched")
        return genres
    logger.warning("Request 1: no data returned")
    return []