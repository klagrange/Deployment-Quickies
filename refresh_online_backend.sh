#############################################
#
# CONFIGURATION VARIABLES - EDITABLE
# MODIFY WITH CAUTION
#
#############################################
# {{
#   LOCAL
# }}
declare -A IPs=(
  ["test"]="SOME_ACCESSIBLE_URL_OR_IP"
  ["staging"]="SOME_ACCESSIBLE_URL_OR_IP"
)

# {{
#   REMOTE
# }}
WAIT_FOR_IT_FILE="/home/ec2-user/wait-for-it.sh"
declare -A MICROSERVICES_COMPOSE_FILES=(
  ["mol"]="/home/ec2-user/my_project/back/ms-1/docker-compose.yml"
)
EC2_SCRIPT="`dirname ${MICROSERVICES_COMPOSE_FILES[mol]}`/$0"

#############################################
#
# FUNCTIONS - LOCAL
#
#############################################
function ip_is_ssh-able() {
  echo "[INFO] Ensuring that deployment target $1 is ssh-able"

  # add ssh key
  # $SSH_KEY is a bitbucket deployment variable.
  # The key was base64 encoded with -w0 option (for whitespace removal)
  eval `ssh-agent`
  ssh-add <(echo "$SSH_KEY" | base64 -d)
  ssh-add -L

  ssh -o ConnectTimeout=10 "ec2-user@$1" -tt exit || { echo "[FATAL] $1 is not ssh-able"; exit 1; }
}

#############################################
#
# FUNCTIONS - REMOTE
#
#############################################
function sanity_checks_remote() {
  # ensure existence of wait-for-me script
  [ -f "${WAIT_FOR_IT_FILE}" ]  || { echo "[FATAL] ${WAIT_FOR_IT_FILE} does not exist"; exit 1; }
}

function pull_code() {

  for ms in "${!MICROSERVICES_COMPOSE_FILES[@]}"; do
    local compose_file="${MICROSERVICES_COMPOSE_FILES[$ms]}"
    local ms_dir=`dirname ${compose_file}`

    echo "[INFO] Pulling code from ${ms_dir}"

    # pull code
    cd $ms_dir; git pull || { echo "[FATAL] git pull"; exit 1; }


    # ensure that the docker-compose files for each ms exist
    [ -f "${compose_file}" ] || { echo "[FATAL] ${compose_file} does not exist"; exit 1; }
  done
}

function _build_compose_cmd_wo_option() {
  # generate docker-compose command without option
  # example:
  #   docker-compose -f ai/docker-compose.yml -f mol/docker-compose.yml
  local temp=""

  for ms in "${!MICROSERVICES_COMPOSE_FILES[@]}"; do
    compose_file="${MICROSERVICES_COMPOSE_FILES[$ms]}"
    temp="${temp} -f ${compose_file}"
  done

  echo "sudo docker-compose$temp"
}

function echo_aggregated_compose_file() {
  echo "[INFO] Building aggregated compose file"
  local compose_config_cmd="`_build_compose_cmd_wo_option` config"

  cat << USAGE >&2
------------------------------------------------------------------\\
            !!! AGGREGATED COMPOSE FILE.
            !!! PLEASE ENSURE CORRECTNESS.
                            |
                            |
`$compose_config_cmd`"
                            |
                            |
            !!! AGGREGATED COMPOSE FILE.
            !!! PLEASE ENSURE CORRECTNESS.
------------------------------------------------------------------/
USAGE
}

function run_compose() {
  echo "[INFO] Running containerized application"
  local cmd="`_build_compose_cmd_wo_option` up --build --detach"
  $cmd || { echo "[FATAL] error while running $cmd"; exit 1; }
}

function post_sanity_check() {
  echo "[INFO] Performing deployment post sanity checks"
  ${WAIT_FOR_IT_FILE} localhost:80 --timeout=1000 \
    || { echo "[FATAL] You fucking suck :("; exit 1; }
  curl localhost:80
}

#############################################
#
# MAIN
#
#############################################
function main() {
  # {{
  #   $1: "test" or "staging"
  # }}
  ip="${IPs[$1]}"

  # run basic sanity checks
  # sanity_checks_local
  [ ! -z "${ip}" ] || { echo "[FATAL] could not get an IP"; exit 1; }
  ip_is_ssh-able "${ip}"

  # run remote script on deployment target
  # 1) pulls relevant code from github
  # 2) starts deployment containerized app
  # ssh -i ${SSH_KEY} "ec2-user@${ip}" "$EC2_SCRIPT" "remote"
  ssh -tt "ec2-user@${ip}" "$EC2_SCRIPT" "remote"
}

function main_remote() {
  sanity_checks_remote
  pull_code
  echo_aggregated_compose_file
  run_compose
  post_sanity_check
}

case "$1" in
  "test")
    echo "[INFO] Deploying to test environment"
    main "test"
    ;;
  "staging")
    echo "[INFO] Deploying to staging environment"
    main "staging"
    ;;
  "remote")
    main_remote
    ;;
  *)
    echo "USAGE: ./$0 <test|stagging>"
    exit 1
    ;;
esac
