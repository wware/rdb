_host_getter = None
_host_ip = None


def get_host_ip():
    global _host_ip
    if _host_ip is None:
        if _host_getter is None:
            return
        _host_ip = _host_getter()
    return _host_ip
