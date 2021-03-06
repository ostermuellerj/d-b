# DATABASE HW1
# John Ostermueller and Gavin Glenn
# 2/3/20

#Field Size Declarations
rank_field_size = 20
name_field_size = 60
city_field_size = 20
state_field_size = 20
zip_field_size = 20
employees_field_size = 20

record_line_size = rank_field_size+name_field_size+city_field_size+state_field_size+zip_field_size+employees_field_size + 1
num_fields = 6 
num_records = 500

#Number of items in overflow
num_in_overflow = 0

#Global Open Database Declarations
db_name = ""

config = None
data = None
overflow = None

# REQUIRED FUNCTIONS:

# converts input .csv into triplet of files:
# Fortune_500_HQ.config: contains the number of records in the data file, describes the names, sizes of the fields in order
# Fortune_500_HQ.data: contains the data records, one per line, with fixed size fields
# Fortune_500_HQ.overflow: initially empty
def create_database():
	print("CREATING DATABASE")

	global config, data, overflow

	# Input File
	csv_name = input("Input the name of a .csv file (e.g. input): ") + str(".csv")

	# Get Data for files
	read_data = open(str(csv_name), "r")
	entries = 0
	record_size = 0
	for line in read_data:
		entries+=1
		if len(line) > record_size:
			record_size = len(line)
	read_data.close()
	
	num_records = entries-1

	#print("Record Size: " + str(record_size))
	print("Record Line Size: " + str(record_line_size))
	print("Num Records: " + str(num_records))

	# Create Config
	update_config(csv_name[:-4])

	# Create Data
	read_data = open(str(csv_name), "r") #input .csv file
	data = open(str(csv_name[:-4])+".data", "w") #new .data file
	
	for line in read_data:
		# A note to mention is that when reading the from the data the actual line length
		# will be one more than the displayed line length to accomodate for \n character

		line = line.rstrip(" ")
		fields = line.split(",")
		#print(fields)

		if fields[0] == "RANK":
			continue

		#original order: RANK,NAME,CITY,STATE,ZIP,EMPLOYEES                                 
		#new order: NAME,RANK,CITY,STATE,ZIP,EMPLOYEES                                 
		new_line = fix_length(fields[1], name_field_size) # Name    
		new_line = new_line+fix_length(fields[0], rank_field_size) # Rank
		new_line = new_line+fix_length(fields[2], city_field_size) # City
		new_line = new_line+fix_length(fields[3], state_field_size) # State
		new_line = new_line+fix_length(fields[4], zip_field_size) # Zip
		new_line = new_line+fix_length(fields[5], employees_field_size) # Employees

		new_line = str(new_line) + "\n"
		data.write(new_line)
	data.close()
	read_data.close()

	# Create Overflow
	overflow = open(str(csv_name[:-4])+".overflow", "w")
	overflow.close()

# opens input database.
# if another database is already open, the user is prompted to close that database first.
def open_database():
	global db_name, config, data, overflow
	print("OPENING DATABASE " + db_name)
	if db_name != "":
		print("Another database is already open, please close " + db_name + ".")
		return
	
	db_name = input("Input the name of a database (e.g. Fortune_500_HQ): ")
	config = open(str(db_name)+".config", "r+")
	data = open(str(db_name)+".data", "r+")
	overflow = open(str(db_name)+".overflow", "r+")

# closes current database files.
def close_database():
	global db_name, config, data, overflow
	print("CLOSING DATABASE " + db_name)
	if db_name == "":
		print("The database is not open.")
		return
	
	db_name = ""
	config.close()
	data.close()
	overflow.close()

# finds record via primary key with seeks and binary search.
# displays name (from the config file) and the value (from the data file record)
def display_record():
	print("DISPLAYING RECORD")

	global db_name
	if db_name == "":
		print("Please open the database first.")
		return
	print(binary_search())

# finds input record (using same process as displayRecord), then displays contents and allows updates in a specified field.
# the primary key is not allowed to be updated.
def update_record():
	print("UPDATE RECORD")

	global db_name, data
	if db_name == "":
		print("Please open the database first.")
		return
	
	#Find Record location
	location = -1
	while location == -1:
		location = binary_search(1)
	
	#get what they want to update
	record = get_record(location)

	#Change the data
	record_data = [record[:60], record[60:80], record[80:100], record[100:120], record[120:140], record[140:160]]
	print("what would you like to change?")
	print("Enter an integer for the field you would like to change:\n1. rank\n2. city\n3. state\n4. zip\n5. # of employees\n")
	
	menu = input()
	#Rank
	if menu == "1":
		print("Please input a new rank for " + str(record_data[0]) + ":")
		new_rank = input()
		new_rank = fix_length(str(new_rank), 20)
		record_data[1] = new_rank
	#City
	elif menu == "2":
		print("Please input a new city for " + str(record_data[0]) + ":")
		new_city = input()
		new_city = fix_length(str(new_city), 20)
		record_data[2] = new_city
	#State
	elif menu == "3":
		print("Please input a new state for " + str(record_data[0]) + ":")
		new_state = input()
		new_state = fix_length(str(new_state), 20)
		record_data[3] = new_state
	#Zip
	elif menu == "4":
		print("Please input a new zip for" + str(record_data[0]) + ":")
		new_zip = input()
		new_zip = fix_length(str(new_zip), 20)
		record_data[4] = new_zip
	#Number of Employees
	elif menu == "5":
		print("Please input a new number of employees for " + str(record_data[0]) + ":")
		new_employees = input()
		new_employees = fix_length(str(new_employees), 20)
		record_data[5] = new_employees
	#Terminate on unverified selection
	else:
		print("Undefined Function, returning to menu")
		return

	#remake the line
	record_data = "".join(record_data) + "\n"

	#Write the line to the file in the location
	data.seek(location * record_line_size)
	data.write(record_data)
	print("New Data has been successfully written")

# generates a "human readable" text file which displays the first ten records sorted by primary key
def create_report():
	print("CREATING REPORT")

	if db_name == "":
		print("Please open the database first.")
		return

	merge()
	f = open("report.txt","w")
	f.write("Below are the top ten records sorted by primary key (NAME):\n\n")
	for i in range(0, 10):

		#print first ten records nicely formatted
		record = get_record(i)
		out = str(i+1) + ". " + "NAME: " + record[:60] + "\n"
		out += "   RANK: " + record[60:80] + "\n"
		out += "   CITY: " + record[80:100] + "\n"
		out += "   STATE: " + record[100:120] + "\n"
		out += "   ZIP: " + record[120:140] + "\n"
		out += "   EMPLOYEES: " + record[140:160] + "\n\n"

		print(out)
		f.write(out)
	f.close()

# adds a record to the database by taking in information
def add_record():
	print("ADD RECORD")

	global num_in_overflow, overflow, db_name

	if db_name == "":
		print("database not open")
		return

	#count how many are in overflow
	overflow.seek(0,0)
	if overflow.readline() == "":
		num_in_overflow=0

	if num_in_overflow >= 4:
		merge()

	user_input = input("Input the following fields separated by commas: NAME, RANK, CITY, STATE, ZIP, EMPLOYEES\n").upper().split(",")
	
	outstring = "" + fix_length(user_input[0], name_field_size)
	outstring += fix_length(user_input[1], rank_field_size)
	outstring += fix_length(user_input[2], city_field_size)
	outstring += fix_length(user_input[3], state_field_size)
	outstring += fix_length(user_input[4], zip_field_size)
	outstring += fix_length(user_input[5], employees_field_size)

	overflow.seek((num_in_overflow)*record_line_size, 0)
	overflow.write(outstring + "\n")

	#For some reason the overflow file doesnt update so just close and reopen
	update_overflow()
	update_config(db_name)

	#update count of overflow
	num_in_overflow+=1

# Deletes a record given an input of the key
def delete_record():
	global data
	print("DELETE RECORD")

	#find index of record to delete
	index = binary_search(1)
	print("deleting record with key: " + get_key(get_record(index)))
	#delete record
	file_shift_delete(index)
	update_config(db_name)

# OTHER FUNCTIONS

#updates and writes to config
def update_config(csv_name):
	global num_records, record_line_size
	config = open(str(csv_name)+".config", "w")
	config.write("There are " + str(num_records) + " records in this database.\n")
	config.write("Each record is " + str(record_line_size) + " characters long (including the \\n).\n")
	config.close()

#updates and rewrites to data
def update_data():
	global db_name, data
	data.close()
	data = open(db_name+ ".data", "r+")

#updates and rewrites to overflow
def update_overflow():
	global db_name, overflow
	overflow.close()
	overflow = open(db_name+ ".overflow", "r+")

# shift up (leaves a copy at bottom)
# remove a line of data by shifting subsequent lines up by 1
def file_shift_delete(line_num):
	global num_records
	for i in range(line_num, num_records):
		data.seek((i+1)*record_line_size, 0)
		record = data.readline()
		data.seek(i*record_line_size, 0)
		data.write(record)
	num_records-=1
	data.seek(i*record_line_size)
	data.truncate()
	# data.write(""*record_line_size)

# shift down (leaves a copy at top)
# add an empty space in .data 
def file_shift_add(line_num):
	global num_records

	for i in range(num_records, line_num-1, -1):
		#print("move record #" + str(i))
		data.seek(i*record_line_size, 0)
		record = data.readline()
		# print(record)
		data.seek((i+1)*record_line_size, 0)
		data.write(record)
	num_records+=1

# finds and returns a record given the primary key (name)
# op = 0 is standard usage, op = 1 is for returining location of found key, op = 2 is for returning location for potential key
def binary_search(op = 0, data_key = None):
	print("findRecord")
	global data, num_records, record_line_size
	key = input("Input primary key (name) to search by (case insensitive):") if data_key == None else data_key
	key = str(key).upper()
	low = 0
	high = num_records-1
	record = "requested record NOT_FOUND"

	#search for key in overflow
	if op==0:	
		# print(num_in_overflow)
		for i in range(num_in_overflow):
			overflow.seek(i*record_line_size, 0)
			overflow_record = overflow.readline()
			# print(overflow_record)
			if get_key(overflow_record) == key:
				return overflow_record

	while low <= high:
		mid = (low+high)//2
		mid_record = get_record(mid)
		mid_key = get_key(mid_record)
		#print(mid_key)
		if mid_key == key: 
			print("found!")
			return mid_record if op == 0 else mid
		elif mid_key < key:
			#print("key>mid")
			low = mid+1
		else:
			#print("key<mid")
			high = mid-1

	#Get the address of the found data
	return record if op == 0 else mid if op == 2 else -1 #if record not found

#Gets a records data from the specified address (offset)
def get_record(record_num):
	global data, num_records, record_line_size

	record = "requested record NOT_FOUND"

	if record_num>=0 and record_num<= num_records:
		data.seek(0,0)
		data.seek(((record_num) * record_line_size)) #offset from the beginning of the file
		record = data.readline()
		# print(record)
	return record

# returns key (name) from given record
def get_key(record):
	return(record[:name_field_size].rstrip(" "))

# moves all elements in overflow to their appropriate locatoin in .data (overflow should be empty afterwards)
def merge():
	print("merge")
	global data, overflow, num_in_overflow
	#Get data from overflow
	overflow.seek(0)
	somedata = overflow.read()
	somedata = somedata.split("\n")[:-1]
	#print(somedata)
	for line in somedata:
		key = line[:60].upper()
		#Find indexes for each line
		index = binary_search(2, key)+1
		#insert into the data file
		file_shift_add(index)
		data.seek(index*record_line_size)
		data.write(line + "\n")
	update_data()

	num_in_overflow = 0
	overflow.seek(0)
	overflow.truncate()

# fixes length of strings to insert into the database
def fix_length(string, length):
    string = string.rstrip(" \n")
    if len(string) > length:
        print("Something is seriously wrong here.")
    else:
        diff = length - len(string)
        out_string = str(string) + " "*diff
        return out_string

# displays list of 8 required functions.
# executes a given function based on user input.
def menu():
	print("Input the appropriate number to execute a function:\n1. Create Database\n2. Open Database\n3. Close Database\n4. Display Record\n5. Update Record\n6. Create Report\n7. Add Record\n8. Delete Record\n9. Quit\n")
	user_input = input()
	# print(user_input)
	if user_input == "1":
		create_database()
	elif user_input == "2":
		open_database()
	elif user_input == "3":
		close_database()
	elif user_input == "4":
		display_record()
	elif user_input == "5":
		update_record()
	elif user_input == "6":
		create_report()
	elif user_input == "7":
		add_record()
	elif user_input == "8":
		delete_record()
	elif user_input == "9":
		close_database()
		exit()
	elif user_input == "0":
		# print(binary_search(2, str(input())))
		# print(num_in_overflow)
		# overflow.seek(0,0)
		# if overflow.readline() == "":
		# 	print("empty")
		merge()

# always display the menu until system exit
while True:
	menu()
