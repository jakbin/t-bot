import sys
import os
import urllib3
import requests
import configparser
from tqdm import tqdm
from pathlib import Path
from shutil import copy2
import requests_toolbelt
from requests.exceptions import JSONDecodeError
from requests.exceptions import MissingSchema
from requests import get, ConnectionError, head

urllib3.disable_warnings()


# --- Constants ---
CONFIG_DIR = Path.home() / '.config' / 't-bot'
CONFIG_FILE = CONFIG_DIR / 'config.ini'
DEFAULT_CONFIG = Path(__file__).parent / 'config.ini'
DOWNLOADS_DIR = Path('downloads')
TELEGRAM_API_URL = 'https://api.telegram.org'

# --- Logging Setup ---
import logging
logging.basicConfig(level=logging.INFO, format='[%(levelname)s] %(message)s')

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

# --- Config Initialization ---
ensure_config_file()
config = get_config()


class ProgressBar(tqdm):
	"""Progress bar for uploads/downloads."""
	def update_to(self, n: int) -> None:
		self.update(n - self.n)


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
		logging.info("Config updated.")
		return
	print('If you did not want to change anyone, just press enter.')
	chat_id = input("Enter your channel name or chat id with '-' : ")
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
	logging.info("Setup complete!")

def reset()	-> None:
	"""Reset the configuration file to default values."""
	config.set('Telegram', 'chat_id', '@xxxxxxxx')
	config.set('Telegram', 'bot_token', '098765:xxxxxxxxxxxxx')
	config.set('Telegram', 'custom_server', '')

	with open(CONFIG_FILE, 'w') as configfile:
		config.write(configfile)

	logging.info("Config file has been reset to default!")

def tg_server_url() -> str:
	custom_server = config['Telegram']['custom_server']
	if custom_server == '':
		return TELEGRAM_API_URL
	else:
		return custom_server

def getme_url(bot_token: str) -> str:
	"""Construct the URL for the getMe API endpoint."""
	custom_server = tg_server_url()
	if custom_server == '':
		return f'{TELEGRAM_API_URL}/bot{bot_token}/getMe'
	else:
		return f'{custom_server}/bot{bot_token}/getMe'

def verify_token(bot_token: str) -> tuple:
	"""Verify the bot token by calling the getMe API endpoint."""
	r = requests.get(getme_url(bot_token))
	try:
		verify_data = r.json()
	except JSONDecodeError:
		sys.exit(r.text)
	if verify_data['ok'] == True:
		return True, verify_data["result"]["username"]
	elif verify_data['ok'] == False:
		return False, None

def test_token(bot_token: str) -> None:
	"""Test the bot token by verifying it and printing the bot's username."""
	is_token_correct, bot_name = verify_token(bot_token)
	if is_token_correct:
		print(f'Bot Token is correct and Bot username is {bot_name}.')
	else:
		print(f'Bot Token is incorrect.')

def uploader(bot_token: str, chat_id: str, file_name: str, server_url: str = "https://api.telegram.org", caption: str = None) -> tuple:

	data_to_send = []
	session = requests.session()

	with open(file_name, "rb") as fp:
		data_to_send.append(
			("document", (file_name, fp))
		)
		data_to_send.append(('chat_id', (chat_id)))
		data_to_send.append(('caption', (caption)))
		encoder = requests_toolbelt.MultipartEncoder(data_to_send)
		with ProgressBar(
			total=encoder.len,
			unit="B",
			unit_scale=True,
			unit_divisor=1024,
			miniters=1,
			file=sys.stdout,
		) as bar:
			monitor = requests_toolbelt.MultipartEncoderMonitor(
				encoder, lambda monitor: bar.update_to(monitor.bytes_read)
			)

			r = session.post(
				f"{server_url}/bot{bot_token}/sendDocument",
				data=monitor,
				allow_redirects=False,
				headers={"Content-Type": monitor.content_type},
			)

	try:
		resp = r.json()

		if resp['ok'] == True:
			return True, resp
		else:
			return False, resp

	except JSONDecodeError:
		return False, r.text
	

def upload_file(bot_token: str, chat_id: str, file_name: str, caption: str = None) -> None:

	file_size = os.path.getsize(file_name)
	server_url =  tg_server_url(bot_token)
	custom_server = config['Telegram']['custom_server']
	if custom_server == '':
		if file_size > 51200000:
			sys.exit("Bot can upload only 50 MB file.")

	status, resp = uploader(bot_token, chat_id, file_name, server_url, caption)
	
	if status == True:
		print(f'{file_name} uploaded sucessfully on {resp["result"]["sender_chat"]["title"]}')
	else:
		print(f"\n{resp}")
		print("There is something error")

def downloader(url: str, file_name: str) -> bool:
	try:
		filesize = int(head(url).headers["Content-Length"])
	except ConnectionError:
		sys.exit("[Error]: No internet")
	except MissingSchema as e:
		sys.exit(str(e))
	except KeyError:
		filesize = None

	chunk_size = 1024

	try:
		with get(url, stream=True) as r, open(file_name, "wb") as f, tqdm(
				unit="B",  # unit string to be displayed.
				unit_scale=True,  # let tqdm to determine the scale in kilo, mega..etc.
				unit_divisor=1024,  # is used when unit_scale is true
				total=filesize,  # the total iteration.
				file=sys.stdout,  # default goes to stderr, this is the display on console.
				desc=file_name  # prefix to be displayed on progress bar.
		) as progress:
			if r.status_code == 200:
				for chunk in r.iter_content(chunk_size=chunk_size):
					datasize = f.write(chunk)
					progress.update(datasize)
				return True
			else:
				os.remove(file_name)
				return False
	except ConnectionError as e:
		print(str(e))
		return False

def download(url: str, bot_token: str, chat_id: str, caption: str = None) -> None:
	if not os.path.isdir(DOWNLOADS_DIR):
		os.mkdir(DOWNLOADS_DIR)

	filename = os.path.basename(url)

	yes = {'yes','y','ye',''}
	choice = input(f"Do you want change filename {filename[0:60]} [Y/n]: ").lower()
	if choice in yes:
		filename = input("Enter new file name with extension: ")

	file_path = os.path.join(DOWNLOADS_DIR, filename)

	print("Downloading file......")
	try:
		downloader(url, file_path)
	except OSError:
		print("File name is too log !")
		filename = input("Enter new filename : ")
		file_path = os.path.join(DOWNLOADS_DIR, filename)
		downloader(url, file_path)
	
	print("\nUploading file......")
	upload_file(bot_token, chat_id, file_path, caption)

def files()	-> None:
	"""List all files in the 'downloads' directory."""
	try:
		files = os.listdir(DOWNLOADS_DIR)
	except FileNotFoundError:
		sys.exit('Directory "downloads" not found !')
	if files != []:
		print("id -> File Name")
		i = 0
		for file in files:
			i += 1
			print(f"{i} -> {file[0:55]}")

def delete() -> None:
	"""Delete files from the 'downloads' directory."""
	try:
		files = os.listdir(DOWNLOADS_DIR)
	except FileNotFoundError:
		sys.exit('Directory "downloads" not found !')
	if files != []:
		print("\nId ->  File Name")
		i = 0
		for file in files:
			i += 1
			print(f"{i}  ->  {file[0:55]}")

		num_of_files = len(files)
		inputs = list(map(str, input(f"\nSelect file number [1-{num_of_files}] seprated by commasm, or 'all':").split(sep=",")))
		print(inputs)
		if inputs == ['all']:
			print("all")
		try:
			isdigits = all(isinstance(int(x), int) for x in inputs)
		except ValueError:
			sys.exit("Invalid input !")
		if isdigits:
			for x in inputs:
				try:
					print(files[int(x)-1])
					os.remove(f"downloads/{files[int(x)-1]}")
				except IndexError:
					print(f"Id {x} not found")

def get_id(bot_token : str) -> None:
	"""Get chat IDs from the bot's updates."""
	if bot_token == '098765:xxxxxxxxxxxxxxxxx':
		bot_token = input("Enter your telegram bot api token  : ")
		config.set('Telegram', 'bot_token', bot_token)
		with open(CONFIG_FILE, 'w') as configfile:
			config.write(configfile)
	url = f'https://api.telegram.org/bot{bot_token}/getUpdates'
	r = requests.get(url)
	resp = r.json()
	if resp['ok'] == True:
		found = False
		for chat_id in resp['result']:
			if 'my_chat_member' in chat_id:
				print("Chad ID        ->  Chat Name")
				print(str(chat_id['my_chat_member']['chat']['id']) + " -> " + chat_id['my_chat_member']['chat']['title'])
				found = True
			elif 'message' in chat_id:
				print("Chad ID        ->  Chat Name")
				print(str(chat_id['message']['chat']['id']) + " -> " + chat_id['message']['chat']['username'])
				found = True
			else:
				print("No chat id found, Remove your bot from chat and add it again, then run it")
		if not found:
			print("No chat id found, Do some activity with bot, then run it")
	else:
		print(resp)
		print("\nThere is something error")

def send_message(message: str, bot_token: str = config['Telegram']['bot_token'], chat_id: str = config['Telegram']['chat_id']) -> None:
	server_url = tg_server_url()

	url = f"{server_url}/bot{bot_token}/sendMessage"
	data = {
		'chat_id': chat_id,
		'text': message
	}

	try:
		r = requests.post(url, data=data)
		resp = r.json()
		if resp['ok'] == True:
			print("Message sent successfully!")
		else:
			print(resp)
	except JSONDecodeError:
		print("There is something error")