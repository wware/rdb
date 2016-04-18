#!/bin/bash

DIR=$(cd $(dirname "$0") && pwd)
addr=""

# Kill all running docker containers
docker rm -f $(docker ps -a | cut -c -20 | tail --lines=+2) 2> /dev/null

mkdir -p $DIR/shared

getaddr() {
    addr="$(docker inspect --format='{{.NetworkSettings.IPAddress}}' $1)"
}

######################
# First set up the listener

docker build -t listener $DIR/../listener || exit 1
docker run -dP -p 127.0.0.1:5000:5000 --name listener listener
getaddr listener
echo listener=$addr > $DIR/shared/addresses

#####################
# Now set up the other guys

build() {
    docker build -t $1 $DIR/$1 || exit 1
}

run() {
    docker run -dP -v $DIR/shared:/shared $*
}

shell() {
    docker run -it -v $DIR/shared:/shared $* /bin/bash
}

for D in web worker; do
    mkdir -p $DIR/$D/rdb
    cp ../setup.py $DIR/$D/rdb
    cp -r ../rdb $DIR/$D/rdb
done

build web
build worker

run -p 127.0.0.1:5002:5000 --name worker worker
getaddr worker
echo worker=$addr >> $DIR/shared/addresses

run -p 127.0.0.1:5001:5000 --name web web
getaddr web
echo web=$addr >> shared/addresses
