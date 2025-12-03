import re

def extract_features(url):
    features = {}
    features['has_ip'] = 1 if re.match(r'\d+\.\d+\.\d+\.\d+', url) else 0
    features['length'] = len(url)
    features['has_https'] = 1 if url.startswith("https") else 0
    features['count_dots'] = url.count('.')
    features['count_at'] = url.count('@')
    features['count_dash'] = url.count('-')
    features['count_slash'] = url.count('/')
    features['count_percent'] = url.count('%')
    features['count_question'] = url.count('?')
    return list(features.values())
