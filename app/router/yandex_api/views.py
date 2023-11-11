import urllib.parse as urlparse
import uuid

from flask import redirect, request, make_response
from flask.blueprints import Blueprint

import jmespath

from core.settings import Settings

from .api import (
    YandexDirectApi,
    ReportGeneratedOffline,
    ReportAddedOfflineQsueue
)


yandex_api_router = Blueprint('yandex', __name__)
yandex_direct_api = YandexDirectApi(
    ads_client_login=Settings.yandex.client_login,
    client_id=Settings.yandex.client_id,
    client_secret=Settings.yandex.client_secret
)

@yandex_api_router.get('/login')
def yandex_oauth_login():

    data = urlparse.urlencode({
        'response_type': 'code',
        'client_id': Settings.yandex.client_id
    })
    return redirect(f'https://oauth.yandex.ru/authorize?{data}')

@yandex_api_router.get('/login/callback')
def yandex_oauth_callback():

    auth_code = request.args.get('code')

    if auth_code is None:
        return redirect('/')

    response = make_response(redirect('/'))
    response.set_cookie(
        key='yandex_token',
        value=yandex_direct_api.get_access_token(auth_code),
        max_age=31_104_000,
        domain=Settings.domain,
        secure=True,
        httponly=True
    )
    return response

@yandex_api_router.post('/account-statistic')
def get_account_statistic():

    token = request.cookies.get('yandex_token')
    response_json = request.get_json()
    report_name = response_json.get('report_name', uuid.uuid4())

    if not token:
        return redirect('/')

    field_names = (
        'Date',
        'Impressions',
        'Clicks',
        'Cost'
    )

    try:
        data = yandex_direct_api.get_report(
            access_token=token,
            field_names=field_names,
            report_type='ACCOUNT_PERFORMANCE_REPORT',
            report_name=report_name
        )
    except ReportAddedOfflineQsueue:
        return {'report_name': report_name}, 201
    except ReportGeneratedOffline:
        return {'report_name': report_name}, 201

    return {
        'report_name': report_name,
        'data': data
    }

@yandex_api_router.post('/search-queries')
def get_search_queries():

    token = request.cookies.get('yandex_token')
    response_json = request.get_json()
    report_name = response_json.get('report_name', uuid.uuid4())

    if not token:
        return redirect('/')

    field_names = (
        'AdGroupId',
        'CampaignName',
        'CampaignType',
        'Clicks',
        'Impressions'
    )

    try:
        data = yandex_direct_api.get_report(
            access_token=token,
            field_names=field_names,
            report_type='SEARCH_QUERY_PERFORMANCE_REPORT',
            report_name=report_name
        )
    except ReportAddedOfflineQsueue:
        return {'report_name': report_name}, 201
    except ReportGeneratedOffline:
        return {'report_name': report_name}, 201

    return {
        'report_name': report_name,
        'data': data
    }

@yandex_api_router.post('/negative-keywords')
def get_negative_keywords():

    token = request.cookies.get('yandex_token')

    if not token:
        return redirect('/')
    
    negative_keywords = yandex_direct_api.get_negative_keywords(token)
    data = jmespath.search(
        expression='result.NegativeKeywordSharedSets[].NegativeKeywords | []',
        data=negative_keywords
    )
    return {
        'data': data
    }
