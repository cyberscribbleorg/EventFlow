#!/bin/bash

SCRIPT_DIR=$(dirname "$0")

FOLDERS_TO_CLEAN=(
    "$SCRIPT_DIR/data"
)

confirm() {
    while true; do
        read -p "$1 [y/n]: " yn
        case $yn in
            [Yy]* ) return 0;;
            [Nn]* ) return 1;;
            * ) echo "Please answer yes or no.";;
        esac
    done
}

clean_docker() {
    CONTAINERS=$(docker ps -aq)
    if [ -z "$CONTAINERS" ]; then
        echo "No Docker containers to stop or remove."
    else
        echo "Stopping all Docker containers..."
        docker stop $CONTAINERS

        echo "Removing all Docker containers..."
        docker rm $CONTAINERS
    fi
}

clean_folders() {
    EMPTY=true
    for folder in "${FOLDERS_TO_CLEAN[@]}"; do
        if [ -d "$folder" ] && [ "$(ls -A $folder)" ]; then
            EMPTY=false
            echo "Cleaning folder: $folder"
            rm -rf "$folder"/*
        else
            echo "Folder not found or already empty: $folder"
        fi
    done

    if $EMPTY; then
        echo "No folders to clean."
    fi
}

if confirm "Zen mind begineers mind! Are you sure ?"; then
    clean_docker
    clean_folders
    echo "Cleanup completed successfully."
else
    echo "Operation canceled."
fi