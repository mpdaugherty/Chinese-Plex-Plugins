@handler('/video/tudou', 'Tudou')
def Main():
  oc = ObjectContainer(
      objects = [
          MovieObject(url = 'http://js.tudouui.com/bin/contentplayer/focus_player_19.swf?iid=99158782',
                      title = 'Test Movie')
          ]
      )
  return oc
