import distutils.spawn
import functools
import os
import platform

from fire.errors import SteamError

system  = platform.system()
windows = (system == 'Windows')
linux   = (system == 'Linux')
osx     = (system == 'Darwin')

if windows:
  import winreg

def _windows_reg_str(path):
  return QueryValue(winreg.HKEY_CURRENT_USER, path)

def _linux_userdata_paths():
  return [
    os.path.join(
      os.path.expanduser('~'),
      '.steam',
      'steam',
      'userdata'
    ),
    os.path.join(
      os.path.expanduser('~'),
      '.local',
      'share',
      'Steam',
      'userdata'
    )
  ]

def _osx_userdata_paths():
  return [
    os.path.join(
       os.path.expanduser("~"),
      "Library",
      "Application Support",
      "Steam",
      "userdata"
    )
  ]

def _windows_userdata_paths():
  return [
    os.path.join(
      _windows_reg_str('Software\Valve\Steam\SteamPath'),
      'userdata'
    )
  ]

_paths = {
  'Linux' : {
    'exe' : lambda: distutils.spawn.find_executable('steam'),
    'userdata' : _linux_userdata_paths
  },

  'Windows' : {
    'exe' : lambda: [_windows_reg_str('Software\Valve\Steam\SteamExe')],
    'userdata' : _windows_userdata_paths
  },

  'Darwin' : {
    'exe' : lambda: ['steam'],
    'userdata' : _osx_userdata_paths
  }
}

def _check_exists(f):
  @functools.wraps(f)
  def _wrapper(*args, **kwargs):
    try:
      ret = f(*args, **kwargs)
      if type(ret) is str:
        ret = [ret]
      for path in ret:
        if os.path.exists(path):
          return path
      raise SteamError('Steam not installed, searched: %s' % str(ret))
    except SteamError:
      raise
    except Exception as e:
      raise SteamError('Cannot obtain Steam handle') from e
  return _wrapper

def _create_dir(f):
  @functools.wraps(f)
  def _wrapper(*args, **kwargs):
    ret = f(*args, **kwargs)
    os.makedirs(ret, exist_ok=True)
    return ret
  return _wrapper

@_check_exists
def get_exe_path():
  return _paths[system]['exe']()

@_check_exists
def get_userdata_path():
  return _paths[system]['userdata']()

@_create_dir
def get_user_path(user):
  return os.path.join(
    user.steam_handle.userdata_path,
    user.user_id
  )

@_create_dir
def get_config_path(user):
  return os.path.join(
    get_user_path(user),
    'config'
  )

@_create_dir
def get_grid_path(user):
  return os.path.join(
    get_config_path(user),
    'grid'
  )

def get_shortcuts_path(user):
  return os.path.join(
    get_config_path(user),
    'shortcuts.vdf'
  )
