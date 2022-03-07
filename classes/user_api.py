import vk_api
from vk_api.tools import VkTools
from vk_api.upload import VkUpload
import requests
from io import BytesIO
from db import VkDb, add_user, Base, engine




USER_TOKEN = '7ba0e1f686a68f97a4478e077220f3e8100719dfca49ee29da0f8d71c3dacc332fedbd288bd26caac62aa'
Base.metadata.create_all(engine) # создаем таблицы
vk_user_session = vk_api.VkApi(token=USER_TOKEN)
tools = VkTools(vk_user_session)
upload = VkUpload(vk_user_session)


def find_users(**kwargs):
    users = []

    params = {'sort': 1,
              'has_photo': 1,
              'fields': 'sex, city, relation, domain, bdate, hometown'
              }

    users_iter = tools.get_all_iter('users.search', max_count=10, values={**params, **kwargs})
    for user in users_iter:
        print(user)

        if add_user(user['id']):
            users.append(user['id'])
        else:
            print('запись существует')
            pass
    if len(users) == 0:
        return False

    print(users)
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
        user_photos[user_id] = []
        for photo in data['items']:
            user_photos[user_id].append((
                photo['likes']['count'],
                photo['sizes'][-1]['url']
            ))
        user_photos[user_id].sort(key=lambda x: (x[0], x[1]), reverse=True)
        if data['count'] > 3:
            user_photos[user_id] = user_photos[user_id][:3]
        else:
            user_photos[user_id] = user_photos[user_id]

    print(user_photos)
    return user_photos


def give_photos_to_user(user_photos):
    # attachments = dict()
    attachments = []

    for user_id, photos in user_photos.items():
        photos_list = []
        user_link = f'https://vk.com/id{str(user_id)}'
        # attachments[user_link] = []
        # user_name = get_fullname(user_id)
        for photo in photos:
            photo_bytes = requests.get(photo[1]).content
            # print(img)
            photo_object = BytesIO(photo_bytes)
            # print(f)
            response = upload.photo_messages(photo_object)[0]
            print(response)
            owner_id = response['owner_id']
            photo_id = response['id']
            access_key = response['access_key']
            photos_list.append(f'photo{owner_id}_{photo_id}_{access_key}')
        attachments.append([user_link, photos_list])
    print(attachments)
    return attachments

# def upload_photos(attachments):
