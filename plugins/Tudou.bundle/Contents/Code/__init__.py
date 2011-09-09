import urllib

####################################################################################################
ICON  = 'icon_default.png'
####################################################################################################

@handler('/video/tudou', 'Tudou')
def Main():
  oc = ObjectContainer(
      objects = [
          DirectoryObject(
              key = Callback(GetAlbums, albumtop='c22t-1a-1y-1h-1s1p1'),
              title = 'Movies'
              ),
          DirectoryObject(
              key = Callback(GetAlbums, albumtop='c22t-1a7y-1h-1s1p1'),
              title = 'American Movies'),
          DirectoryObject(
              key = Callback(GetAlbums, albumtop='c30t-1a-1y-1h-1s1p1'),
              title = 'TV Shows'),
          DirectoryObject(
              key = Callback(GetAlbums, albumtop='c30t-1a7y-1h-1s0p1'),
              title = 'American TV Shows'),
          DirectoryObject(
              key = Callback(GetAlbumVideos, url='http://www.tudou.com/playlist/id/10737591'),
              title = 'P90X'),
          DirectoryObject(
              key = Callback(GetAlbumVideos, url='http://www.tudou.com/playlist/id/2597000'),
              title = 'Intro Yoga (28 Classes)'),
          ]
      )
  return oc

def GetMovieRegions():
    movie_page = HTML.ElementFromURL(url='http://movie.tudou.com', encoding='gbk')
    country_dl = movie_page.cssselect('div.catelist dl')[1]

    countries = [MovieObject(url='xx', title='xx')]
    links = country_dl.cssselect('dd a')
    for link in links:
        countries.append(MovieObject(url = link.attrib.get('href'),
                                     title = link.attrib.get('title')))
    return ObjectContainer(objects = countries)


def GetAlbumCategories(albumtop):
    pass

def GetAlbumSubcategories(albumtop, category):
    pass

def GetAlbums(albumtop):
    url = 'http://www.tudou.com/albumtop/' + albumtop + '.html'
    page = HTML.ElementFromURL(url=url, encoding='gbk')

    try:
      num_pages = int(page.cssselect('#pagingBars li a')[-1].text)
    except:
      num_pages = 1

    albums = []
    for page_num in range(1, num_pages+1):
        albums.extend(GetAlbumsOnPage(albumtop, page_num))

    return ObjectContainer(objects = albums)

def GetAlbumsOnPage(albumtop, page_num):
    albums = []
    # The last character in an albumtop is usually 'pX' where X is the page number
    albumtop = albumtop[:-1] + str(page_num)
    url = 'http://www.tudou.com/albumtop/' + albumtop + '.html'
    page = HTML.ElementFromURL(url=url, encoding='gbk')
    album_divs = page.cssselect('div.pack.pack_album')
    for div in album_divs:
        albums.append(DirectoryObject(
            key = Callback(GetAlbumVideos, url=div.cssselect('h6.caption a')[0].attrib.get('href')),
            title = div.cssselect('h6.caption a')[0].attrib.get('title'),
            tagline = div.cssselect('ul.info li.desc')[0].text,
            summary = div.cssselect('p.ext_intro')[0].text,
            thumb = div.cssselect('div.pic img')[0].attrib.get('src')
            )
        )
    return albums

def GetAlbumVideos(url):
    # This function breaks with Desperate Housewives.  TODO: Figure out why
    # Example URL: http://www.tudou.com/playlist/album/id65725.html

    videos = []
    try:
        page = HTML.ElementFromURL(url=url, encoding='gbk')
    except:
        return ObjectContainer(objects = [MovieObject(url='x',title='Downloading page broke',summary=url)])

    #album_title = page.cssselect('h2 a.album-title')[0].text
    video_divs = page.cssselect('div.pack_video_card')
    for div in video_divs:
        try:
            url = div.cssselect('.caption a')[0].attrib.get('href')
            url = GetPlayableVideoUrl(url)
        except:
            # With no URL, we can't create a video link
            continue

        try:
            title = div.cssselect('.caption a')[0].attrib.get('title')
            if url is None:
                title = title + ' (No URL Found; Unplayable)'
        except:
            title = 'NO TITLE FOUND'

        try:
            thumb = div.cssselect('div.pic img')[0].attrib.get('src')
        except:
            thumb = None

        try:
            summary = div.cssselect('span.vinf')[0].text
            duration = ms_from_time_string(summary)
        except:
            duration = 0
            summary = None

        movie_meta_data = MovieObject(
            url = url,
            title = title,
            #show = album_title,  # This only works with Episode Objects.  Maybe eventually I can figure out if I'm working with TV Shows or movies.
            thumb = thumb,
            duration = duration,

            # I'm just using the length of time as the summary for now; not ideal
            summary = summary
            )
        Log('url = ' + url)
        movie_meta_data.add(MediaObject(
            platforms = [ ClientPlatform.MacOSX ],
            protocols = [ Protocol.RTMP ],
            bitrate = 1000,
            video_codec = VideoCodec.H264,
            audio_channels = 2,
            container = AudioCodec.MP3,
            parts = [
                PartObject(
                   key = url,
                   duration = duration
                ),
            ]))
        videos.append(movie_meta_data)
    return ObjectContainer(objects = videos)

def ms_from_time_string(time_str):
    '''time_str is in the format HH:MM:SS, and this converts it to an int representing milliseconds'''

    time_arr = time_str.split(':')
    try:
        hours = int(time_arr[-3])
    except:
        hours = 0;

    minutes = 60 * hours
    try:
        minutes = minutes + int(time_arr[-2])
    except:
        pass

    seconds = 60 * minutes
    try:
        seconds = second + int(time_arr[-1])
    except:
        pass

    return 1000 * seconds

def GetPlayableVideoUrl(tudou_url):
    page = HTML.ElementFromURL(url='http://www.flvcd.com/parse.php?kw='+urllib.quote(tudou_url), encoding='gbk')
    try:
        real_url = page.cssselect('a.link')[0].attrib.get('href')
    except:
        return None

    try:
        url_parts = real_url.split('/')
        host = str.join('/', url_parts[:3])+'/'
        clip = str.join('/', url_parts[3:])
        return RTMPVideoURL(host, clip=clip)
    except:
        return None

