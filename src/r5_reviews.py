import logging
import time
logger = logging.getLogger('rawg_api')


def get_game_reviews(client, game_id, max_pages=1):
    logger.debug(f"Request 5: getting reviews for game id={game_id}")
    all_reviews = []
    page = 1
    while page <= max_pages:
        time.sleep(0.1)
        data = client._get(f'games/{game_id}/reviews', {'page': page})
        if not data or not data.get('results'):
            break
        for review in data['results']:
            text = review.get('text', '')
            if not text or len(text.strip()) < 10:
                continue
            all_reviews.append({
                'game_id': game_id,
                'review_id': review.get('id'),
                'text': text.strip(),
                'rating': review.get('rating'),
                'likes_count': review.get('likes_count', 0),
                'created': review.get('created'),
                'is_external': review.get('is_external', False)
            })
        if not data.get('next'):
            break
        page += 1
    logger.debug(f"Request 5 complete: {len(all_reviews)} reviews for game id={game_id}")
    aggregated = _aggregate_reviews(game_id, all_reviews)
    return all_reviews, aggregated


def _aggregate_reviews(game_id, reviews_list):
    if not reviews_list:
        return {
            'game_id': game_id,
            'reviews_count': 0,
            'reviews_avg_rating': None,
            'reviews_positive_pct': None
        }
    ratings = [r['rating'] for r in reviews_list if r['rating'] is not None]
    if not ratings:
        return {
            'game_id': game_id,
            'reviews_count': len(reviews_list),
            'reviews_avg_rating': None,
            'reviews_positive_pct': None
        }
    avg_rating = round(sum(ratings) / len(ratings), 2)
    positive = sum(1 for r in ratings if r >= 4)
    positive_pct = round(positive / len(ratings)*100, 1)
    return {
        'game_id': game_id,
        'reviews_count': len(reviews_list),
        'reviews_avg_rating': avg_rating,
        'reviews_positive_pct': positive_pct
    }