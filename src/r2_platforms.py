import logging
logger = logging.getLogger('rawg_api')


def get_platforms(client):
    logger.info("Request 2: fetching platforms list")
    data = client._get('platforms', {'page_size': 51})
    if data:
        platforms = [{'id': p['id'],
                      'name': p['name'],
                      'slug': p['slug']}
                     for p in data.get('results', [])]
        logger.info(f"Request 2 complete: {len(platforms)} platforms fetched")
        return platforms
    logger.warning("Request 2: no data returned")
    return []