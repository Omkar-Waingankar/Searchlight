import os

def log(message):
	with open("mods_mover_log.txt", "a") as logsfile:
		logsfile.write(message + "\n") 

try:
	list_of_folders = os.listdir('./scraped_folders')
	list_of_folders = sorted(list_of_folders)
	if '.DS_Store' in list_of_folders:
		list_of_folders.remove('.DS_Store')
	for i in range(len(list_of_folders)):
		folder = list_of_folders[i]
		list_of_files = os.listdir('./scraped_folders/' + str(folder))
		if 'DS_Store' in list_of_files:
			list_of_files.remove('.DS_Store')
		if 'nohup.out' in list_of_files:
			list_of_files.remove('nohup.out')
		list_of_files = sorted(list_of_files)
		last_file = list_of_files[-1]
		last_file_extension = last_file[-3:]
		if last_file_extension == 'txt':
			if i == len(list_of_folders) - 1:
				log(str(folder))
				log("    " + "last folder")
				log("    " + str(list_of_files[0]))
				log("    " + str(last_file))
				continue
			next_folder = list_of_folders[i+1]
			os.rename("./scraped_folders/" + folder + "/" + last_file, "./scraped_folders/" + next_folder + "/" + last_file)
			log("Moved: " + str(last_file) + " from " + folder + " to " + next_folder)
	log("DONE MOVING")
except Exception as e:
	log('ERROR CAUGHT: ' + repr(e))
	error_file = open("mods_mover_error_log.txt", "w")
	traceback.print_exc(file=error_file)
	log("Check error_log.txt file for traceback")