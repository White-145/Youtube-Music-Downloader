import os

os.system('color')

### Colors

END      = '\33[0m'

BOLD       = '\33[1m'
ITALIC     = '\33[3m'
UNDERLINED = '\33[4m'
BLINK      = '\33[5m'
BLINK_2    = '\33[6m'
INVERTED   = '\33[7m'

###

BLACK       = '\33[30m'
RED         = '\33[31m'
GREEN       = '\33[32m'
YELLOW      = '\33[33m'
BLUE        = '\33[34m'
VIOLET      = '\33[35m'
BEIGE       = '\33[36m'
WHITE       = '\33[37m'

GREY        = '\33[90m'
RED_2       = '\33[91m'
GREEN_2     = '\33[92m'
YELLOW_2    = '\33[93m'
BLUE_2      = '\33[94m'
VIOLET_2    = '\33[95m'
BEIGE_2     = '\33[96m'
WHITE_2     = '\33[97m'

###

BG_BLACK      = '\33[40m'
BG_RED        = '\33[41m'
BG_GREEN      = '\33[42m'
BG_YELLOW     = '\33[43m'
BG_BLUE       = '\33[44m'
BG_VIOLET     = '\33[45m'
BG_BEIGE      = '\33[46m'
BG_WHITE      = '\33[47m'

BG_GREY       = '\33[100m'
BG_RED_2      = '\33[101m'
BG_GREEN_2    = '\33[102m'
BG_YELLOW_2   = '\33[103m'
BG_BLUE_2     = '\33[104m'
BG_VIOLET_2   = '\33[105m'
BG_BEIGE_2    = '\33[106m'
BG_WHITE_2    = '\33[107m'

ATTRS     = (BOLD, ITALIC, UNDERLINED, BLINK, BLINK_2, INVERTED)
COLORS    = (BLACK, RED, GREEN, YELLOW, BLUE, VIOLET, BEIGE, WHITE, GREY,
	RED_2, GREEN_2, YELLOW_2, BLUE_2, VIOLET_2, BEIGE_2, WHITE_2)
BG_COLORS = (BG_BLACK, BG_RED, BG_GREEN, BG_YELLOW, BG_BLUE, BG_VIOLET,
	BG_BEIGE, BG_WHITE, BG_GREY, BG_RED_2, BG_GREEN_2, BG_YELLOW_2,
	BG_BLUE_2, BG_VIOLET_2, BG_BEIGE_2, BG_WHITE_2)

def colors_to_bg(color):
	if color in BG_COLORS:
		return color

	table = {
		BLACK: BG_BLACK,
		RED: BG_RED,
		GREEN: BG_GREEN,
		YELLOW: BG_YELLOW,
		BLUE: BG_BLUE,
		VIOLET: BG_VIOLET,
		BEIGE: BG_BEIGE,
		WHITE: BG_WHITE,
		GREY: BG_GREY,
		RED_2: BG_RED_2,
		GREEN_2: BG_GREEN_2,
		YELLOW_2: BG_YELLOW_2,
		BLUE_2: BG_BLUE_2,
		VIOLET_2: BG_VIOLET_2,
		BEIGE_2: BG_BEIGE_2,
		WHITE_2: BG_WHITE_2
	}

	if color in table:
		return table[color]

	return color

def print_format_table():
    """
    prints table of formatted text format options
    """
    for style in range(8):
        for fg in range(30,38):
            s1 = ''
            for bg in range(40,48):
                format = ';'.join([str(style), str(fg), str(bg)])
                s1 += '\x1b[%sm %s \x1b[0m' % (format, format)
            print(s1)
        print('\n')

def colored(text, color=None, bg_color=None, attr=None):
	result = ''
	if color and color in COLORS:
		if color not in COLORS:
			raise ValueError("given color is not color")
		result += color

	if bg_color:
		bg_color = colors_to_bg(bg_color)

		if bg_color not in BG_COLORS:
			raise ValueError("given bg color is not bg color")
		result += bg_color

	if attr:
		if type(attr) == str:
			attr = [attr]

		for i in attr:
			if i not in ATTRS:
				raise ValueError("one of given attrs is not attr")
			result += i

	result += text + END

	return result

class Color:

	def __init__(self, color=None, bg_color=None, attr=None):
		if color and color in COLORS:
			if color not in COLORS:
				raise ValueError("given color is not color")

		if bg_color:
			bg_color = colors_to_bg(bg_color)

			if bg_color not in BG_COLORS:
				raise ValueError("given bg color is not bg color")

		if attr:
			if type(attr) == str:
				attr = [attr]

			for i in attr:
				if i not in ATTRS:
					raise ValueError("one of given attrs is not attr")

		self.color = color
		self.bg_color = bg_color
		self.attr = attr

	def text(self, text):
		result = ''
		if self.color: result += self.color
		if self.bg_color:
			bg_color = colors_to_bg(self.bg_color)
			result += bg_color
		if self.attr:
			for i in self.attr:
				result += i

		result += text + END

		return result

	def __str__(self):
		result = ''
		if self.color: result += self.color
		if self.bg_color: result += self.bg_color
		if self.attr:
			for i in self.attr:
				result += i

		result += " TEXT " + END

		return result
