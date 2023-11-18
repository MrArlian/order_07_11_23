import urllib.parse as urlparse
import typing
import json
import uuid

import requests


class ReportAddedOfflineQsueue(Exception):
    """..."""

class ReportGeneratedOffline(Exception):
    """..."""


class YandexDirectApi:

    def __init__(
        self,
        ads_client_login: str,
        access_token: str = None,
        client_id: str = None,
        client_secret: str = None,
        version: str = 'v5',
        api_url: str = 'https://api.direct.yandex.com/json',
        oauth_url: str = 'https://oauth.yandex.ru'
    ) -> None:

        self.client_id = client_id
        self.client_secret = client_secret

        self.token = access_token
        self.ads_client_login = ads_client_login

        self.api_version = version
        self.api_url = api_url
        self.oauth_url = oauth_url

        self.session = requests.Session()
        self._timeout = 5
        self._headers = {
            'Content-Type': 'application/json',
            'Client-Login': self.ads_client_login,
        }

    def _do_request(
        self,
        method: str,
        path: typing.Union[typing.Iterable[str], str],
        access_token: str = None,
        data: dict = None,
        params: dict = None
    ) -> requests.Response:

        assert not (access_token is None and self.token is None)

        if isinstance(path, str):
            path = (path,)

        _data = json.dumps(data or {})
        _url = '/'.join((self.api_url, self.api_version, *path))
        _params = urlparse.urlencode(params or {}, encoding='utf-8')
        _headers = {
            'Authorization': f'Bearer {access_token or self.token}'
        }

        response = self.session.request(
            method=method,
            url=_url,
            data=_data,
            params=_params,
            headers=self._headers | _headers,
            timeout=self._timeout,
            allow_redirects=False
        )
        return response

    def get_report(
        self,
        access_token: str,
        field_names: typing.Iterable[str],
        report_type: str,
        report_name: str = None
    ) -> None:
        """
            ...
        """
        data = {
            'params': {
                'SelectionCriteria': {},
                'FieldNames': field_names,
                'ReportName': report_name or uuid.uuid4().hex,
                'ReportType': report_type,
                'DateRangeType': 'ALL_TIME',
                'Format': 'TSV',
                'IncludeVAT': 'YES',
                'IncludeDiscount': 'YES'
            }
        }
        response = self._do_request(
            method='post',
            path='reports',
            access_token=access_token,
            data=data
        )

        if response.status_code == 201:
            raise ReportAddedOfflineQsueue
        elif response.status_code == 202:
            raise ReportGeneratedOffline
        elif response.status_code == 4000:
            raise Exception

        return response.text

    def get_negative_keywords(self, access_token: str) -> dict:
        """
            ...
        """
        data = {
            'method': 'get',
            'params': {
                'FieldNames': ['NegativeKeywords']
            }
        }
        response = self._do_request(
            method='post',
            path='negativekeywordsharedsets',
            access_token=access_token,
            data=data
        )
        return response.json()

    def get_access_token(
        self,
        code: str,
        client_id: str = None,
        client_secret: str = None
    ) -> str:
        """
            ...
        """
        data = {
            'grant_type': 'authorization_code',
            'code': code,
            'client_id': self.client_id or client_id,
            'client_secret': self.client_secret or client_secret
        }
        response = self.session.post(f'{self.oauth_url}/token', data)

        if response.status_code != 200:
            raise ValueError

        return response.json().get('access_token')
