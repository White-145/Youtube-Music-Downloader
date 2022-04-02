# https://stackoverflow.com/questions/24072790/how-to-detect-key-presses

import contextlib as _contextlib
import threading as _threading

try:
	import msvcrt as _msvcrt

	_ESCAPE_SEQUENCES = tuple([frozenset(('\x00', '\xe0'))])
	_next_input = _msvcrt.getwch
	_set_terminal_raw = _contextlib.nullcontext
	_input_ready = _msvcrt.kbhit

except ImportError:  # Unix
	import sys as _sys
	import tty as _tty
	import termios as _termios
	import select as _select
	import functools as _functools

	_ESCAPE_SEQUENCES = tuple([
		frozenset(('\x1b',)),
		frozenset(('\x1b\x5b', '\x1b\x4f'))
	])

	@_contextlib.contextmanager
	def _set_terminal_raw():
		fd = _sys.stdin.fileno()
		old_settings = _termios.tcgetattr(fd)

		try:
			_tty.setraw(_sys.stdin.fileno())
			yield

		finally:
			_termios.tcsetattr(fd, _termios.TCSADRAIN, old_settings)

	_next_input = _functools.partial(_sys.stdin.read, 1)

	def _input_ready():
		return _select.select([_sys.stdin], [], [], 0) == ([_sys.stdin], [], [])

_MAX_ESCAPE_SEQUENCE_LENGTH = len(_ESCAPE_SEQUENCES)

def _get_keystroke():
	key = _next_input()
	while (len(key) <= _MAX_ESCAPE_SEQUENCE_LENGTH and
		key in _ESCAPE_SEQUENCES[len(key) - 1]
	):
		key += _next_input()

	return key

def _flush():
	while _input_ready():
		_next_input()

# The Key class is a class that represents a key on keyboard.
class Key:
	def __init__(self, *values):
		if len(values) == 0:
			self._value = ['\x00']

		else:
			self._value = []
			for value in values:
				if isinstance(value, Key):
					self._value.extend(value._value)
				else:
					if value is None:
						self._value.append('\x00')
					else:
						self._value.append(value)

	def __str__(self):
		for special in Key.SPECIAL:
			if self in special:
				return Key.SPECIAL[special]

		return ', '.join(self._value)

	def __repr__(self):
		values = []
		for value in self._value:
			values.append('\\x' + '\\x'.join(map("{:02x}".format, map(ord, value))))

		return ', '.join(values)

	def __eq__(self, other):
		if isinstance(other, Key):
			for i in self._value:
				if i not in other._value:
					return False
			return True

		if isinstance(other, str):
			return other in self._value

		return False

	def __ne__(self, other):
		if isinstance(other, Key):
			for i in self._value:
				if i in other._value:
					return False
			return True

		if isinstance(other, str):
			return self._value != other

		return True

	def __hash__(self):
		return hash(' '.join(self._value))

	def __contains__(self, other):
		for value in other._value:
			if value not in self._value:
				return False

		return True

Key.NONE         = Key('\x00')
Key.BELL         = Key('\x07')
Key.BACKSPACE    = Key('\x08')
Key.TAB          = Key('\x09')
Key.NEWLINE      = Key('\x0a')
Key.VERTICAL_TAB = Key('\x0b')
Key.FORM_FEED    = Key('\x0c')
Key.ENTER        = Key('\x0d')
Key.SHIFT        = Key('\x0f')
Key.CTRL         = Key('\x10')
Key.ALT          = Key('\x11')
Key.PAUSE_BREAK  = Key('\x12')
Key.CAPS_LOCK    = Key('\x13')
Key.ESC          = Key('\x1b')
Key.F1           = Key('\x00\x3b', '\xe0\x3b')
Key.F2           = Key('\x00\x3c', '\xe0\x3c')
Key.F3           = Key('\x00\x3d', '\xe0\x3d')
Key.F4           = Key('\x00\x3e', '\xe0\x3e')
Key.F5           = Key('\x00\x3f', '\xe0\x3f')
Key.F6           = Key('\x00\x40', '\xe0\x40')
Key.F7           = Key('\x00\x41', '\xe0\x41')
Key.F8           = Key('\x00\x42', '\xe0\x42')
Key.F9           = Key('\x00\x43', '\xe0\x43')
Key.F10          = Key('\x00\x44', '\xe0\x44')
Key.HOME         = Key('\x00\x47', '\xe0\x47')
Key.UP           = Key('\x00\x48', '\xe0\x48')
Key.PAGE_UP      = Key('\x00\x49', '\xe0\x49')
Key.LEFT         = Key('\x00\x4b', '\xe0\x4b')
Key.RIGHT        = Key('\x00\x4d', '\xe0\x4d')
Key.END          = Key('\x00\x4f', '\xe0\x4f')
Key.DOWN         = Key('\x00\x50', '\xe0\x50')
Key.PAGE_DOWN    = Key('\x00\x51', '\xe0\x51')
Key.INS          = Key('\x00\x52', '\xe0\x52')
Key.DEL          = Key('\x00\x53', '\xe0\x53')
Key.F11          = Key('\x00\x85', '\xe0\x85')
Key.F12          = Key('\x00\x86', '\xe0\x86')

Key.SPECIAL = {
	Key.NONE:         '<none>',
	Key.BELL:         '<bell>',
	Key.BACKSPACE:    '<backspace>',
	Key.NEWLINE:      '<newline>',
	Key.VERTICAL_TAB: '<verticaltab>',
	Key.FORM_FEED:    '<formfeed>',
	Key.TAB:          '<tab>',
	Key.ENTER:        '<enter>',
	Key.SHIFT:        '<shift>',
	Key.CTRL:         '<ctrl>',
	Key.ALT:          '<alt>',
	Key.PAUSE_BREAK:  '<pausebreak>',
	Key.CAPS_LOCK:    '<capslock>',
	Key.ESC:          '<esc>',
	Key.F1:           '<f1>',
	Key.F2:           '<f2>',
	Key.F3:           '<f3>',
	Key.F4:           '<f4>',
	Key.F5:           '<f5>',
	Key.F6:           '<f6>',
	Key.F7:           '<f7>',
	Key.F8:           '<f8>',
	Key.F9:           '<f9>',
	Key.F10:          '<f10>',
	Key.HOME:         '<home>',
	Key.UP:           '<up>',
	Key.PAGE_UP:      '<pageup>',
	Key.LEFT:         '<left>',
	Key.RIGHT:        '<right>',
	Key.END:          '<end>',
	Key.DOWN:         '<down>',
	Key.PAGE_DOWN:    '<pagedown>',
	Key.INS:          '<insert>',
	Key.DEL:          '<delele>',
	Key.F11:          '<f11>',
	Key.F12:          '<f12>'
}

def is_pressed(key: str=None, flush: bool=True) -> bool:
	"""
	Returns if any (or specified) key is pressed

	Arguments:
		str: key - specify key needed to be pressed
		bool: flush - if True flushes keys buffer after key found

	Returns:
		bool: is any (or specified) key is pressed
	"""

	with _set_terminal_raw():
		if key is None:
			if not _input_ready():
				return False

			if flush: _flush()
			return True

		while _input_ready():
			keystroke = _get_keystroke()

			if keystroke == key:
				if flush: _flush()
				return True

		return False

def wait_key(key: str | Key=None, pre_flush: bool=False, post_flush: bool=True) -> Key:
	"""
	Returns when any (or specified) key is pressed

	Arguments:
		str | Key: key - specify key needed to be pressed
		bool: pre_flush - if True flushes keys buffer before check
		bool: post_flush - if True flushes keys buffer after check

	Returns:
		Key: (specified) key pressed
	"""

	with _set_terminal_raw():
		if pre_flush:
			_flush()

		if key is None:
			got_key = _get_keystroke()

			if post_flush: _flush()
			return Key(got_key)

		while (got_key := Key(_get_keystroke())) != key:
			pass
		
		if post_flush: _flush()
		return got_key

def get_key(flush: bool=True):
	"""
	Returns key what is pressed now

	Arguments:
		bool: flush - if True flushes keys buffer after check

	Returns:
		Key: key that is pressed (or None)
	"""

	with _set_terminal_raw():
		if not _input_ready():
			return Key(None)

		key = _get_keystroke()
		if flush: _flush()
		return Key(key)

def listen(func):
	"""
	Run given function every time key pressed
	with this key until False is returned
	
	Arguments:
		function: func - function to use
	"""
	def wrapper():
		while func(wait_key()) is not False:
			pass
	
	thr = _threading.Thread(target=wrapper)
	thr.start()
	return thr

if __name__ == '__main__':
	print("esc to exit")

	def func(key):
		if key == Key.ESC:
			return False

		print(key, repr(key))

	listen(func)
