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

base_dir = os.path.dirname(os.path.realpath(__file__))
config = os.path.join(base_dir, 'config.ini')

home_path = Path.home()

if not os.path.isdir(os.path.join(home_path, '.config')):
	os.mkdir(os.path.join(home_path, '.config'))

if os.path.isfile(os.path.join(home_path, ".config/t-bot/config.ini")):
	config_file = os.path.join(home_path, ".config/t-bot/config.ini")
else:
	if not os.path.isdir(os.path.join(home_path, '.config/t-bot')):
		os.mkdir(os.path.join(home_path, '.config/t-bot'))
	copy2(config,os.path.join(home_path, ".config/t-bot"))
	config_file = os.path.join(home_path, ".config/t-bot/config.ini")

config = configparser.ConfigParser()
config.read(config_file)

class ProgressBar(tqdm):
	def update_to(self, n: int) -> None:
		self.update(n - self.n)

def setup():
	print('If you did not want to change anyone, just press enter.')
	chat_id = input("Enter your channel name or chat id with '-' : ")
	if chat_id != '':
		config.set('Telegram', 'chat_id', chat_id)

	bot_token = input("Enter your telegram bot api token  : ")
	if bot_token != '':
		config.set('Telegram', 'bot_token', bot_token)

	custom_server = input("Enter your telegram bot private server url  : ")
	if custom_server != '':
		config.set('Telegram', 'custom_server', custom_server)

	with open(config_file, 'w') as configfile:
		config.write(configfile)

	print("Setup complete!")

def reset():
	config.set('Telegram', 'chat_id', '@xxxxxxxx')
	config.set('Telegram', 'bot_token', '098765:xxxxxxxxxxxxx')
	config.set('Telegram', 'custom_server', '')

	with open(config_file, 'w') as configfile:
		config.write(configfile)

	print("Config file has been reset to default!")	

def url(bot_token: str) -> str:
	custom_server = config['Telegram']['custom_server']
	if custom_server == '':
		return f'https://api.telegram.org/bot{bot_token}/getMe'
	else:
		return f'{custom_server}/bot{bot_token}/getMe'

def verify_token(bot_token: str):
	r = requests.get(url(bot_token))
	try:
		verify_data = r.json()
	except JSONDecodeError:
		sys.exit(r.text)
	if verify_data['ok'] == True:
		return True, verify_data["result"]["username"]
	elif verify_data['ok'] == False:
		return False, None

def test_token(bot_token: str):
	is_token_correct, bot_name = verify_token(bot_token)
	if is_token_correct:
		print(f'Bot Token is correct and Bot username is {bot_name}.')
	else:
		print(f'Bot Token is incorrect.')

def upload_url(bot_token: str) -> str:
	config = configparser.ConfigParser()
	config.read(config_file)
	custom_server = config['Telegram']['custom_server']
	if custom_server == '':
		return 'https://api.telegram.org'
	else:
		return custom_server

def uploader(bot_token: str, chat_id: str, file_name: str, server_url: str = "https://api.telegram.org", caption: str = None):

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
	

def upload_file(bot_token: str, chat_id: str, file_name: str, caption: str = None):

	file_size = os.path.getsize(file_name)
	server_url =  upload_url(bot_token)
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

def download(url: str, bot_token: str, chat_id: str, caption: str = None):
	download_path = 'downloads'
	if not os.path.isdir(download_path):
		os.mkdir(download_path)

	filename = os.path.basename(url)

	yes = {'yes','y','ye',''}
	choice = input(f"Do you want change filename {filename[0:60]} [Y/n]: ").lower()
	if choice in yes:
		filename = input("Enter new file name with extension: ")

	file_path = os.path.join(download_path, filename)

	print("Downloading file......")
	try:
		downloader(url, file_path)
	except OSError:
		print("File name is too log !")
		filename = input("Enter new filename : ")
		file_path = os.path.join(download_path, filename)
		downloader(url, file_path)
	
	print("\nUploading file......")
	upload_file(bot_token, chat_id, file_path, caption)

def files():
	try:
		files = os.listdir('downloads')
	except FileNotFoundError:
		sys.exit('Directory "downloads" not found !')
	if files != []:
		print("id -> File Name")
		i = 0
		for file in files:
			i += 1
			print(f"{i} -> {file[0:55]}")

def delete():
	try:
		files = os.listdir('downloads')
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

def get_id(bot_token:str):
	if bot_token == '098765:xxxxxxxxxxxxxxxxx':
		bot_token = input("Enter your telegram bot api token  : ")
		config.set('Telegram', 'bot_token', bot_token)
		with open(config_file, 'w') as configfile:
			config.write(configfile)
	url = f'https://api.telegram.org/bot{bot_token}/getUpdates'
	r = requests.get(url)
	resp = r.json()

	if resp['ok'] == True:
		for chat_id in resp['result']:
			if 'my_chat_member' in chat_id:
				print("Chad ID        ->  Chat Name")
				print(str(chat_id['my_chat_member']['chat']['id']) + " -> " + chat_id['my_chat_member']['chat']['title'])
			else:
				print("No chat id found, Remove your bot from chat and add it again, then run it")
	else:
		print(resp)
		print("\nThere is something error")