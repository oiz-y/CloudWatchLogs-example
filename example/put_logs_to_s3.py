import os
import json
import time
import datetime
import boto3

logs_client = boto3.client('logs')
s3_client = boto3.client('s3')

def change_milli_to_datetime(milli_seconds, is_jst=False):
    if is_jst:
        utc_datetime = datetime.datetime.fromtimestamp(milli_seconds / 1000)
        return_datetime = utc_datetime + datetime.timedelta(hours=9)
    else:
        return_datetime = datetime.datetime.fromtimestamp(milli_seconds / 1000)
    return return_datetime.strftime('%Y-%m-%d %H:%M:%S')

def _get_custom_log_events(log_group_name, log_stream_name, next_token=''):
    if next_token == '':
        response = logs_client.get_log_events(
            logGroupName=log_group_name,
            logStreamName=log_stream_name,
            startFromHead=True
        )
    else:
        response = logs_client.get_log_events(
            logGroupName=log_group_name,
            logStreamName=log_stream_name,
            startFromHead=True,
            nextToken=next_token
        )
    return response['events'], response['nextForwardToken']

def get_custom_log_events(log_group_name, log_stream_name):
    next_token = ''
    merge_log_events = []
    log_events, next_token = _get_custom_log_events(
        log_group_name, log_stream_name, next_token=next_token)
    merge_log_events.extend(log_events)
    while len(log_events) > 0:
        log_events, next_token = _get_custom_log_events(
            log_group_name, log_stream_name, next_token=next_token)
        merge_log_events.extend(log_events)
    make_log_file(log_group_name, log_stream_name, merge_log_events)

def make_log_file(log_group_name, log_stream_name, log_events):
    log_file_name = f'{log_group_name}/{log_stream_name}.log'
    log_file = os.path.join('/tmp', log_file_name)
    os.makedirs(os.path.split(log_file)[0], exist_ok=True)
    with open(log_file, 'w') as f:
        for event in log_events:
            record = '\t'.join([
                change_milli_to_datetime(event['timestamp'], is_jst=True),
                event['message']
            ])
            f.write(f'{record}\n')
    s3_client.upload_file(
        log_file,
        'cloudwatchlogs-upload-logs',
        os.path.join(
            'tmp',
            os.path.split(log_file_name)[0],
            datetime.datetime.now().strftime('%Y%m%d-%H%M%S') + '_' + os.path.split(log_file_name)[1]
        )
    )

def lambda_handler(event, context):
    log_group_name = 'my-log-group'
    log_stream_name = 'test-log-stream-5'
    get_custom_log_events(log_group_name, log_stream_name)
