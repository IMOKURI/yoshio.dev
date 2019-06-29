#!/bin/bash

set -eu

WORK_DIR="/tmp/github_actions/"
RELEASE_DIR="/usr/local/src/web/"

rsync -av --delete --exclude-from="${WORK_DIR}/.releaseignore" "${WORK_DIR}" "${RELEASE_DIR}"

# sudo systemctl restart gunicorn
