import logging
logger = logging.getLogger('rawg_api')


def get_developers(client, page=1):
    logger.info(f"Request 6: getting developers list, page {page}")
    data = client._get('developers', {'page': page, 'page_size': 40})
    if data:
        logger.info(
            f"Request 6 complete: {len(data.get('results', []))} developers finded")
    else:
        logger.warning("Request 6: no data returned")
    return data