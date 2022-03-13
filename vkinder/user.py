import vk_api
from vk_api.tools import VkTools
from vkinder.db import Users, find_user_in_db, find_in_blacklisted
from keys import USER_TOKEN


user_token = USER_TOKEN
vk_user_session = vk_api.VkApi(token=user_token)
tools = VkTools(vk_user_session)


def find_users(**kwargs):
    users = []

    params = {'sort': 0,
              'has_photo': 1,
              'is_closed': False,
              'fields': 'sex, city, relation, domain, bdate, hometown'
              }

    users_iter = tools.get_all_iter('users.search', max_count=1000, values={**params, **kwargs})
    for user in users_iter:
        if find_user_in_db(Users, user['id']) or user['is_closed'] or find_in_blacklisted(user['id']):
            continue
        else:
            users.append(user['id'])
    if len(users) == 0:
        return False
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

        if data['count'] > 3:
            user_photos[user_id].sort(key=lambda x: (x[0], x[1]), reverse=True)
            user_photos[user_id] = user_photos[user_id][:3]

    return user_photos
