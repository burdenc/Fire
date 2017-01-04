import collections
import os

from fire.errors import ShortcutsError

class UTF8():
  @staticmethod
  def encode(f, data):
    return data.encode('UTF8')

  @staticmethod
  def decode(f):
    data = _read_value(f)
    return data.decode('UTF8')

class BitBool():
  @staticmethod
  def encode(f, data):
    return b'\x01' if data else b'\x00'

  @staticmethod
  def decode(f):
    data = f.read(1)
    # Null terminator
    f.read(len(_NUL))
    return data == b'\x01'

_SHORTCUTS_HEADER = b'\x00shortcuts\x00'

_SHORTCUTS_FORMAT = {
  'appname' : {
    'version' : 1,
    'default' : '',
    'encoder' : UTF8
  },
  'exe' : {
    'version' : 1,
    'default' : '',
    'encoder' : UTF8
  },
  'StartDir' : {
    'version' : 1,
    'default' : '',
    'encoder' : UTF8
  },
  'icon' : {
    'version' : 1,
    'default' : '',
    'encoder' : UTF8
  },
  'ShortcutPath' : {
    'version' : 1,
    'default' : '',
    'encoder' : UTF8
  },
  'IsHidden' : {
    'version' : 2,
    'default' : False,
    'encoder' : BitBool
  },
  'AllowDesktopConfig' : {
    'version' : 2,
    'default' : True,
    'encoder' : BitBool
  },
  'OpenVR' : {
    'version' : 2,
    'default' : False,
    'encoder' : BitBool
  }
}

_NUL = b'\x00'
_STARTV1 = b'\x01'
_STARTV2 = b'\x02'
_STARTTAGS = b'\x00tags\x00'
_ENDV2 = b'\x00\x00'
_ENDLIST = b'\x08\x08'
_VALID_VERSIONS = [_STARTV1, _STARTV2]

class Shortcut():
  
  def __init__(self, data, unsupported):
    self.data = data
    self.unsupported = unsupported
    return
    
    try:
      self.tags = data.pop('tags')
      for key, fmt in _SHORTCUTS_FORMAT.items():
        val = data.pop(key, fmt['default'])
        setattr(self, key, val)
    except Exception as e:
      raise ShortcutsError('Invalid shortcut format') from e

    # Unsupported fields go here, they will be copied exactly back byte by byte
    # when writing back. This won't handle key-value pairs of newer versions...
    self._unsupported = unsupported

  def __repr__(self):
    return '<Shortcut %r>' % self.data['appname']

def _peek(f, size=1):
  return f.peek()[0:size]

def _read_value(f, term=_NUL):
  contents = bytes()
  while _peek(f, 1) != term:
    b = f.read(1)
    contents += b
  f.read(1)
  return contents

def parse_shortcuts_file(shortcuts_file):
  if not os.path.exists(shortcuts_file):
    return []

  with open(shortcuts_file, 'rb') as f:
    if f.read(len(_SHORTCUTS_HEADER)) != _SHORTCUTS_HEADER:
      raise ShortcutsError('Invalid shortcuts file %s' % shortcuts_file)
    
    try:
     return _parse_list(f, _parse_shortcut_entry)
    except Exception as e:
      raise ShortcutsError('Could not parse shortcuts file.') from e

def _parse_list(f, handler):
  contents = []
  while _peek(f, len(_ENDLIST)) != _ENDLIST:
    data = handler(f)
    contents.append(data)

  # Remove _ENDLIST from buffer
  f.read(len(_ENDLIST))
 
  return contents

def _parse_shortcut_entry(f):
  entry = collections.OrderedDict({})

  # Don't care about list index, throw it away
  f.read(len(_NUL))
  _read_value(f)
  
  while _peek(f, len(_NUL)) != _NUL:
    version = f.read(1)
    if version == _STARTV1:
      key, val = _parse_key_pair_v1(f)
    elif version == _STARTV2:
      key, val = _parse_key_pair_v2(f)
    else:
      # TODO: unsupported version
      pass

    entry[key] = val

  # Parse tags for shortcut
  if f.read(len(_STARTTAGS)) != _STARTTAGS:
    raise ShortcutsError('Expected tags list for shortcut.')
  entry['tags'] = _parse_list(f, _parse_tag_entry)

  return Shortcut(entry, {})

def _parse_key_pair_v1(f):
  # TODO: unsupported key
  key = _read_value(f).decode('UTF8')
  value = _SHORTCUTS_FORMAT[key]['encoder'].decode(f)

  return key, value

def _parse_key_pair_v2(f):
  # TODO: unsupported key
  key = _read_value(f).decode('UTF8')
  value = _SHORTCUTS_FORMAT[key]['encoder'].decode(f)

  # Version 2 keys have 2 extra null terminators
  if f.read(len(_ENDV2)) != _ENDV2:
    raise ShortcutsError('Invalid v2 key terminator: %s' % key)

  return key, value
  

def _parse_tag_entry(f):
  # Don't care about list index, throw it away
  f.read(len('\x01')) # tag entries start with 1 for some reason? Valve pls
  _read_value(f)

  return UTF8.decode(f)

