import logging
logger = logging.getLogger('rawg_api')


def get_games_page(client, page=1, page_size=50, genre_slug=None, ordering='-rating'):
    params = {
        'page': page,
        'page_size': page_size,
        'ordering': ordering
    }
    if genre_slug:
        params['genres'] = genre_slug
    logger.debug(
        f"Request 3: fetching games — page {page}, genre={genre_slug}")
    data = client._get('games', params)
    if data:
        logger.debug(
            f"Request 3 complete: {len(data.get('results', []))} games on page {page}")
    else:
        logger.warning(
            f"Request 3: no data for genre={genre_slug}, page={page}")
    return data