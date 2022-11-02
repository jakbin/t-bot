import setuptools
from tl_bot import __version__

with open("README.md", "r") as readme_file:
	readme = readme_file.read()

setuptools.setup(
	name="tl-bot",
	version=__version__,
	author="Jak Bin",
	author_email="jakbin4747@gmail.com",
	description="upload files to your telegram channel or group with your telegram bot",
	long_description=readme,
	long_description_content_type="text/markdown",
	url="https://github.com/jakbin/t-bot",
	install_requires=["tqdm","requests","requests-toolbelt"],
	python_requires=">=3",
	project_urls={
		"Bug Tracker": "https://github.com/jakbin/t-bot/issues",
	},
	classifiers=[
		"Programming Language :: Python :: 3.6",
		"License :: OSI Approved :: MIT License",
		"Natural Language :: English",
		"Operating System :: OS Independent",
	],
	keywords='telegram,t-bot,telegram-api,telegram-api-bot,telegram-file-upload,elegram-upload',
	packages=["tl_bot"],
	package_data={  
		'tl_bot': [
			'config.ini',
		]},
	entry_points={
		"console_scripts":[
			"t-bot = tl_bot.cli:main"
		]
	}
)