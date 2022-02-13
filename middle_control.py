# -*- coding: utf-8 -*-
"""
Main script for computing recommendations

"""

'''
Examples 
python middle_control.py -t 'Blinded in chains' -a 'Avenged Sevenfold' 

python middle_control.py -t 'Toxicity' -a 'System of a Down' 

python middle_control.py -t 'Dirty Magic' -a 'The Offspring'

python middle_control.py -t 'My Soul to Keep' -a 'The Creepshow'

python middle_control.py -t 'Pupila' -a 'Anavitória'

python middle_control.py -t 'Bixinho' -a 'DUDA BEAT'

python middle_control.py -t 'Before I forget' -a 'Slipknot'

python middle_control.py -t 'Believer' -a 'Imagine Dragons'

python middle_control.py -t 'Enter Sandman' -a 'Metallica'  

python middle_control.py -t 'Meteoro' -a 'Luan Santana'  

python middle_control.py -t '' -a '' 
'''

import time

from recommendations import get_recommendations, print_recommendations


def middle(artist: str, title: str, limit: int):
    start = time.time()
    profile, recommendations, status = get_recommendations(title, artist, limit)
    end = time.time()
    print('Time passed: {} seconds'.format(end - start))
    if not status['error']:
        return print_recommendations(profile, recommendations)
    else:
        return 'Processing error:', status['error']

#
# if __name__ == '__main__':
#     argv = sys.argv
#     try:
#         if argv[1] == '-t':
#             title = argv[2]
#         if argv[3] == '-a':
#             artist = argv[4]
#         if len(sys.argv) == 5:
#             limit = 10
#         elif argv[5] == '-l':
#             limit = int(argv[6])
#         title, artist
#     except Exception as e:
#         print(e)
#         print('middle_control.py -t <track_title> -a <artist_name> -lastindex() <limit>')
#         sys.exit(1)
#     print('Getting {} recommendations for {} by {}\n'.format(limit, title, artist))
#     main(artist, title, limit)
