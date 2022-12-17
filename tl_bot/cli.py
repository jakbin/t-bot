import argparse
import configparser

from tl_bot import __version__
from tl_bot.main import setup, test_token, reset, upload_file, download, config_file, get_id, files, delete

package_name = "t-bot"

config = configparser.ConfigParser()
config.read(config_file)
chat_id = config['Telegram']['chat_id']
bot_token = config['Telegram']['bot_token']

example_uses = '''example:
   t-bot setup
   t-bot reset
   t-bot test
   t-bot getid
   t-bot up {files_name} -c file_caption
   t-bot d {url} -c caption'''

def main(argv = None):
	parser = argparse.ArgumentParser(prog=package_name, description="upload your files to your group or channel", epilog=example_uses, formatter_class=argparse.RawDescriptionHelpFormatter)
	subparsers = parser.add_subparsers(dest="command")

	setup_parser = subparsers.add_parser("setup", help="setup your telegram credentials")

	reset_parser = subparsers.add_parser("reset", help="reset to default your telegram credentials")

	test_parser = subparsers.add_parser("test", help="test telegram bot token")

	getid_parser = subparsers.add_parser("getid", help="test telegram bot token")

	upload_parser = subparsers.add_parser("up", help="upload file to your group or channel")
	upload_parser.add_argument("filename", type=str, help="one or more files to upload")
	upload_parser.add_argument('-c', '--caption', type=str, default=None, help="Send caption for your file")

	download_parser = subparsers.add_parser("d", help="download and upload file to your group or channel")
	download_parser.add_argument("url", type=str, help="url")
	download_parser.add_argument('-c', '--caption', type=str, default=None, help="Send caption for your file")

	files_parser = subparsers.add_parser("files", help="Show all available files 'downloads' folder")

	delete_parser = subparsers.add_parser("del", help="delete available files 'downloads' folder")

	parser.add_argument('-v',"--version",
							action="store_true",
							dest="version",
							help="check version of t-bot")

	args = parser.parse_args(argv)

	if args.command == "test":
		return test_token(bot_token)
	elif args.command == "getid":
		return get_id(bot_token)
	elif args.command == "setup":
		return setup()
	elif args.command == "reset":
		return reset()
	elif args.command == "up":
		return upload_file(bot_token, chat_id, args.filename, args.caption)
	elif args.command == "d":
		return download(args.url, bot_token, chat_id, args.caption)
	elif args.command == "files":
		return files()
	elif args.command == "del":
		return delete()
	elif args.version:
		return print(__version__)
	else:
		parser.print_help()

if __name__ == '__main__':
	raise SystemExit(main())