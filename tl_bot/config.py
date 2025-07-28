import configparser
from pathlib import Path
from shutil import copy2
from appdirs import user_config_dir

# --- Constants ---
CONFIG_DIR = Path(user_config_dir('t-bot', 't-bot'))
CONFIG_FILE = CONFIG_DIR / 'config.ini'
DEFAULT_CONFIG = Path(__file__).parent / 'config.ini'

# --- Helper Functions ---
def ensure_config_file() -> Path:
	"""Ensure the config file exists in the user's config directory."""
	CONFIG_DIR.mkdir(parents=True, exist_ok=True)
	if not CONFIG_FILE.exists():
		copy2(DEFAULT_CONFIG, CONFIG_FILE)
	return CONFIG_FILE

def get_config() -> configparser.ConfigParser:
	"""Load and return the config parser object."""
	config = configparser.ConfigParser()
	config.read(CONFIG_FILE)
	return config

def setup(chatid: str = None, token: str = None, server: str = None) -> None:
	"""Setup or update Telegram bot configuration."""
	config = get_config()
	changed = False
	if chatid:
		config.set('Telegram', 'chat_id', chatid)
		changed = True
	if token:
		config.set('Telegram', 'bot_token', token)
		changed = True
	if server:
		config.set('Telegram', 'custom_server', server)
		changed = True
	if changed:
		with open(CONFIG_FILE, 'w') as configfile:
			config.write(configfile)
		print("Config updated.")
		return
	print('If you did not want to change anyone, just press enter.')
	chat_id = input("Enter your channel name or chat id: ")
	if chat_id:
		config.set('Telegram', 'chat_id', chat_id)
	bot_token = input("Enter your telegram bot api token  : ")
	if bot_token:
		config.set('Telegram', 'bot_token', bot_token)
	custom_server = input("Enter your telegram bot private server url  : ")
	if custom_server:
		config.set('Telegram', 'custom_server', custom_server)
	with open(CONFIG_FILE, 'w') as configfile:
		config.write(configfile)
	print("Setup complete!")

def reset()	-> None:
	"""Reset the configuration file to default values."""
	config.set('Telegram', 'chat_id', '@xxxxxxxx')
	config.set('Telegram', 'bot_token', '098765:xxxxxxxxxxxxx')
	config.set('Telegram', 'custom_server', '')

	with open(CONFIG_FILE, 'w') as configfile:
		config.write(configfile)

	print("Config file has been reset to default!")

# --- Config Initialization ---
ensure_config_file()
config = get_config()