import os, sys

def files(DOWNLOADS_DIR)	-> None:
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

def delete(DOWNLOADS_DIR) -> None:
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
