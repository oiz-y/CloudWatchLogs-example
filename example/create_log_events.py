import json
import time
import datetime
import uuid
import boto3

client = boto3.client('logs')

def get_log_stream_token(log_group_name, log_stream_name):
    response = client.describe_log_streams(
        logGroupName=log_group_name,
        logStreamNamePrefix=log_stream_name,
    )
    log_streams = response['logStreams']
    log_stream = log_streams[0]
    log_stream_token = log_stream['uploadSequenceToken']
    return log_stream_token

def put_custom_log_event(log_group_name, log_stream_name, log_stream_token):
    next_token = ''
    for i in range(50):
        if next_token == '':
            response = client.put_log_events(
                logGroupName=log_group_name,
                logStreamName=log_stream_name,
                logEvents=[
                    {
                        'timestamp': int(time.time()) * 1000,
                        'message': str(uuid.uuid4())
                    },
                ],
                sequenceToken=log_stream_token
            )
        else:
            try:
                response = client.put_log_events(
                    logGroupName=log_group_name,
                    logStreamName=log_stream_name,
                    logEvents=[
                        {
                            'timestamp': int(time.time()) * 1000,
                            'message': str(uuid.uuid4())
                        },
                    ],
                    sequenceToken=next_token
                )
            except Exception as exc:
                print(f'error {i}')
        next_token = response['nextSequenceToken']

def lambda_handler(event, context):
    print(event)
    log_group_name = 'my-log-group'
    log_stream_name = 'test-log-stream-5'
    log_stream_token= get_log_stream_token(log_group_name, log_stream_name)
    put_custom_log_event(log_group_name, log_stream_name, log_stream_token)
    inc = {'Count': event['Count'] + 1}
    return inc
