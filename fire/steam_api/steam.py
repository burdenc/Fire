import os
import subprocess

import fire.steam_api.paths as paths
from fire.steam_api.user import SteamUser

from fire.errors import SteamError

class Steam():
  
  def __init__(self, userdata_path, exe_path):
    self.userdata_path = userdata_path
    self.exe_path = exe_path

  def __repr__(self):
    return '<Steam (%r, %r)>' % (self.userdata_path, self.exe_path)

def get_steam_handle(userdata_path='', exe_path=''):
  if not userdata_path:
    userdata_path = paths.get_userdata_path()
  elif not os.path.exists(userdata_path):
    raise SteamError('Userdata path does not exist', userdata_path)

  if not exe_path:
    exe_path = paths.get_exe_path()
  elif not os.path.exists(exe_path):
    raise SteamError('Executable path does not exists', exe_path)

  return Steam(userdata_path, exe_path)

def get_users(steam_handle):
  users = os.listdir(steam_handle.userdata_path)
  if 'anonymous' in users:
    users.remove('anonymous')

  return [SteamUser(steam_handle, u) for u in users]

def open_steam(steam_handle):
  subprocess.Popen(steam_handle.exe_path, stdout=subprocess.DEVNULL)

def exit_steam(steam_handle):
  subprocess.Popen(
    [steam_handle.exe_path, '-shutdown'],
    stdout=subprocess.DEVNULL
  )
