import urllib.request


def get_html_page(quest):
    url = "https://www.youtube.com/results?search_query=" + quest
    page = urllib.request.urlopen(url)
    data = str(page.read().decode("utf8"))
    return data


def get_names_search(data):
    video_search = data.split('"title":{"runs":[{"text":"')
    code_search = data.split('{"url":"/watch?v=')
    code_results = []
    name_results = []

    for n in range(1, 6):
        code_results.append(code_search[n].split('","webPageType"')[0])
        name_results.append(video_search[n].split('"}],"accessibility"')[0])

    results = [code_results, name_results]
    return results


def get_url_watch(video_id):
    donn = 'https://www.youtube.com/watch?v=' + video_id
    return donn


def info_results(data):
    video = []
    video_search = data.split('"title":{"runs":[{"text":"')
    for n in range(1, 6):
        tsb = data.split('{"text":{"accessibility":{"accessibilityData":{"label":"')
        tsm = tsb[n].split(',"simpleText":"')
        tsa = tsm[1].split('"},')
        video.append(f"""**{n}**: {video_search[n].split('"}],"accessibility"')[0]}  ({tsa[0]})""")
    return video