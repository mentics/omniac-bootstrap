#!/bin/bash
arg=$1
echo "args: $# first=$1 arg=$arg test=$testing"

# Check if docker is installed
echo "Looking for docker"
which docker >/dev/null 2>/dev/null
if [ $? -eq 0 ]; then
  echo "  found docker in path"
else
  curl -o ${TMP}/docker-install.exe https://download.docker.com/win/stable/Docker%20for%20Windows%20Installer.exe
  /tmp/docker-install.exe
fi

echo "Checking for omniac-admin image"
if [[ "$arg" == "r" ]]; then
  echo "    deleting omniac-admin image"
  docker rmi "omniac-admin"
fi
#docker images | grep "omniac-admin" >/dev/null 2>/dev/null
if [[ -z `docker images | grep "omniac-admin"` || "$arg" == "r" ]]; then
  echo "Building docker image omniac-admin"
  docker build -t "omniac-admin" .
else
  echo "  found docker image omniac-admin"
fi

docker run --rm --name "admin" omniac-admin





: <<'END'
echo "Checking for ubuntu docker image"
docker images | grep "ubuntu" >/dev/null 2>/dev/null
if [ $? -eq 0 ]; then
  echo "  found docker image ubuntu"
else
  docker pull ubuntu:latest
fi


echo "Checking for python:3 docker image"
docker images | grep "python" >/dev/null 2>/dev/null
if [ $? -eq 0 ]; then
  echo "  found docker image python"
else
  docker pull python:3
fi

#docker run -i --rm --name "RunPythonScript" -v '/$(pwd)':'//home/run' -w //home/run -a python:3 python run.py
#docker run -i --rm --name "Run Python Script" --mount type=bind,source="$(pwd)",destination=/home/run,consistency=cached -w /c/home/run python:3 python run.py
END

read
