#!/bin/bash

CURRENT_DIR=$(pwd)
PROJECT_DIR=${1:-"$CURRENT_DIR"}

# Start a new tmux session
tmux new-session -d -s cartblanche

# Split the window into three panes
tmux split-window -h
tmux split-window -v

# Send commands to each pane
tmux send-keys -t 0 "conda activate cartblanche22 && cd $PROJECT_DIR && npm start" C-m
tmux send-keys -t 1 "conda activate cartblanche22 && cd $PROJECT_DIR/backend && celery -A cartblanche.run_celery.celery worker -l INFO -n worker3 --concurrency=5" C-m
tmux send-keys -t 2 "conda activate cartblanche22 && cd $PROJECT_DIR/backend && gunicorn -b :5000 -w 3 --log-level=DEBUG --access-logfile - --error-logfile - application --timeout 36000 --reload" C-m

# Attach to the tmux session
tmux attach-session -t cartblanche


#To switch between the two tmux terminals: control-B + arrow keys
#To kill the tmux session: tmux kill-server
#To check processeses that are running: lsof -i :<Port Number>
#To kill a process: kill -9 <PID>
#To kill all processes: pkill -f <process_name> 