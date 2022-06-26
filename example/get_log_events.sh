function get_log_events_with_token () {
  log_group_name=${1}
  log_stream_name=${2}
  output_log_file=${3}
  next_token=${4}
  aws logs get-log-events \
    --log-group-name ${log_group_name} \
    --log-stream-name ${log_stream_name} \
    --start-from-head \
    --next-token ${next_token} \
    | jq -r '.events[] | [(.timestamp / 1000 | strftime("%Y-%m-%d %H:%M:%S")), (."message")] | @tsv' \
  >> ${output_log_file}
}

function get_log_events () {
  log_group_name=${1}
  log_stream_name=${2}
  output_log_file=${3}
  aws logs get-log-events \
    --log-group-name ${log_group_name} \
    --log-stream-name ${log_stream_name} \
    --start-from-head \
    | jq -r '.events[] | [(.timestamp / 1000 | strftime("%Y-%m-%d %H:%M:%S")), (."message")] | @tsv' \
  >> ${output_log_file}
}

function get_next_token_with_token () {
  log_group_name=${1}
  log_stream_name=${2}
  next_token=${3}
  aws logs get-log-events \
    --log-group-name ${log_group_name} \
    --log-stream-name ${log_stream_name} \
    --start-from-head \
    --next-token ${next_token} \
    | jq '.nextForwardToken'
}

function get_next_token () {
  log_group_name=${1}
  log_stream_name=${2}
  aws logs get-log-events \
    --log-group-name ${log_group_name} \
    --log-stream-name ${log_stream_name} \
    --start-from-head \
    | jq '.nextForwardToken'
}

log_group_name=${1}
log_stream_name=${2}
output_log_file="${log_stream_name}.log"

if [ "${log_group_name}" = '' ] || [ "${log_stream_name}" = '' ]; then
  echo 'arg1: Log group name'
  echo 'arg2: Log stream name'
  exit 1
fi

next_forward_token='not set next token'
prev_token='not set prev token'

while [ "${prev_token}" != "${next_forward_token}" ];
do
  echo "next_forward_token: ${next_forward_token}    prev_token: ${prev_token}"
  prev_token=${next_forward_token}
  if [ "${next_forward_token}" != 'not set next token' ]; then
    get_log_events_with_token ${log_group_name} ${log_stream_name} ${output_log_file} ${next_forward_token}
    next_forward_token=`get_next_token_with_token ${log_group_name} ${log_stream_name} ${next_forward_token} | sed 's/"//g'`
  else
    get_log_events ${log_group_name} ${log_stream_name} ${output_log_file}
    next_forward_token=`get_next_token ${log_group_name} ${log_stream_name} | sed 's/"//g'`
  fi
done
