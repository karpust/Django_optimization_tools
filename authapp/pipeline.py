from collections import OrderedDict
from datetime import datetime
from urllib.parse import urlencode, urlunparse
import requests
from django.utils import timezone
from social_core.exceptions import AuthForbidden
from authapp.models import ShopUserProfile


def save_user_profile(backend, user, response, *args, **kwargs):
    if backend.name != 'vk-oauth2':
        return
    api_url = urlunparse(('https',
                          'api.vk.com',
                          '/method/users.get',
                          None,
                          urlencode(OrderedDict(fields=','.join((
                              'bdate', 'sex', 'about', 'lang', 'id')),
                              access_token=response['access_token'],
                              v='5.92')), None
                          ))
# https://api.vk.com/method/users.get?fields=bdate%2Csex%2Cabout&access_token=vk1.a.lFFKKe-nkfG__hUmHlnaGmuD9HjbqTzLNu3ulfVP3LmWG1C30BeqZzsySULiWVq8PvGDGr_p2E1S_cqMNiTMAyZRGGpwX8q9hKifQ-BbtzyEmlYd1m9WOSpXBSaLm0PsJewvdNpBhcRniAm6DdPfHRF3nLY1pWkSGc_ZXyh060mkB1Uv-TfJGkYOiRxLXg2V&v=5.92
    resp = requests.get(api_url)
    if resp.status_code != 200:
        return
    data = resp.json()['response'][0]

    if data['sex']:
        user.shopuserprofile.gender = ShopUserProfile.MALE if data['sex'] == 2 else ShopUserProfile.FEMALE

    if data['about']:
        user.shopuserprofile.aboutMe = data['about']

    if data['language']:
        langs = {
            '0': 'ru', '1': 'uk', '2': 'be', '3': 'en', '4': 'es', '5': 'fi', '6': 'de', '7': 'it'
        }
        user.shopuserprofile.vk_lang = langs[data['language']]

    if data['id']:
        user.shopuserprofile.vk_url = 'https://vk.com/id' + str(data['id'])

    if data['bdate']:
        bdate = datetime.strptime(data['bdate'], '%d.%m.%Y').date()
        age = timezone.now().date().year - bdate.year
        if age < 18:
            user.delete()
            raise AuthForbidden('social_core.backends.vk.VKOAuth2')
    user.save()
