#############################################
#
# CONFIGURATION VARIABLES - EDITABLE
# MODIFY WITH CAUTION
#
#############################################
function init() {
  HELPER_JS_FILE="./.dbCtlHelper.js"
  [ -f ${HELPER_JS_FILE} ] || { echo "FATAL JS HELPER FILE MISSING"; exit 1; }

  INFO=`node ${HELPER_JS_FILE}`

  echo "$INFO" | jq
  POSTGRES_CONTAINER_NAME=`echo ${INFO} | jq '.connection.database' | tr -d '"'`
  POSTGRES_IMAGE="postgres"
  POSTGRES_PASSWORD=`echo ${INFO} | jq '.connection.password' | tr -d '"'`
  POSTGRES_DB=`echo ${INFO} | jq '.connection.database' | tr -d '"'`
  POSTGRES_EXPOSED_PORT=`echo ${INFO} | jq '.connection.port' | tr -d '"'`
}

function container_is_running() {
   [ ! -z `docker ps -q -f name=${1}` ]
}

function container_has_been_cached() {
  [ ! -z `docker ps -aq -f name=${1}` ]
}

function start() {
    container_is_running ${POSTGRES_CONTAINER_NAME} \
    || docker run -d -p "${POSTGRES_EXPOSED_PORT}":5432 --name "${POSTGRES_CONTAINER_NAME}" -e POSTGRES_DB="${POSTGRES_DB}" -e POSTGRES_PASSWORD="${POSTGRES_PASSWORD}" -d "${POSTGRES_IMAGE}" \
    && sleep 5 \
    && knex migrate:latest && knex seed:run
}

function stop() {
    container_is_running ${POSTGRES_CONTAINER_NAME} && docker container stop ${POSTGRES_CONTAINER_NAME} && docker container rm ${POSTGRES_CONTAINER_NAME}
}

function restart() {
    stop
    start
}

case "$1" in
  "dev:start")
    init
    start
    ;;
  "dev:stop")
    init
    stop
    ;;
  "dev:restart")
    init
    restart
    ;;
  "test:start")
    export NODE_ENV=test
    init
    start
    unset NODE_ENV
    ;;
  "test:stop")
    export NODE_ENV=test
    init
    stop
    unset NODE_ENV
    ;;
  "test:restart")
    export NODE_ENV=test
    init
    restart
    unset NODE_ENV
    ;;
  *)
    echo """USAGE: ./$0 
    < 
      dev:start
      dev:stop
      dev:restart
      test:start
      test:stop
      test:restart
    >
    """
    exit 1
    ;;
esac



