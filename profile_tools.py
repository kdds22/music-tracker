# -*- coding: utf-8 -*-
'''
Functions for creating profiles and accessing apis

'''

import re
from threading import Thread
from urllib.parse import quote as quote_plus

import requests
from dateutil import parser as dparser
from numpy import NaN

import api_keys as keys
from musical_metadata import load_data

# API KEYS AND TOKENS

last_fm_api_key = keys.lastFmApiKey
spotify_api_code = 'AQA0FBjbux8xQk_SH5fcM2JrwArP-dhrhXeIWeH8g36_zLre5slkHdZO-oS_oYVqmVHI7qLc3Da-PDr_SAfhUcgXRsBwgXN_qcPUJYq3WxAcUJPX8paqYygGXxowbPVZl2CWTBeQdlcJw-6XWJEN37hKqsvZy6OgnBw-zOwjJU3-1EykU4rg3Z52U7wnmXbdiUmdIhOmlDH2f224K03IF0GRjusgLQ'
spotify_api_token = 'BQC820Xb8MQBcj0i3yvGeSb1t1KbYhRfxRrg-0gj9X5Bx2ri9a5dOaymnf3AetS9IISghDSKmxHuZUPpgIyctuOdbNDWD7p4VutJPvOrO1t9HCdNpNFQ_3mNNs2aC26xQyiqFguy0hE0oxpRehRVM2-IOqL0WZsp'


# spotify_api_token = 'AQDKLwAHx1ADyLMI3PJUzVhpXhW-Vn90b4iAxUeIok0eRbXloZOasDdpGR78rz7klbowJAEFEArhYYQdJrD6MzWnr5ZJbt_DCgfGJ94sacGE8BYd7Mk-CDzwVGWWuZXJyqE'


# 'redirect_uri': 'klaus-music-tracker://callback',
# accessToken = "BQAI3rRcZ3z-FWo4YHm6NMX7KMrK26dWuSoIw1Oxs24qnVItQ6mZEg-ZZQsV9eEWE4SvQ37g4JzQtYm_cVjzOaikOAJMMgiA7QPMFGRezQM8Ksel6AQVj0iiBBxV15ENgT_lH2zzFlRKnfkr96yuznJkURen02qM"
# refreshToken = AQAc61QdDkPobIc5DWJE5rA6XNq5AhWOQbSFi97b27wqje43p2LYMUiIEn78KMVogoX8EYjRfvGVTAYvek-M42L91mSuCkXaiGNgIBrx9zMk6LMo-DuEVDTWlSeR3H60feA"
# 'redirect_uri': 'http://localhost:8888/callback',

def refresh_spotify_token():
    global spotify_api_token
    global spotify_api_code

    params = {
        'grant_type': 'client_credentials',
        'refresh_token': spotify_api_code,
        'redirect_uri': keys.redirectUri,
        'client_id': keys.clientId,
        'client_secret': keys.clientSecret,
    }
    url = 'https://accounts.spotify.com/api/token'
    try:
        spotify_api_token = requests.post(url, params=params, headers={
            'content-type': 'application/x-www-form-urlencoded'}).json()['access_token']
    except:
        return False
    return True


# API'S INITALIZATION


def prepare_apis():
    return refresh_spotify_token()


# PROFILE FEATURES


# lastfm
data_dict = load_data()
genre_list = set(
    list(map(lambda x: x.replace('-', ' ').lower(), data_dict['genres'])))
mood_list = list(map(lambda x: x.lower(), data_dict['moods']))
ensemble_list = list(map(lambda x: x.lower(), data_dict['ensembles']))


def add_lastfm_features_profile(song_profile):
    artist = song_profile['artist']
    title = song_profile['title']
    song_profile['lastfm_found'] = False

    top_tags = []
    url = ''
    try:
        r = requests.get(
            'http://ws.audioscrobbler.com/2.0/?method=track.gettoptags&artist={}&track={}&api_key={}&format=json'.format(
                quote_plus(artist), quote_plus(title), last_fm_api_key))
        top_tags = [tag['name'].lower().replace('-', ' ').strip()
                    for tag in r.json()['toptags']['tag']]
        url = requests.get(
            'http://ws.audioscrobbler.com/2.0/?method=track.getInfo&artist={}&track={}&api_key={}&format=json'.format(
                quote_plus(artist), quote_plus(title), last_fm_api_key)).json()['track']['url']
    except:
        print('LAST FM REQUEST ERROR',
              'http://ws.audioscrobbler.com/2.0/?method=track.gettoptags&artist={}&track={}&api_key={}&format=json'.format(
                  quote_plus(artist), quote_plus(title), last_fm_api_key))
    # remove duplicates
    top_tags = list(set(top_tags))

    genre_tag_list = []
    tag_list = []  # remaining tags
    mood_tag_list = []
    ensemble_tag_list = []
    for tag in top_tags:
        if tag in genre_list:
            genre_tag_list.append(tag)
        elif tag in mood_list:
            mood_tag_list.append(tag)
        elif tag in ensemble_list:
            ensemble_tag_list.append(tag)
        elif tag not in tag_list:
            tag_list.append(tag)

    # remove more general genre tags
    genre_tag_list_aux = []
    for genre in genre_tag_list:
        found = False
        for genre_aux in genre_tag_list:
            if genre != genre_aux and genre in genre_aux:
                found = True
        if not found:
            genre_tag_list_aux.append(genre)

    vocal_sex = ''
    for tag in tag_list:
        tag_processed = tag.lower().replace('-', ' ')
        if 'male vocal' in tag_processed:
            vocal_sex = 'male'
            if 'female vocal' in tag_processed:
                vocal_sex = 'female'
            break

    genre_tag_list = genre_tag_list_aux
    song_profile['genres'] = genre_tag_list
    song_profile['moods'] = mood_tag_list
    song_profile['ensemble'] = ensemble_tag_list
    song_profile['tags'] = tag_list
    song_profile['vocal'] = [vocal_sex]
    song_profile['lastfm_url'] = url
    song_profile['lastfm_found'] = True


def add_lastfm_features(profile_list):
    thread_list = []
    for profile in profile_list:
        process = Thread(target=add_lastfm_features_profile, args=[profile])
        process.start()
        thread_list.append(process)
    for thread in thread_list:
        thread.join()


# spotify
url = 'https://api.spotify.com/v1/search?q={}%20artist:{}&limit=1&type=track'


def add_song_id(profile, song_ids, pos):
    if profile.get('spotify_id'):
        song_ids[pos] = profile.get('spotify_id')
    else:
        new_url = url.format(quote_plus(
            profile['title'].lower()), quote_plus(profile['artist'].lower()))
        try:
            r = requests.get(new_url, headers={
                'Authorization': 'Bearer ' + spotify_api_token})
            song_id = r.json()['tracks']['items'][0]['id']
        except:
            print('SPOTIFY NOT FOUND', new_url)
            song_id = None
        song_ids[pos] = song_id


def get_features(song_ids, result):
    try:
        result['features'] = requests.get('https://api.spotify.com/v1/audio-features/?ids=' + ','.join(
            song_ids), headers={'Authorization': 'Bearer ' + spotify_api_token}).json()['audio_features']
    except:
        print('SPOTIFY FEATURES ERROR')
        result['features'] = []


def get_tracks(song_ids, result):
    try:
        result['tracks'] = requests.get('https://api.spotify.com/v1/tracks/?ids=' + ','.join(
            song_ids), headers={'Authorization': 'Bearer ' + spotify_api_token}).json()['tracks']
    except:
        print('SPOTIFY TRACS ERROR')
        result['tracks'] = []


def add_spotify_features(profile_list):
    threads = []
    song_ids = [None] * len(profile_list)
    for i, profile in enumerate(profile_list):
        process = Thread(target=add_song_id, args=[profile, song_ids, i])
        process.start()
        threads.append(process)
    for thread in threads:
        thread.join()

    # marks invalid ids
    pos_list = [i for (i, song_id) in enumerate(song_ids) if song_id is None]
    song_ids = [song_id for song_id in song_ids if song_id is not None]

    # get infos
    result = {}
    threads = []
    for func in [lambda: get_tracks(song_ids, result),
                 lambda: get_features(song_ids, result)]:
        process = Thread(target=func)
        process.start()
        threads.append(process)
    for thread in threads:
        thread.join()

    i = 0
    for i1, song_profile in enumerate(profile_list):
        if i1 in pos_list:
            song_profile['features'] = []
            song_profile['era'] = None
            song_profile['popularity'] = 0
            song_profile['spotify_id'] = None
            song_profile['spotify_found'] = False
            song_profile['spotify_url'] = ''
        else:
            song_profile['spotify_id'] = song_ids[i]
            song_profile['features'] = [
                NaN if result['features'][i]['key'] == -1 else result['features'][i]['key'] / 12,
                NaN if result['features'][i]['tempo'] == 0 else result['features'][i]['tempo'] / 232,
                result['features'][i]['acousticness'],
                result['features'][i]['instrumentalness'],
                result['features'][i]['speechiness'],
                result['features'][i]['valence'],
                result['features'][i]['danceability'],
                result['features'][i]['energy'],
                (result['features'][i]['loudness'] + 60) / 60,
            ]
            published_year = dparser.parse(
                result['tracks'][i]['album']['release_date'], fuzzy=True).year
            song_profile['era'] = published_year - (published_year % 10)
            song_profile['popularity'] = result['tracks'][i]['popularity']
            song_profile['spotify_found'] = True
            song_profile['spotify_url'] = result['tracks'][i]['external_urls'].get(
                'spotify', '')
            i += 1


# PROFILES

# single profile based on song title and artist


def create_profile(title, artist):
    profile_list = [{'artist': artist, 'title': title}]
    threads = []
    for func in [add_lastfm_features, add_spotify_features]:
        process = Thread(target=func, args=[profile_list])
        process.start()
        threads.append(process)
    for thread in threads:
        thread.join()
    profile = profile_list[0]
    if profile['spotify_found'] and profile['lastfm_found']:
        return profile
    else:
        return {}


# multiple profiles based on song profile


def create_profiles(profile):
    profile_list = get_new_tracks(profile)
    threads = []
    for func in [add_lastfm_features, add_spotify_features]:
        process = Thread(target=func, args=[profile_list])
        process.start()
        threads.append(process)
    for thread in threads:
        thread.join()
    return profile_list


# GET API'S RECOMMENDATIONS
# get new tracks based on song profile
featuring_regex = re.compile('\(feat\..+\)')


def get_new_tracks(profile, limit=50):
    tracks = []
    try:
        # lastfm recommendations
        url = 'http://ws.audioscrobbler.com/2.0/?api_key={}&limit={}&method=track.getsimilar&format=json&track={}&artist={}'.format(
            last_fm_api_key, limit, quote_plus(profile['title']), quote_plus(profile['artist']))
        r = requests.get(url)
        tracks = tracks + [{'title': featuring_regex.sub('', track['name']).strip(
        ), 'artist': track['artist']['name']} for track in r.json()['similartracks']['track']]
        # Lastfm top tracks by artirst
        url = 'http://ws.audioscrobbler.com/2.0/?method=artist.gettoptracks&artist={}&api_key={}&limit={}&format=json'.format(
            quote_plus(profile['artist']), last_fm_api_key, 10)
        r = requests.get(url)
        json = r.json()
        tracks = tracks + [{'title': featuring_regex.sub('', track['name']).strip(
        ), 'artist': track['artist']['name']} for track in json['toptracks']['track']]
    except Exception:
        print('LASTFM NEW TRACKS')
    # spotify recommendations
    try:
        url = 'https://api.spotify.com/v1/recommendations?seed_tracks={}&limit={}'.format(
            profile['spotify_id'], limit)
        json = requests.get(
            url, headers={'Authorization': 'Bearer ' + spotify_api_token}).json()
        tracks = tracks + [{'title': track['name'], 'artist': track['artists']
        [0]['name'], 'spotify_id': track['id']} for track in json['tracks']]
        json = requests.get(
            url, headers={'Authorization': 'Bearer ' + spotify_api_token}).json()
        tracks = tracks + [{'title': track['name'], 'artist': track['artists']
        [0]['name'], 'spotify_id': track['id']} for track in json['tracks']]
        json = requests.get(
            url, headers={'Authorization': 'Bearer ' + spotify_api_token}).json()
        tracks = tracks + [{'title': track['name'], 'artist': track['artists']
        [0]['name'], 'spotify_id': track['id']} for track in json['tracks']]
    except Exception as e:
        print('SPOTIFY NEW TRACKS')
    # removing duplicates
    tracks_aux = []
    for track in tracks:
        found = False
        for track_aux in tracks_aux:
            if not ((track['title'].lower() == track_aux['title'].lower()) and (
                    track['artist'].lower() == track_aux['artist'].lower())):
                continue
            else:
                found = True
                break
        if not found:
            tracks_aux.append(track)
    # remove the track itself
    tracks = [track for track in tracks_aux if not (track['artist'].lower(
    ) == profile['artist'].lower() and track['title'].lower() == profile['title'].lower())]
    return tracks[:limit]
