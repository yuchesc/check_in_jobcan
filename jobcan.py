import requests
from bs4 import BeautifulSoup


class Jobcan:
    login_url = "https://id.jobcan.jp/users/sign_in"
    top_url = "https://ssl.jobcan.jp/jbcoauth/login"
    adit_url = "https://ssl.jobcan.jp/employee/index/adit"
    session = None

    @staticmethod
    def get_authenticity_token(soup):
        inputs = filter(lambda x: x['name'] == 'authenticity_token', soup.find_all('input'))
        for tag in inputs:
            return tag['value']

    @staticmethod
    def get_token(soup):
        inputs = filter(lambda x: x['name'] == 'token', soup.find_all('input'))
        for tag in inputs:
            return tag['value']

    @staticmethod
    def get_option(soup):
        return soup.find('option')['value']

    def create_checkin_data(self, token, adit_group_id):
        return self.create_submit_data(token, adit_group_id, '', 'DEF')

    def create_checkout_data(self, token, adit_group_id, notice):
        return self.create_submit_data(token, adit_group_id, notice, 'work_end')

    @staticmethod
    def create_submit_data(token, adit_group_id, notice, adit_item):
        return {
            'is_yakin': 0,
            'adit_item': adit_item,
            'notice': notice,
            'token': token,
            'adit_group_id': adit_group_id,
            '_': ''
        }

    def login(self, user_email, user_password):
        self.session = requests.session()

        payload = dict()
        payload['utf8'] = '✓'
        payload['commit'] = 'ログイン'
        payload['user[email]'] = user_email
        payload['user[client_code]'] = ''
        payload['user[password]'] = user_password

        r = self.session.get(self.login_url)
        if r.status_code != 200:
            raise Exception('Invalid top response. {}'.format(r.status_code))
        parsed_body = BeautifulSoup(r.text, 'html.parser')
        auth_token = self.get_authenticity_token(parsed_body)
        payload['authenticity_token'] = auth_token

        r = self.session.post(self.login_url, payload)
        if r.status_code != 200:
            raise Exception('Invalid login response. {}'.format(r.status_code))

        r = self.session.get(self.top_url)
        if r.status_code != 200:
            raise Exception('Invalid top response. {}'.format(r.status_code))
        return r.text

    def checkin(self, user_email, user_password):
        body = self.login(user_email, user_password)
        if body.find('current_status = "working"') >= 0:
            raise Exception('Already working.')
        else:
            parsed_body = BeautifulSoup(body, 'html.parser')
            current_token = self.get_token(parsed_body)
            opt = self.get_option(parsed_body)
            data = self.create_checkin_data(current_token, opt)
            print(data)
            r = self.session.post(self.adit_url, data)
            if r.status_code != 200:
                raise Exception('error occurred. {}'.format(r.status_code))

    def checkout(self, user_email, user_password, notice):
        body = self.login(user_email, user_password)
        if body.find('current_status = "working"') >= 0:
            parsed_body = BeautifulSoup(body, 'html.parser')
            current_token = self.get_token(parsed_body)
            opt = self.get_option(parsed_body)
            data = self.create_checkout_data(current_token, opt, notice)
            r = self.session.post(self.adit_url, data)
            if r.status_code != 200:
                raise Exception('error occured. {}'.format(r.status_code))
        else:
            raise Exception('Not working.')
