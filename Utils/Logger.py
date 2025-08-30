# 📦 Built-in modules
import logging

# 📥 Custom modules
from rich.console import Console as RichConsole
from rich.highlighter import RegexHighlighter
from rich.traceback import install as Install
from rich.logging import RichHandler
from rich.theme import Theme

# ⚙️ Settings
from Config import LogLevel, CommandPrefix


# 💡 Custom highlighter for log messages
class Highlighter(RegexHighlighter):
	base_style = f'{__name__}.'
	highlights = [
		r'(?P<Url>https?://[^\s]+)',
		r'Session ID: (?P<SessionID>[0-9a-z]{32})',
		r'Logged in as (?P<Login>.*?) \((?P<ID>[0-9]{19})\)',
		r'\[(?P<Channel>.*?)\]',
		r'Message from (?P<User>.*?): (?P<SentMessage>.*?)',
		r'Message edited by (?P<User>.*?): "(?P<OriginalMessage>.*?)" -> "(?P<EditedMessage>.*?)"',
		r'Message deleted by (?P<User>.*?): "(?P<DeletedMessage>.*?)"',
		r'Loading extension: (?P<Cog>Cogs\..*)',
		rf'(?P<Command>{CommandPrefix}.*)',
	]


# 🌱 Initialize and define logging
def InitLogging():
	# 🎨 Pastel theme dictionary for log highlighting
	ThemeDict = {
		'log.time': 'bright_black',
		'logging.level.debug': '#B3D7EC',
		'logging.level.info': '#A0D6B4',
		'logging.level.warning': '#F5D7A3',
		'logging.level.error': '#F5A3A3',
		'logging.level.critical': '#ffc6ff',
		f'{__name__}.Url': '#F5D7A3',
		f'{__name__}.SessionID': '#A0D6B4',
		f'{__name__}.Login': '#B3D7EC',
		f'{__name__}.ID': '#A0D6B4',
		f'{__name__}.Channel': '#F5D7A3',
		f'{__name__}.User': '#B3D7EC',
		f'{__name__}.SentMessage': '#B3D7EC',
		f'{__name__}.OriginalMessage': '#F5A3A3',
		f'{__name__}.EditedMessage': '#A0D6B4',
		f'{__name__}.DeletedMessage': '#F5A3A3',
		f'{__name__}.Cog': '#e0bbff',
		f'{__name__}.Command': '#b5ead7',
	}
	Console = RichConsole(
		theme=Theme(ThemeDict),
		force_terminal=True,
		log_path=False,
		highlighter=Highlighter(),
		color_system='truecolor',
	)

	ConsoleHandler = RichHandler(
		markup=False,
		rich_tracebacks=True,
		show_time=True,
		console=Console,
		show_path=False,
		omit_repeated_times=True,
		highlighter=Highlighter(),
		show_level=True,
	)

	ConsoleHandler.setFormatter(logging.Formatter('│ %(message)s', datefmt='[%H:%M:%S]'))

	logging.basicConfig(level=LogLevel, handlers=[ConsoleHandler], force=True)

	Logger = logging.getLogger('rich')
	Logger.handlers.clear()
	Logger.addHandler(ConsoleHandler)
	Logger.propagate = False

	return Console, Logger, ConsoleHandler


Console, Logger, ConsoleHandler = InitLogging()
Install()

# 🧪 Logging test messages
if __name__ == '__main__':
	Logger.debug('This is a debug message.')
	Logger.info('This is an info message.')
	Logger.warning('This is a warning message.')
	Logger.error('This is an error message.')
	Logger.critical('This is a critical message.')
