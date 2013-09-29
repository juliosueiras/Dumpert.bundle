TITLE = 'Dumpert'
BASE_URL = 'http://www.dumpert.nl'
TOP = '%s/toppers' % BASE_URL
THEMES = '%s/themas' % BASE_URL
PAGE = '%s/%d/'

####################################################################################################
def Start():

  Plugin.AddViewGroup('InfoList', viewMode='InfoList', mediaType='items')
  ObjectContainer.title1 = TITLE
  ObjectContainer.view_group = 'InfoList'

  HTTP.CacheTime = CACHE_1HOUR
  HTTP.Headers['User-Agent'] = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.8; rv:23.0) Gecko/20100101 Firefox/23.0'

####################################################################################################
@handler('/video/dumpert', TITLE)
def MainMenu():

  oc = ObjectContainer()

  oc.add(DirectoryObject(key=Callback(Videos, title='Filmpjes', url=BASE_URL), title='Filmpjes'))
  oc.add(DirectoryObject(key=Callback(Videos, title='Toppers', url=TOP), title='Toppers'))
  oc.add(DirectoryObject(key=Callback(Themes, title='Thema\'s'), title='Thema\'s'))

  return oc

####################################################################################################
@route('/video/dumpert/videos', page=int)
def Videos(title, url, page=1):

  oc = ObjectContainer(title2=title)
  html = HTML.ElementFromURL(PAGE % (url, page), headers={'Cookie':'filter=video'})

  for video in html.xpath('//section[@id="content"]/a[@class="dumpthumb"]/span[@class="video"]/..'):
    vid_url = video.get('href')
    vid_title = video.xpath('.//h1')[0].text
    summary = video.xpath('.//p[@class="description"]')[0].text
    date = video.xpath('.//date')[0].text
    date = Datetime.ParseDate(date).date()
    thumb = video.xpath('./img')[0].get('src')

    oc.add(VideoClipObject(
      url = vid_url,
      title = vid_title,
      summary = summary,
      originally_available_at = date,
      thumb = Resource.ContentsOfURLWithFallback(thumb)
    ))

  if len(oc) < 1:
    return ObjectContainer(header="Geen video's", message="Deze directory bevat geen video's")

  else:
    if len(html.xpath('//li[@class="volgende"]')) > 0:
      oc.add(NextPageObject(
        key = Callback(Videos, title='Filmpjes', url=url, page=page+1),
        title = 'Meer ...'
      ))

    return oc

####################################################################################################
@route('/video/dumpert/themes')
def Themes(title):

  oc = ObjectContainer(title2=title)
  html = HTML.ElementFromURL(THEMES)

  for theme in html.xpath('//section[@id="content"]/a[contains(@class, "themalink")]'):
    title = theme.xpath('.//h1')[0].text
    url = theme.get('href').rstrip('/')
    thumb = theme.xpath('./img')[0].get('src').replace('_kl.jpg', '_gr.jpg')

    oc.add(DirectoryObject(
      key = Callback(Videos, title=title, url=BASE_URL + url),
      title = title,
      thumb = Resource.ContentsOfURLWithFallback(thumb)
    ))

  oc.objects.sort(key = lambda obj: obj.title)
  return oc
