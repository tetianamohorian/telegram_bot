#!/bin/bash


# Zostavenie Docker obrazu

docker build -t tetianamohorian/hate-speech-bot:latest .


# Push obrazu
docker push tetianamohorian/hate-speech-bot:latest


