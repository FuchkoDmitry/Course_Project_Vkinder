import vk_api
from random import randrange
import os

group_token = os.getenv('GROUP_TOKEN')
vk_group_session = vk_api.VkApi(token=group_token)


def write_message(user_id=None, message=None, keyboard=None, attachment=None):
    post = {'user_id': user_id,
            'random_id': randrange(10 ** 7),
            }
    if message:
        post['message'] = message

    if keyboard:
        post['keyboard'] = keyboard.get_keyboard()

    if attachment:
        post['attachment'] = attachment

    vk_group_session.method('messages.send', post)


def get_fullname(user_id):
    request = vk_group_session.method('users.get', values={'user_ids': user_id})[0]
    first_name = request['first_name']
    last_name = request['last_name']
    return first_name, last_name
