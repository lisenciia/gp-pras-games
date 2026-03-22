import logging
import time
logger = logging.getLogger('rawg_api')


def get_game_details(client, game_id):
    logger.debug(f"Request 4: fetching details for game id={game_id}")
    data = client._get(f'games/{game_id}')
    if data:
        logger.debug(
            f"Request 4 complete: got details for '{data.get('name')}'")
    else:
        logger.warning(
            f"Request 4: no data returned for game id={game_id}")
    return data