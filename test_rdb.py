from rdb import RemotePdb


def tryit():
    RemotePdb(
        smtp_server='smtp.example.com',
        sender='wware@alum.mit.edu',
        recipients=['wware@alum.mit.edu']
    ).set_trace()

    def add(u, v):
        return u + v

    x = 3
    y = 4
    print add(x, y)

if __name__ == '__main__':
    tryit()
