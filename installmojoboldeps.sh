#!/bin/bash
# Install mojobol's system dependencies.
#
# Scope is deliberately narrow (ADR-0012): telephony interaction and data
# capture only. The mail/batch/outbound subsystems are gone, so the MySQL,
# PHP, Apache, mojomailman and livingdata dependencies they pulled in are
# gone with them — as are python-setuptools/easy_install, which no longer
# exist on a current Ubuntu.

set -euo pipefail

sudo apt-get update
sudo apt-get install -y \
    asterisk \
    python3 \
    python3-pip \
    python3-venv \
    git \
    sox \
    espeak

# Python dependencies are pinned in requirements.txt.
pip3 install -r "$(dirname "$0")/requirements.txt"
