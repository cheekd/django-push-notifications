import json
from datetime import timedelta, datetime

from django.core.exceptions import ImproperlyConfigured
import requests

from .base import BaseService

ONESIGNAL_REQUEST_URL   = 'https://onesignal.com/api/v1/'
ONESIGNAL_NOTIFY_URL    = ONESIGNAL_REQUEST_URL + 'notifications'

class OneSignalService(BaseService):

    def __init__(self, settings):
        self.auth_token = settings.get('AUTH_TOKEN')
        self.app_id = settings.get('APP_ID')

        if not self.auth_token:
            raise ImproperlyConfigured('For OneSignal to work you need an '
                                       'AUTH_TOKEN in the configuration')

    @staticmethod
    def process_expiry(expiry):
        """
        Processes the expiry, checks if it's a datetime or timedelta and
        responds accordingly
        """
        if isinstance(expiry, datetime):
            expiry = expiry.second

        if isinstance(expiry, timedelta):
            expiry = expiry.seconds
        return expiry

    def get_auth_headers(self):
        return {
            'Accept':'application/json',
            'Content-Type':'application/json',
            'Authorization': 'Basic {}'.format(self.auth_token),
        }

    def send_push_notification(self, devices, message,
                               badge_number=None, sound=None,
                               payload=None, expiry=None,
                               category=None):
        """
        Sends a push notification request to OneSignal.
        """
        if len(devices):
            params = {
                'app_id' :self.app_id,
                'isIos' : True,
                'include_ios_tokens':[device.token for device in devices]
            }

            if message is not None:
                params.update({'contents': {'en' : message}})

            if sound is not None:
                params.update({"ios_sound": sound})

            if badge_number is not None:
                params.update({"ios_badgeType": "SetTo"})
                params.update({"ios_badgeCount" :badge_number})

            if payload is not None:
                params.update({"data": payload})

            response = requests.post(ONESIGNAL_NOTIFY_URL, data=json.dumps(params).encode('utf-8'),
                                     headers=self.get_auth_headers())

            if response.ok:
                return True

        return False
