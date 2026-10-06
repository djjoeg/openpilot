#!/usr/bin/env bash
# Car setup for the Honda Accord with the add-on steering motor. Run on the comma device over SSH:
#   /data/openpilot/accord_setup.sh car     part 1, parked: checks the car's data and the motor (about 10 minutes)
#   /data/openpilot/accord_setup.sh drive   part 2, after driving 5 minutes: checks the speed reading
set -e
cd "$(dirname "$0")"
export PYTHONPATH="$PWD"
case "$1" in
  car)   exec python3 -m openpilot.sunnypilot.tools.hondastepper.setup_car ;;
  drive) exec python3 -m openpilot.sunnypilot.tools.hondastepper.check_drive ;;
  *)     echo "usage: $0 car|drive"; exit 1 ;;
esac
