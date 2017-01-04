import fire.steam_api.paths as paths

class SteamUser():

  def __init__(self, steam_handle, user_id):
    self.steam_handle = steam_handle
    self.user_id = user_id

  def __repr__(self):
    return '<SteamUser (%r, %r)>' % (self.steam_handle, self.user_id)
