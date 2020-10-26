import hassbrainapi.settings as sett


def correct_url(url):

    # check that urls begin with http if they don't
    if url[:4] != "http":
        if url[:6] != "http://":
            url = "http://" + url
            pass
        pass

    # remove trailing / if there is any
    if url[-1:] == "/":
        url = url[:-1]

    # check if url matches the following pattern if not raise an error
    # with regex
    # todo

    return url

def create_device_url(server_address, id):
    url = server_address
    url += sett.URL_DEVICE + str(id) + "/"
    return correct_url(url)

def rt_node_id2rt_node_url(server_address, ide):
    url = server_address
    url += sett.URL_RT_NODE + str(ide) + "/"
    return correct_url(url)
