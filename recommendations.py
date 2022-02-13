# -*- coding: utf-8 -*-
'''
Functions for computing similarity and making final recommendations

'''

import copy

from scipy import stats

from profile_tools import prepare_apis, create_profile, create_profiles


# METRICS

# STRING LIST  X STRING LIST
# gives full score for intersection
# gives half score for the intersection of nested parts


def partial_overlap(a, b):
    size_a = len(a)
    size_b = len(b)
    if size_a > size_b:
        a, b = b, a
    if size_a == 0:
        return 0
    score = 0
    for part in a:
        if part in b:
            score += 1
            continue
        part_set = set(part.split())
        for part2 in b:
            part2_set = set(part2.split())
            if len(part_set.intersection(part2_set)) >= 1:
                score += 0.5
                break
    score = score / size_a
    return score if score <= 1 else 1


# FLOAT LIST X FLOAT LIST (normalized)
# harmonic mean of distances


def harmonic_mean_distances(values_a, values_b):
    return stats.hmean([1 - abs(values_a[i] - values_b[i]) for i in range(len(values_a))])


# SIMILARITY FUNCTION


def compute_similarity(profile, profile_list):
    profile_list = copy.deepcopy(profile_list)
    for song_profile in profile_list:
        max_score = 0
        score = 0
        if profile['features']:
            '''
            0 key
            1 tempo
            2 acousticness
            3 instrumentalness
            4 speechiness
            5 valence
            6 danceability
            7 energy
            8 loudness
            '''
            weight = 4
            if song_profile['features']:
                pos_list = [1, 2, 3, 4, 5, 6, 7, 8]  # [3, 6, 7, 8]  # [1,3,4,6,7,8]   #[0,2,3,6,7,8]
                features1 = [profile['features'][i] for i in pos_list]
                features2 = [song_profile['features'][i] for i in pos_list]
                score += harmonic_mean_distances(features1, features2) * weight
            max_score += weight
        if profile['era']:
            weight = 2
            if profile['era'] == song_profile['era']:
                score += weight
            max_score += weight
        if profile['genres']:
            weight = 3
            genre_score = partial_overlap(
                profile['genres'], song_profile['genres'])
            score += genre_score * weight
            max_score += weight
        extras1 = []
        extras2 = []
        for key in ['moods', 'vocal', 'ensemble']:
            extras1 = extras1 + profile[key]
            extras2 = extras2 + song_profile[key]
        if extras1:
            weight = 1
            score += partial_overlap(extras1, extras2) * weight
            max_score += weight
        song_profile['similarity'] = score / max_score
    return profile_list


# RECOMMENDATIONS


def get_recommendations(title, artist, limit):
    prepared = prepare_apis()
    result = []
    status = {'error': "Failed to prepare API's"}
    profile = []
    if prepared:
        status = {'error': ''}
        try:
            profile = create_profile(title, artist)
            if profile:
                profile_list = create_profiles(profile)
                if profile_list:
                    recommendations = compute_similarity(profile, profile_list)
                    recommendations = sorted(
                        recommendations, reverse=True, key=lambda x: (x['similarity'], x['popularity']))
                    recommendations = [
                        recommendation for recommendation in recommendations if recommendation['similarity'] >= 0.4]
                    result = recommendations[:limit]
                else:
                    status = {'error': 'Recommendations not found'}
            else:
                status = {'error': 'Track not found'}
        except Exception as e:
            status = {'error': e}
    return profile, result, status


def print_recommendations(profile, recommendations):
    print('\nRecommendations for "{}" by "{}", \n lastfm: {} \n spotify: {} \n'.format(
        profile['title'], profile['artist'], profile['lastfm_url'], profile['spotify_url']))
    returnJson = {}
    for i, rec in enumerate(recommendations):
        returnJson[i] = ({'artist': rec['artist'], 'title': rec['title'], 'similarity': "{0:.0f}%".format(rec['similarity']*100),
                          'popularity': rec['popularity'], 'lastfm_url': rec['lastfm_url'],
                          'spotify_url': rec['spotify_url']})
        # print('{}: "{}" by "{}", similarity:{:.2f} popularity:{:.2f} \n lastfm: {} \n spotify: {} \n'.format(
        #     i + 1, rec['title'], rec['artist'], rec['similarity'], rec['popularity'], rec['lastfm_url'],
        #     rec['spotify_url']))
    return returnJson
