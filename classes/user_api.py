import json.decoder

import vk_api
from vk_api.tools import VkTools
from vk_api.upload import VkUpload
import requests
from io import BytesIO
from db import Users, add_user_to_db, Base, engine, find_user_in_db
from vk_api.exceptions import ApiError




USER_TOKEN = '7ba0e1f686a68f97a4478e077220f3e8100719dfca49ee29da0f8d71c3dacc332fedbd288bd26caac62aa'

vk_user_session = vk_api.VkApi(token=USER_TOKEN)
tools = VkTools(vk_user_session)
upload = VkUpload(vk_user_session)


def find_users(**kwargs):
    users = []

    params = {'sort': 0,
              'has_photo': 1,
              'is_closed': False,
              'fields': 'sex, city, relation, domain, bdate, hometown'
              }

    users_iter = tools.get_all_iter('users.search', max_count=4, values={**params, **kwargs})
    for user in users_iter:
        if find_user_in_db(Users, user['id']) or user['is_closed']:
            # print(f'{user["id"]} есть в базе')
            continue
        else:
            # print(f'{user} добавлен')
            users.append(user['id'])

        # if add_user_to_db(user['id']):
        #     users.append(user['id'])
        #     print(f'{user} добавлен')
        # else:
        #     print('запись существует')
        #     print(f'{user} не добавлен')
        #     continue
    if len(users) == 0:
        return False
    print('find_users отработала', len(users))

    return users


def get_photos_for_founded_users(user_list):
    user_photos = dict()

    default_values = {
                      'album_id': 'profile',
                      'extended': 1, 'photo_sizes': 1
                     }

    users_photos, errors = vk_api.vk_request_one_param_pool(
        vk_user_session,
        'photos.get',
        key='user_id',
        values=user_list,
        default_values=default_values
    )

    for user_id, data in users_photos.items():

        if data['count'] == 0:
            continue
        else:
            user_photos[user_id] = []
            for photo in data['items']:
                user_photos[user_id].append((
                    photo['likes']['count'],
                    photo['sizes'][-1]['url']
                ))
            # print(f'{user_id} добавлен')

        if data['count'] > 3:
            user_photos[user_id].sort(key=lambda x: (x[0], x[1]), reverse=True)
            user_photos[user_id] = user_photos[user_id][:3]
        # print(user_photos)

        # else:
        #     user_photos[user_id] = user_photos[user_id]
    print(f'get_photos_for_founded_users() отработала')

    return user_photos


# def give_photos_to_user(user_photos):
#
#     attachments = []
#
#     for user_id, photos in user_photos.items():
#         photos_list = []
#         for photo in photos:
#             photo_bytes = requests.get(photo[1]).content
#             photo_object = BytesIO(photo_bytes)
#
#             try:
#                 response = upload.photo_messages(photo_object)[0]
#
#                 owner_id = response['owner_id']
#                 photo_id = response['id']
#                 access_key = response['access_key']
#                 photos_list.append(f'photo{owner_id}_{photo_id}_{access_key}')
#
#             except Exception as er:
#                 print('error', photo)
#                 # print(er)
#                 continue
#             except json.decoder.JSONDecodeError:
#                 print('json decode error', photo)
#         attachments.append([user_id, photos_list])
#     print('give_photos_to user отработала')
#     return attachments
