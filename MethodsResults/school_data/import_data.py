# Author: Kevin Sun
# Date of last edit: Wednesday, May 2, 2018

import pandas as pd 
import numpy as np 
from pandas import ExcelWriter
from pandas import ExcelFile
import re
from ethnicolr import census_ln, pred_census_ln, pred_wiki_ln, pred_wiki_name, pred_fl_reg_name

TEACHERS = "teacher_positions_12312017.xls"
RETENTION = "retention_rates.xls"
STDNT_RACE = "demo_stdnt_race_2018.xls"
STDNT_SPED_ELL_T1 = "demo_sped_ell_lunch_2018.xls"

def impute_final_race_estimate():
	"""
	This function uses an ensemble method to determine a final race
	estimate from the four methods (census_last, wiki_last, wiki_full,
	fl_full).

	Input: None
	Output:

	"""
	df = impute_names_all_methods()

	white_list = []

	# iterate through dataframe and get initial race pred. counts
	for t in df.itertuples():
		count_white = 0
		count_not_white = 0
		if t.census_lastname == "white":
			count_white += 1
		elif t.wiki_lastname == "white":
			count_white += 1
		elif t.wiki_fullname == "white":
			count_white += 1
		elif t.fl_fullname == "white":
			count_white += 1

		white_list.append(count_white)

	# push white_list into dataframe
	df['white_count'] = 

	return df


def impute_names_all_methods():
	"""
	This function utilizes the ethnicolr package to predict the race
	of teachers based on their name. It will append probabilities of
	each race to the dataframe and assign a "final race" to be used
	in the modeling process based on the greatest probability.

	Input: None
	Output:
		- df: a dataframe with four new columns attached that include 
		predictions for that teacher's race
	"""
	results = {}
	subset_df = make_teacher_subset()

	# run census_ln function
	# census_last = run_census_last(subset_df, 2010)
	# run pred_census_ln function
	pred_census_last = run_pred_census_ln(subset_df, 2010)
	# run pred_wiki_ln function
	pred_wiki_last = run_pred_wiki_ln(subset_df)
	# run pred_wiki_name function
	pred_wiki_full = run_pred_wiki_name(subset_df)
	# run pred_fl_reg_name function
	pred_fl_full = run_pred_fl_name(subset_df)

	df = import_teachers(TEACHERS)
	df['census_lastname'] = pred_census_last
	df['wiki_lastname'] = pred_wiki_last
	df['wiki_fullname'] = pred_wiki_full
	df['fl_fullname'] = pred_fl_full

	return df

# def run_census_last (subset_df, census_year):
#     """
#     This function runs the Census Ln Function.
#     """
#     has_last_name_df = subset_df[subset_df.teacher_last.notnull()].copy()
    
#     return census_ln(has_last_name_df, 'teacher_last', census_year)


def run_pred_census_ln (subset_df, census_year):
    """
    This function takes a dataframe of teacher information and 
    runs the Pred Census Ln Function.

    Input:
    	- subset_df: a dataframe that is a subset of teacher information
    Output:
    	- df: a dataframe with a predicted race imputation 
    """
    has_last_name_df = subset_df[subset_df.teacher_last.notnull()].copy() 
    df = pred_census_ln(has_last_name_df, 'teacher_last', census_year)
    
    #recode two race categories
    recode_dict = {'api': 'asian'}

    # replace values using generalized race categories
    df.replace(to_replace=recode_dict, value=None, inplace=True)
   
    # keep only the race column
    cols_to_keep = ['race']
    df = df[cols_to_keep]
    df.rename(columns={'race':'census_lastname'}, inplace=True)

    return df


def run_pred_wiki_ln (subset_df):
    """
    This function takes a dataframe of teacher information and
    runs the Pred Wiki Ln Function.

    Input:
    	- subset_df: a dataframe that is a subset of teacher information
    Output:
    	- df: a dataframe with a predicted race imputation 
    """
    has_last_name_df = subset_df[subset_df.teacher_last.notnull()].copy()
    df = pred_wiki_ln(has_last_name_df, 'teacher_last')
    
    # generalize the race categories
    recode_dict = {'GreaterEuropean,British': 'white',
    'GreaterEuropean,WestEuropean,Italian': 'white',
    'Asian,GreaterEastAsian,Japanese': 'asian', 
    'GreaterEuropean,Jewish':'white',
    'GreaterEuropean,EastEuropean': 'white',
    'GreaterEuropean,WestEuropean,Hispanic': 'hispanic', 
    'GreaterAfrican,Africans':'black',
    'GreaterEuropean,WestEuropean,Germanic': 'white',
    'GreaterEuropean,WestEuropean,Nordic': 'white', 
    'Asian,IndianSubContinent': 'white',
    'GreaterAfrican,Muslim': 'black', 
    'GreaterEuropean,WestEuropean,French':'white',
    'Asian,GreaterEastAsian,EastAsian':'asian'}

    # replace values using generalized race categories
    df.replace(to_replace=recode_dict, value=None, inplace=True)

    # keep only the race colummn
    cols_to_keep = ['race']
    df = df[cols_to_keep]
    df.rename(columns={'race':'wiki_lastname'}, inplace=True)

    return df


def run_pred_wiki_name (subset_df):
    """
    This function takes a dataframe of teacher information and
    runs the Pred Wiki Name Function.

    Input:
    	- subset_df: a dataframe that is a subset of teacher information
    Output:
    	- df: a dataframe with a predicted race imputation 
    """
    has_last_name_df = subset_df[subset_df.teacher_last.notnull()].copy()
    also_has_first_name_df = has_last_name_df[has_last_name_df.teacher_first.notnull()].copy()
    df = pred_wiki_name(also_has_first_name_df, 'teacher_first', 'teacher_last')
    
    # generalize the race categories
    recode_dict = {'GreaterEuropean,British': 'white',
    'GreaterEuropean,WestEuropean,Italian': 'white',
    'Asian,GreaterEastAsian,Japanese': 'asian', 
    'GreaterEuropean,Jewish':'white',
    'GreaterEuropean,EastEuropean': 'white',
    'GreaterEuropean,WestEuropean,Hispanic': 'hispanic', 
    'GreaterAfrican,Africans':'black',
    'GreaterEuropean,WestEuropean,Germanic': 'white',
    'GreaterEuropean,WestEuropean,Nordic': 'white', 
    'Asian,IndianSubContinent': 'white',
    'GreaterAfrican,Muslim': 'black', 
    'GreaterEuropean,WestEuropean,French':'white',
    'Asian,GreaterEastAsian,EastAsian':'asian'}

    # replace values using generalized race categories
    df.replace(to_replace=recode_dict, value=None, inplace=True)
    
    # keep only the race colummn
    cols_to_keep = ['race']
    df = df[cols_to_keep]
    df.rename(columns={'race':'wiki_fullname'}, inplace=True)

    return df


def run_pred_fl_name (subset_df):
	"""
    This function takes a dataframe of teacher information
    and runs the Pred Fl Reg Name Function.

    Input:
    	- subset_df: a dataframe that is a subset of teacher information
    Output:
    	- df: a dataframe with a predicted race imputation 
    """
	has_last_name_df = subset_df[subset_df.teacher_last.notnull()].copy()
	also_has_first_name_df = has_last_name_df[has_last_name_df.teacher_first.notnull()].copy()
	df = pred_fl_reg_name(also_has_first_name_df, 'teacher_first', 'teacher_last')

	#recode two race categories
	recode_dict = {'nh_white': 'white', 'nh_black': 'black'}
	
	# replace values using generalized race categories
	df.replace(to_replace=recode_dict, value=None, inplace=True)
	
	# keep only the race column
	cols_to_keep = ['race']
	df = df[cols_to_keep]
	df.rename(columns={'race':'fl_fullname'}, inplace=True)   
	
	return df


def make_teacher_subset():
	"""
	This function takes the imported teacher dataframe and keeps only the
	relevant columns needed for imputing teacher race based on name.

	Output:
		- df_subset: a pandas dataframe
	"""
	df = import_teachers(TEACHERS)
	cols_to_keep = ['school_id', 'school', 'count', 'teacher_first', 'teacher_last']

	subset_df = df[cols_to_keep]

	return subset_df


def get_staff_dict():
	"""
	This function produces a dictionary of total teacher count
	per school. Key (school name), Value (count)

	Input: None
	Output:
		- staff_dict: a python dictionary
	"""
	teacher_df = import_teachers(TEACHERS)
	staff_df = teacher_df.groupby('school').sum()
	staff_df.drop(['school_id'], inplace=True, axis=1)
	staff_dict = staff_df.to_dict()
	staff_dict = staff_dict['count']

	return staff_dict

def get_last_name(name):
	"""
	This is a helper function that gets the last name of the teacher
	"""
	last_name = re.findall(r"[\w']+", name)[0]
	
	return last_name

def get_first_name(name):
	"""
	This is a helper function that gets the first name of the teahcer
	"""
	first_name = re.findall(r"[\w']+", name)[1]
	
	return first_name

def import_teachers(filename):
	"""
	This function takes an excel file of teacher salaries and 
	returns a cleaned pandas dataframe w/ columns renamed.

	Input:
		- filename: a string name of the excel file
	Output:
		- df: a pandas dataframe with school and teacher name cols
	"""
	# import, clean, & format dataframe
	df = pd.read_excel(filename, sheetname='Export Worksheet', 
		usecols=[0,1,2,9,10])
	df.set_index('Pos #', inplace=True)
	df.rename(index=int, columns={'Dept ID': 'school_id','Department': 'school', 
		'Job Title': 'job_title', 'Name': 'teacher'}, inplace=True)
	df.index.names = ['ID']

	# filter out non-teacher & non-instructor positions
	l = list(df.job_title.unique())
	teach_list = [s for s in l if "Teacher" in s]
	# instructor_list = [s for s in l if "Instructor" in s]
	# counselor_list = [s for s in l if "Counselor" in s]
	# all_list = teach_list + instructor_list + counselor_list
	# df = df[df['job_title'].isin(all_list)]
	df = df[df['job_title'].isin(teach_list)]

	# filter out specific positions
	df = df[df.job_title != 'Teacher Compliance Analyst']
	df = df[df.job_title != 'Guidance Counselor Assistant']

	# create column of 1's to count teachers per school
	df['count'] = 1
	df.dropna(axis=0, how='any', inplace=True)
	
	# split each name into two different columns
	df['teacher_first'] = df.teacher.apply(get_first_name)
	df['teacher_last'] = df.teacher.apply(get_last_name)
	
	return df


def import_retention(filename):
	"""
	This function takes an excel file of retention rates and 
	returns a cleaned pandas dataframe w/ columns renamed.

	Input:
		- filename: a string name of the excel file
	Output:
		- df: a pandas dataframe
	"""
	# import, clean, & format dataframe
	df = pd.read_excel(filename, skiprows=1, sheetname="CollegeEnrollPersist_2017_sch")
	df.set_index('School ID', inplace=True)
	df.rename(index=int, columns={'School Name': 'school', 'Status as of 2017': 'status',
		'Graduates': '16_grads', 'Enrollments': '16_en', 'Enrollment Pct': '16_enp', 
		'Graduates.1': '15_grads', 'Enrollments.1': '15_en', 'Enrollment Pct.1': '15_enp', 
		'# of Enrollments Persisting': '15_pers', 'Persistence Pct': '15_pers_p', 
		'Graduates.2': '14_grads', 'Enrollments.2': '14_en', 'Enrollment Pct.2': '14_enp', 
		'# of Enrollments Persisting.1': '14_pers', 'Persistence Pct.1': '14_pers_p', 
		'Graduates.3': '13_grads', 'Enrollments.3': '13_en', 'Enrollment Pct.3': '13_enp', 
		'# of Enrollments Persisting.2': '13_pers', 'Persistence Pct.2': '13_pers_p', 
		'Graduates.4': '12_grads', 'Enrollments.4': '12_en', 'Enrollment Pct.4': '12_enp', 
		'# of Enrollments Persisting.3': '12_pers', 'Persistence Pct.3': '12_pers_p', 
		'Graduates.5': '11_grads', 'Enrollments.5': '11_en', 'Enrollment Pct.5': '11_enp', 
		'# of Enrollments Persisting.4': '11_pers', 'Persistence Pct.4': '11_pers_p', 
		'Graduates.6': '10_grads', 'Enrollments.6': '10_en', 'Enrollment Pct.6': '10_enp', 
		'# of Enrollments Persisting.5': '10_pers', 'Persistence Pct.5': '10_pers_p'}, inplace=True)
	df.index.names = ['ID']

	# drop a row if the school has "Closed" status
	df = df[df.status != "Closed"]
	
	# # drop irrelevant columns
	df.drop(['status', '16_grads', '16_en', '16_enp', '15_grads', '15_en',
       '15_pers', '14_grads', '14_en', '14_pers', '13_grads', '13_en', 
       '13_pers', '12_grads', '12_en', '12_pers', '11_grads', '11_en', 
       '11_pers', '10_grads', '10_en', '10_pers'], axis=1, inplace=True)

	# replace '*' and NaNs with -1.0
	df.replace(to_replace='*', value= -1.0, inplace=True)
	df.fillna(value = -1.0, inplace=True)

	# create empty_count column
	df['empty_count'] = 0.0

	# get missing cell counts for each row and push into empty_count col
	l = []
	for row in df.iterrows():
		counter = 0
		for i in row[1][1:]:
			if i == -1.0:
				counter += 1
		l.append(counter)
	se = pd.Series(l)
	df['empty_count'] = se.values

	# keep schools that had 4 or fewer missing cells (184 -> 104)
	df = df[df['empty_count'] <= 4]

	# calculate the mean enrollment and persistence rates
	df.replace(-1.0, np.nan, inplace=True)
	df['enroll_avg'] = df[['15_enp', '14_enp', '13_enp', '12_enp','11_enp', '10_enp']].mean(axis=1)
	df['persis_avg'] = df[['15_pers_p', '14_pers_p', '13_pers_p', '12_pers_p', '11_pers_p', '10_pers_p']].mean(axis=1)

	# impute the missing enrollment & persistence rates 
	df['15_enp'].fillna(df['enroll_avg'], inplace=True)
	df['14_enp'].fillna(df['enroll_avg'], inplace=True)
	df['13_enp'].fillna(df['enroll_avg'], inplace=True)	
	df['12_enp'].fillna(df['enroll_avg'], inplace=True)
	df['11_enp'].fillna(df['enroll_avg'], inplace=True)
	df['10_enp'].fillna(df['enroll_avg'], inplace=True)
	df['15_pers_p'].fillna(df['persis_avg'], inplace=True)
	df['14_pers_p'].fillna(df['persis_avg'], inplace=True)
	df['13_pers_p'].fillna(df['persis_avg'], inplace=True)
	df['12_pers_p'].fillna(df['persis_avg'], inplace=True)
	df['11_pers_p'].fillna(df['persis_avg'], inplace=True)
	df['10_pers_p'].fillna(df['persis_avg'], inplace=True)

	return df


def import_student_sped_ell(filename):
	"""
	This function takes an excel file of counts on student SPED, ELL, and 
	Free/Reduced Lunch populations at each school and
	returns a cleaned pandas dataframe w/ columns renamed.

	Input:
		- filename: a string name of the excel file
	Output:
		- df: a pandas dataframe
	"""
	df = pd.read_excel(filename, skiprows=1, sheetname='Schools', 
		usecols=[1,2,4,5,6,7,8,9])
	df.drop([0,661,662,663], inplace=True)
	df.set_index('School ID', inplace=True)
	df.rename(index=int, columns={'School Name': 'school', 'N': 'ell_n', '%': 'ell_p',
		'N.1': 'sped_n', '%.1': 'sped_p', 'N.2': 'lunch_n', '%.2': 'lunch_p'}, inplace=True)
	df.index.names = ['ID']
	
	# drop the rows where any of the elements are nan
	df.dropna(axis=0, how='any')

	return df

def import_student_race(filename):
	"""
	This function takes an excel file of counts on student race
	populations at each school and returns a cleaned pandas 
	dataframe w/ columns renamed.

	Input:
		- filename: a string name of the excel file
	Output:
		- df: a pandas dataframe
	"""
	df = pd.read_excel(filename, skiprows=1, sheetname='Schools', 
		usecols=[0,1,5,7,11,13,15,17,19,21])
	df.drop([0], inplace=True)
	df.set_index('School ID', inplace=True)
	df.rename(index=int, columns={'School Name': 'school', 'Pct': 'white', 'Pct.1': 'black',
		'Pct.3': 'nat_am_alsk', 'Pct.4': 'hispanic', 'Pct.5': 'multi', 'Pct.6': 'asian',
		'Pct.7': 'hi_pi', 'Pct.8': 'unknown'}, inplace=True)
	df.index.names = ['ID']

	# drop the rows where any of the elements are nan
	df.dropna(axis=0, how='any')

	return df

