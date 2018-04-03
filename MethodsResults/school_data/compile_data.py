# Date of last edit: Friday, 03.30.2018
#
# Author: Kevin Sun
#
# This compile_data.py file will take multiple csv files, clean
# and reorganize the data into a single dataframe. Each row of the
# final dataframe will contain all relevant numbers and data points
# for a single student.


from pandas import ExcelWriter
from pandas import ExcelFile
import numpy as np
import pandas as pd
from collections import defaultdict

########## IMPORTANT ############
#								#
# WHEN NEW FILES ARE DOWNLOADED #
#      COPY AND PASTE THE       #
#      NEW FILENAMES BELOW	    #
#								#
#################################

# FILE UPLOAD DATE IS: FEBRUARY 16, 2018

GPA_DATA = "CPSHSStudentGPAs(updatedweekly) (7).csv"
CLASS_RANK_DATA = "Report Status- CPS_Class Rank (GPA) (3).csv"
WEEKLY_ATTN_DATA = "Weekly Attendance % Details_20180216.csv"
YTD_ATTN_DATA = "YTD Attn Details_20180216.csv"
SWIPE_DATA = "-Verify.net-GEN_View_Student_Swipe_Print_Report_20180216.csv"
ORANGE_DATA = "ORANGE List_Week of March 5th, 2018 - 9th Grade .csv"
EMAIL_LIST =  "Email List - Username and Passwords_as of 9-7-2017.xls"
SAT_9 = "scores-by-org 2018-03-27T12-48-59.xlsx"
SAT_10 = "scores-by-org 2018-03-27T12-50-29.xlsx"
SAT_11 = "scores-by-org 2018-03-08T09-08-59.xlsx"
start_date = "March 26, 2018" 
end_date = "March 30, 2018"

###########################
#    PLEASE DO NOT MAKE   #
#   CHANGES TO THE CODE   #
# 		   BELOW          #
###########################

######### STEP 1 ##########
#    IMPORT THE DATA      #
# FILTER RELEVANT COLUMNS #
#    THIS STEP HAS 5      #
#   RELEVANT FUNCTIONS	  #
###########################

def import_gpa_data(filename):
	"""
	This function takes csv file of STUDENT GPA DATA and 
	returns a cleaned pandas dataframe w/ columns renamed.

	Input:
		- filename: a string name of the csv file
	Output:
		- gpa_df: a pandas dataframe of the gpa data
	"""
	gpa_df = pd.read_csv(filename, index_col='STUDENT ID')
	gpa_df = gpa_df.rename(index=int, columns={"GRADE LEVEL": "grade", 
		"LAST NAME": "last_name", "FIRST NAME": "first_name", 
		"AVG GPA":"avg_gpa"})
	gpa_df.index.names = ['ID']

	return gpa_df


def import_rank_data(filename):
	"""
	This function takes csv file of STUDENT CLASS RANK DATA and 
	returns a cleaned pandas dataframe w/ columns renamed.

	Input:
		- filename: a string name of the csv file
	Output:
		- classrank_df: a pandas dataframe of the class rank data
	"""
	classrank_df = pd.read_csv(filename, header=None,
		usecols=[13,20,21,22], index_col=0)
	classrank_df = classrank_df.rename(index=int, columns={20: "class_rank",
		21: "class_size", 22: "credits_earned"})
	classrank_df.index.names = ['ID']

	return classrank_df


def import_week_attn_data(filename):
	"""
	This function takes csv file of STUDENT WEEKLY ATTENDANCE DATA and 
	returns a cleaned pandas dataframe w/ columns renamed.

	Input:
		- filename: a string name of the csv file
	Output:
		- weekly_df: a pandas dataframe of the weekly attendance data
	"""
	weekly_df = pd.read_csv(filename, usecols=['Student ID',
		'Week','Attendance Pct'], index_col='Student ID')
	weekly_df = weekly_df.rename(index=int, columns={"Week": "week",
		"Attendance Pct": "weekly_attn"})
	weekly_df.index.names = ['ID']
	weekly_df['start_date'] = start_date
	weekly_df['end_date'] = end_date
	
	return weekly_df


def import_year_attn_data(filename):
	"""
	This function takes csv file of STUDENT YTD ATTENDANCE DATA and 
	returns a cleaned pandas dataframe w/ columns renamed.

	Input:
		- filename: a string name of the csv file
	Output:
		- ytd_attn_df: a pandas dataframe of the year-to-date attendance data
	"""
	ytd_attn_df = pd.read_csv(filename, usecols=['Student ID',
		'Current School', 'Attendance Pct'], index_col='Student ID')
	# keep only active studenst and drop inactive students
	active = ytd_attn_df['Current School'] == "HYDE PARK HS"
	ytd_attn_df = ytd_attn_df[active]
	# drop Current School column
	ytd_attn_df = ytd_attn_df.drop(labels = "Current School", axis=1)
	ytd_attn_df = ytd_attn_df.rename(index=int, columns={"Attendance Pct"
		: "ytd_attn"})
	ytd_attn_df.index.names = ['ID']				
	
	return ytd_attn_df


def import_swipe_data(filename):
	"""
	This function takes csv file of STUDENT SWIPE DATA and 
	returns a cleaned pandas dataframe w/ columns renamed.

	Input:
		- filename: a string name of the csv file
	Output:
		- final_swipe_df: a pandas dataframe of the swipe data
	"""
	# read in swipe report data and rename columns
	swipe_df = pd.read_csv(filename, usecols=['Textbox20',
		'Textbox12', 'Textbox14', 'Type'])
	swipe_df = swipe_df.rename(index=int, columns={
		"Textbox20": "ID", "Textbox12": "date",
		"Textbox14": "swipe_time"})
	# keep only student ID number in ID column
	swipe_df['ID'] = swipe_df['ID'].apply(lambda x: int(x.split(" ")[0]))
	drop_list = []
	for row in swipe_df.itertuples():
		index, time = row[0], row[3]
		h, m, s = time.split(":")
		cut_off = int(h+m)
		# count only students swiping between 900-1030am
		if (cut_off < 900) or (cut_off > 1030):
			drop_list.append(index)
			swipe_df1 = swipe_df.drop(drop_list)
	swipe_df1.set_index('ID', inplace=True)
	# initialize defualt dictionaries to put indiv. data into single row
	d_date = defaultdict(list)
	d_time = defaultdict(list)
	for t in swipe_df1.itertuples():
		i, d, s, x = t
		d_date[i].append(d)
		d_time[i].append(s)
	# make values a string
	d_date = str_list(d_date)
	d_time = str_list(d_time)
	# put into data frames
	df_date = pd.DataFrame.from_dict(d_date, orient='index')
	df_time = pd.DataFrame.from_dict(d_time, orient='index')
	final_swipe_df = pd.merge(df_date, df_time, left_index=True, 
		right_index=True)
	# rename columns
	final_swipe_df = final_swipe_df.rename(index=int, 
		columns={"0_x": "late_date", "0_y":"late_time"})


	return final_swipe_df


def str_list(d):
	"""
	This is a helper function to turn the values of the keys of a
	python dictionary into a string. This is utilized for cleaning
	the swipes dataframe.
	"""
	d_new = {}
	for key, value in d.items():
		d_new[key] = str(value)

	return d_new

def import_orange_list(filename):
	"""
	This function takes csv file of ORANGE LIST students and
	returns a cleaned pandas dataframe w/ columns renamed.

	Input:
		- filename: a string name of the csv file
	Output:
		- orange_df: a pandas dataframe of orange list students
	"""
	orange_df = pd.read_csv(filename, usecols=['Student', 'Steps for Removal from Orange List'])
	# rename columns
	orange_df = orange_df.rename(index=int, columns={'Student':'ID', 
		'Steps for Removal from Orange List':'study_hall'})
	# extract Student ID numbers
	orange_df['ID'] = orange_df['ID'].apply(lambda x: int(x.split(" ")[1]))
	# add status column
	orange_df['orange_status'] = "ARE"
	# index by ID numbers
	orange_df.set_index('ID', inplace=True)


	return orange_df

def import_sat(filenames):
	"""
	This function takes an excel files of SAT_9, SAT_10, SAT_11 and 
	returns a cleaned pandas dataframe w/ columns renamed.

	Input:
		- filename: a list of names of the excel file

	Output:
		- sat_df: a pandas dataframe of SAT score data
	"""
	# import SAT scores for each grade
	l = []
	for file in filenames:
		df = pd.read_excel(file, skiprows=9, usecols=['Student ID', 'Total Score', 
													'ERW', 'Math'])
		# drop students withg missing IDs
		df.dropna(inplace=True)
		# make ID an integer and index
		df['Student ID'] = df['Student ID'].apply(lambda x: int(x))
		# rename columns 		
		df = df.rename(index=int, columns={'Student ID':'ID', 'Total Score':'composite_sat', 
						'Math':'math_sat', 'ERW':'erw_sat'})
		# index by ID
		df.set_index('ID')
		l.append(df)

	nine, ten, eleven = l
	sat_df = nine.append([ten, eleven])
	sat_df = sat_df.set_index('ID')

	return sat_df


def import_student_emails(filename):
	"""
	This function takes csv file of STUDENT EMAILS and 
	returns a cleaned pandas dataframe w/ columns renamed.

	Input:
		- filename: a string name of the excel file
	Output:
		- email_df: a pandas dataframe of student emails
	"""
	email_df = pd.read_excel(filename, sheetname="All",
		usecols=[5,6])
	email_df.set_index('ID#', inplace=True)
	email_df = email_df.rename(index=int, columns={"CPS Email Address": "email",})
	email_df.index.names = ['ID']
	
	return email_df	

######### STEP 2 ##########
#   MERGE THE DATAFRAMES  #
#	INTO A SINGLE DATA-   #
#			FRAME         #
###########################

def master_dataframe(threshold):
	"""
	This function makes calls on each function that imports and cleans
	each csv file, concats the dataframes into a single master dataframe 
	while also creating new dataframes divided by grade level.

	Input:
		- threshold: integer of the max # of empty cells per student
					 we are willing to tolerate in the master dataframe
	Output:
		- master_dataframe: dataframe of all student data
		- nine: dataframe of all 9th grade student data
		- ten: dataframe of all 10th grade student data
		- eleven: dataframe of all 11th grade student data
		- twelve: dataframe of all 12th grade student data
	"""
	# import each of the dataframes
	gpa = import_gpa_data(GPA_DATA)
	rank = import_rank_data(CLASS_RANK_DATA)
	week = import_week_attn_data(WEEKLY_ATTN_DATA)
	year = import_year_attn_data(YTD_ATTN_DATA)
	swipe = import_swipe_data(SWIPE_DATA)
	orange = import_orange_list(ORANGE_DATA)
	sat = import_sat([SAT_9, SAT_10, SAT_11])
	email = import_student_emails(EMAIL_LIST)
	master_dataframe = pd.concat([email,gpa,rank,sat,week,year,swipe,orange],axis=1)
	
	# drop rows missing excessive amounts of data
	master_dataframe = master_dataframe.dropna(thresh=threshold)
	# fill in NaNs
	master_dataframe[['late_date', 'late_time', 'study_hall']] = master_dataframe[['late_date', 
																'late_time', 'study_hall']].fillna(value="None")
	master_dataframe[['orange_status']] = master_dataframe[['orange_status']].fillna(value="ARE NOT")
	master_dataframe[['composite_sat', 'erw_sat', 'math_sat']] = master_dataframe[['composite_sat', 'erw_sat', 'math_sat']].fillna(value="N/A")
	# obtain separate dataframes for each grade level
	nine, ten, eleven, twelve = groupby_grade(master_dataframe)

	return master_dataframe, nine, ten, eleven, twelve


def groupby_grade(master_dataframe):
	"""
	This is a helper function that drops the student names of the 
	master dataframe and divides the master dataframe into
	four separate dataframes by grade.
	"""
	no_name_df = master_dataframe.drop(['last_name', 'first_name', 'email'], axis=1)
	grouped = list(no_name_df.groupby(['grade']))
	nine, ten, eleven, twelve = grouped[0][1], grouped[1][1], grouped[2][1], grouped[3][1]

	return nine, ten, eleven, twelve


def get_excel_spreadsheets(threshold):
	"""
	This function creates a single Excel file with multiple worksheets: a 
	master worksheet, and one for each grade level.

	Input:
		- threshold: integer of the max # of empty cells per student
					 we are willing to tolerate in the master dataframe
	"""
	master, nine, ten, eleven, twelve = master_dataframe(threshold)

	writer = pd.ExcelWriter('ALL_STUDENT_NUMBERS.xlsx')
	master.to_excel(writer,'ALL STUDENTS')
	nine.to_excel(writer,'GRADE_9')
	ten.to_excel(writer,'GRADE_10')
	eleven.to_excel(writer,'GRADE_11')
	twelve.to_excel(writer,'GRADE_12')
	writer.save()


###### OTHER HELPER FUNCTIONS #########

def missing_emails(master_dataframe):
	"""
	This function obtains the first name, last name, id numbers of students
	who have missing emails.

	Input:
		- master_dataframe: a pandas datafarme
	"""
	master, nine, ten, eleven, twelve = master_dataframe(threshold)
	missing_email = master_dataframe['email'].isnull()

	l = set()
	for id_num, value in missing_email.iteritems():
		if value == True:
			l.add(id_num)
	d = {}
	for i in master.iterrows():
		id_num = i[0]
		if id_num in l:
			last_name = i[1][1]
			first_name = i[1][2]
			name = (last_name, first_name)
			d[id_num] = name

	w = csv.writer(open("missing_email.csv", "w"))

	for key, val in d.items():
		w.writerow([key,val])












