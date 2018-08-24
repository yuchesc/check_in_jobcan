import boto3
import os
from jobcan import Jobcan

sns_topic_arn = os.environ.get('sns_topic_arn', '')


def check_in():
    sns = boto3.client('sns')
    try:
        jobcan = Jobcan()
        jobcan.checkin(os.environ.get('user_email'), os.environ.get('user_password'))
        if sns_topic_arn != '':
            sns.publish(TopicArn=sns_topic_arn, Subject='OK Jobcan Checkin', Message='200')
        return 204
    except Exception as e:
        if sns_topic_arn != '':
            sns.publish(TopicArn=sns_topic_arn, Subject='NG Jobcan Checkin', Message=str(e))
        raise e


def lambda_handler(event, context):
    return check_in()
