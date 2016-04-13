#!/bin/bash

DIR=$(cd $(dirname "$0") && pwd)
addr=""

mkdir -p $DIR/shared

# when the rdb package is completely stable, remove this bit
# and switch the pip-install statements in the Dockerfiles
for D in web worker listener; do
    mkdir -p $DIR/$D/rdb
    cp ../setup.py $DIR/$D/rdb
    cp -r ../rdb $DIR/$D/rdb
done

build() {
    docker build -t $1 $DIR/$1 || exit 1
}

getaddr() {
    addr="$(docker inspect --format='{{.NetworkSettings.IPAddress}}' $1)"
}

run() {
    docker run -dP -v $DIR/shared:/shared $*
}

shell() {
    docker run -it -v $DIR/shared:/shared $* /bin/bash
}

docker rm -f $(docker ps -a | cut -c -20 | tail --lines=+2) 2> /dev/null

build listener
build web
build worker
rm -f $DIR/shared/addresses

run -p 127.0.0.1:5000:5000 --name listener listener
getaddr listener
echo listener=$addr > $DIR/shared/addresses

run -p 127.0.0.1:5002:5000 --name worker worker
getaddr worker
echo worker=$addr >> $DIR/shared/addresses

run -p 127.0.0.1:5001:5000 --name web web
getaddr web
echo web=$addr >> shared/addresses

cat $DIR/shared/addresses
