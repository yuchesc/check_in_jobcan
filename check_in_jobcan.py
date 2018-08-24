import boto3
import os
import requests
from bs4 import BeautifulSoup

login_url = "https://id.jobcan.jp/users/sign_in"
top_url = "https://ssl.jobcan.jp/jbcoauth/login"
adit_url = "https://ssl.jobcan.jp/employee/index/adit"

sns_topic_arn = os.environ.get('sns_topic_arn', '')


def get_authenticity_token(soup):
    inputs = filter(lambda x: x['name'] == 'authenticity_token', soup.find_all('input'))
    for tag in inputs:
        return tag['value']


def get_token(soup):
    inputs = filter(lambda x: x['name'] == 'token', soup.find_all('input'))
    for tag in inputs:
        return tag['value']


def get_option(soup):
    return soup.find('option')['value']


def create_submit_data(token, adit_group_id):
    return {
        'is_yakin': 0,
        'adit_item': 'DEF',
        'notice': '',
        'token': token,
        'adit_group_id': adit_group_id,
        '_': ''
    }


def check_in():
    sns = boto3.client('sns')
    try:
        session = requests.session()

        payload = dict()
        payload['utf8'] = '✓'
        payload['commit'] = 'ログイン'
        payload['user[email]'] = os.environ.get('user_email')
        payload['user[client_code]'] = ''
        payload['user[password]'] = os.environ.get('user_password')

        r = session.get(login_url)
        if r.status_code != 200:
            raise Exception('Invalid top response. {}'.format(r.status_code))
        parsed_body = BeautifulSoup(r.text, 'html.parser')
        auth_token = get_authenticity_token(parsed_body)
        payload['authenticity_token'] = auth_token

        r = session.post(login_url, payload)
        if r.status_code != 200:
            raise Exception('Invalid login response. {}'.format(r.status_code))

        r = session.get(top_url)
        if r.status_code != 200:
            raise Exception('Invalid top response. {}'.format(r.status_code))
        body = r.text

        if body.find('current_status = "working"') >= 0:
            raise Exception('Already working.')
        else:
            parsed_body = BeautifulSoup(body, 'html.parser')
            current_token = get_token(parsed_body)
            opt = get_option(parsed_body)
            data = create_submit_data(current_token, opt)
            print(data)
            r = session.post(adit_url, data)
            if r.status_code != 200:
                raise Exception('error occurred. {}'.format(r.status_code))
            if sns_topic_arn != '':
                sns.publish(TopicArn=sns_topic_arn, Subject='OK Jobcan Checkin', Message='200')
            return 204
    except Exception as e:
        sns.publish(TopicArn=sns_topic_arn, Subject='NG Jobcan Checkin', Message=str(e))
        raise e


def lambda_handler(event, context):
    return check_in()
