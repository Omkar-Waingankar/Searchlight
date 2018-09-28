import os

def log(message):
	with open("mods_checker_log.txt", "a") as logsfile:
		logsfile.write(message + "\n") 

try:
	list_of_folders = os.listdir('./scraped_folders')
	list_of_folders = sorted(list_of_folders)
	if '.DS_Store' in list_of_folders:
		list_of_folders.remove('.DS_Store')
	for folder in list_of_folders:
		list_of_files = os.listdir('./scraped_folders/' + str(folder))
		if '.DS_Store' in list_of_files:
			list_of_files.remove('.DS_Store')
		if 'nohup.out' in list_of_files:
			list_of_files.remove('nohup.out')
		list_of_files = sorted(list_of_files)
		first_file = list_of_files[0]
		last_file = list_of_files[-1]
		first_file_extension = first_file[-3:]
		last_file_extension = last_file[-3:]
		if first_file_extension == 'xml' or last_file_extension == 'txt':
			log(str(folder))
			log("    " + str(first_file))
			log("    " + str(last_file))
	log("DONE CHECKING")
except Exception as e:
	log('ERROR CAUGHT: ' + repr(e))
	error_file = open("mods_checker_error_log.txt", "w")
	traceback.print_exc(file=error_file)
	log("Check error_log.txt file for traceback")