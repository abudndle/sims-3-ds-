#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
cc -std=c99 -Wall -Wextra -Werror -pedantic src/camera.c src/control_ui.c src/gameplay_nav.c tests/test_gameplay_nav.c -o /tmp/sims3_nav_test
/tmp/sims3_nav_test
