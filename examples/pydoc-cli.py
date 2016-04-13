from io import BytesIO
from docker import Client

cli = Client(base_url='unix://var/run/docker.sock')

for line in cli.build(fileobj=open('Dockerfile'),
                      rm=True, tag='wware/example'):
    print line
