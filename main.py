# import vk_api
# from vk_api.longpoll import VkLongPoll, VkEventType
# from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType
# from random import randrange
# from vk_api.keyboard import VkKeyboard, VkKeyboardColor, VkKeyboardButton
# from vk_api.upload import VkUpload
# from vk_api.utils import get_random_id
# import re
# from data import cities, sex, relation
# from test_function import find_users, get_photos_for_founded_users
# import requests
# from io import BytesIO
#
#
# GROUP_TOKEN = '242ccb4880c150584eaa54371361c18bff724d7969d0705af912250f3b2468ec7d71eb23a50ec38aedf75'
# USER_TOKEN = '7ba0e1f686a68f97a4478e077220f3e8100719dfca49ee29da0f8d71c3dacc332fedbd288bd26caac62aa'
# # USER_ID = '1136869'
#
#
# vk_session = vk_api.VkApi(token=GROUP_TOKEN)
# longpoll = VkLongPoll(vk_session)
# upload = VkUpload(vk_session)
#
#
#
# vk = vk_session.get_api()
#
#
# def write_message(user_id, message=None, keyboard=None, attachment=None):
#     post = {'user_id': user_id,
#             'random_id': randrange(10 ** 7),
#             'peer_id': user_id
#             }
#     if message:
#         post['message'] = message
#
#     if keyboard:
#         post['keyboard'] = keyboard.get_keyboard()
#
#     if attachment:
#         post['attachment'] = attachment
#
#     vk_session.method('messages.send', post)
#
#
# def get_fullname(user_id):
#     request = vk.users.get(user_ids=user_id)[0]
#     first_name = request['first_name']
#     last_name = request['last_name']
#     return f'{first_name} {last_name}'
#
#
# def give_photos_to_user(user_photos):
#     for user_id, photos in user_photos.items():
#         # attachments = []
#         user_link = f'https://vk.com/id{str(user_id)}'
#         # user_name = get_fullname(user_id)
#         keyboard = VkKeyboard(one_time=True)
#         keyboard.add_openlink_button(user_link, user_link)
#         write_message(event.user_id, message=user_link, keyboard=keyboard)
#         for photo in photos:
#             img = requests.get(photo[1]).content
#             # print(img)
#             f = BytesIO(img)
#             # print(f)
#             response = upload.photo_messages(f)[0]
#             print(response)
#             owner_id = response['owner_id']
#             photo_id = response['id']
#             access_key = response['access_key']
#             attachment = f'photo{owner_id}_{photo_id}_{access_key}'
#             print(attachment)
#             # upload.photo_messages()
#             write_message(uid, attachment=attachment)
#             # attachments.append(f'photo{owner_id}_{photo_id}_{access_key}')
#
#         # write_message(event.user_id, )
#
#
# for event in longpoll.listen():
#     if event.type == VkEventType.MESSAGE_NEW and event.to_me:
#
#         text = event.text.lower()
#         uid = event.user_id
#         # print(user_id)
#         # first_name, last_name = get_fullname(user_id)
#         # USER_TOKEN = '7ba0e1f686a68f97a4478e077220f3e8100719dfca49ee29da0f8d71c3dacc332fedbd288bd26caac62aa'
#
#         if text == 'start':
#
#             keyboard = VkKeyboard(one_time=True)
#             keyboard.add_button('Давай', color=VkKeyboardColor.PRIMARY)
#             keyboard.add_button('Нет', color=VkKeyboardColor.NEGATIVE)
#
#             write_message(uid, f'Привет {get_fullname(uid)}. Поищем вторую половинку?', keyboard)
#
#         elif text == 'давай':
#             keyboard = VkKeyboard(one_time=True)
#             keyboard.add_button('Мужской', color=VkKeyboardColor.NEGATIVE)
#             keyboard.add_button('Женский', color=VkKeyboardColor.SECONDARY)
#             write_message(uid, f'{get_fullname(uid)}, выбери пол: ', keyboard)
#
#         elif text == 'нет':
#             write_message(uid, f'Пока {get_fullname(uid)}.')
#
#         elif text in sex:
#             gender = sex[text]
#             write_message(uid, f'{get_fullname(uid)}, напиши возраст: ')
#
#         elif re.search(r'^[0-9]{1,3}', text):
#             age = int(text)
#
#             keyboard = VkKeyboard(one_time=True)
#             keyboard.add_button('замужем/женат', color=VkKeyboardColor.NEGATIVE)
#             keyboard.add_button('не замужем/не женат', color=VkKeyboardColor.POSITIVE)
#             keyboard.add_line()
#             keyboard.add_button('есть друг/есть подруга', color=VkKeyboardColor.SECONDARY)
#             keyboard.add_button('В активном поиске', color=VkKeyboardColor.PRIMARY)
#             write_message(uid, f'{get_fullname(uid)}, выбери семейное положение: ', keyboard)
#
#         elif text in relation:
#             status = relation[text]
#             write_message(uid, 'выбери город поиска:')
#
#         elif text in cities:
#             city = text
#
#             keyboard = VkKeyboard(one_time=True)
#             keyboard.add_button('search', color=VkKeyboardColor.PRIMARY)
#             write_message(uid, f'{get_fullname(uid)}, напиши search для поиска.', keyboard)
#
#         elif text == 'search':
#             users = find_users(gender, age, city, status)
#             user_photos = get_photos_for_founded_users(users)
#             give_photos_to_user(user_photos)
#             # for user, photos in user_photos.items():





