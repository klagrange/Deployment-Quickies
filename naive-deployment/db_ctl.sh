#############################################
#
# CONFIGURATION VARIABLES - EDITABLE
# MODIFY WITH CAUTION
#
#############################################
POSTGRES_CONTAINER_NAME="my-postgres-db"
POSTGRES_IMAGE="postgres:9.6-alpine"
POSTGRES_PASSWORD="password"
POSTGRES_DB="Test"

function postgres_is_running() {
   [ ! -z `docker ps -q -f name=${POSTGRES_CONTAINER_NAME}` ]
}

function postgres_is_not_running() {
   [ ! -z `docker ps -q -f name=${POSTGRES_CONTAINER_NAME}` ]
}

function postgres_has_been_cached() {
  [ ! -z `docker ps -aq -f name=${POSTGRES_CONTAINER_NAME}` ]
}

function postgres_start() {
  postgres_is_not_running || postgres_has_been_cached && docker start ${POSTGRES_CONTAINER_NAME}
  postgres_is_not_running || postgres_has_been_cached || docker run --name ${POSTGRES_CONTAINER_NAME} -p 5432:5432 -e POSTGRES_PASSWORD=${POSTGRES_PASSWORD} -e POSTGRES_DB=${POSTGRES_DB} -d ${POSTGRES_IMAGE}
}

function postgres_stop() {
   postgres_is_running && docker stop ${POSTGRES_CONTAINER_NAME}
}

function postgres_restart() {
  postgres_stop && postgres_start
  postgres_is_not_running || postgres_start
}

case "$1" in
  "postgres:start")
    postgres_start
    ;;
  "postgres:stop")
    postgres_stop
    ;;
  "postgres:restart")
    postgres_restart
    ;;
  *)
    echo "USAGE: ./$0 <postgres:start|postgres:stop|postgres:restart>"
    exit 1
    ;;
esac
