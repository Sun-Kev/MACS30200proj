# Author: Kevin Sun
# Date of last edit: Wednesday, April 25, 2018

import pandas as pd 
import numpy as np 
from pandas import ExcelWriter
from pandas import ExcelFile

TEACHERS = "teacher_positions_12312017.xls"
RETENTION = "retention_rates.xls"
STDNT_RACE = "demo_stdnt_race_2018.xls"
STDNT_SPED_ELL_T1 = "demo_sped_ell_lunch_2018.xls"

def import_teachers(filename):
	"""
	This function takes an excel file of teacher salaries and 
	returns a cleaned pandas dataframe w/ columns renamed.

	Input:
		- filename: a string name of the excel file
	Output:
		- df: a pandas dataframe with school and teacher name cols
	"""
	df = pd.read_excel(filename, sheetname='Export Worksheet', 
		usecols=[0,2,10])
	df.set_index('Pos #', inplace=True)
	df = df.rename(index=int, columns={'Department': 'school', 'Name': 'teacher'})
	df.index.names = ['ID']
	
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
	df = pd.read_excel(filename, skiprows=1, sheetname="CollegeEnrollPersist_2017_sch")
	df.set_index('School ID', inplace=True)
	df = df.rename(index=int, columns={'School Name': 'school', 'Status as of 2017': 'status',
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
		'# of Enrollments Persisting.5': '10_pers', 'Persistence Pct.5': '10_pers_p',})
	df.index.names = ['ID']

	# drop a row if the school has "Closed" status
	df[df.status != "Closed"]
	
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
	df = df.rename(index=int, columns={'School Name': 'school', 'N': 'ell_n', '%': 'ell_p',
		'N.1': 'sped_n', '%.1': 'sped_p', 'N.2': 'lunch_n', '%.2': 'lunch_p'})
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
	df = df.rename(index=int, columns={'School Name': 'school', 'Pct': 'white', 'Pct.1': 'black',
		'Pct.3': 'nat_am_alsk', 'Pct.4': 'hispanic', 'Pct.5': 'multi', 'Pct.6': 'asian',
		'Pct.7': 'hi_pi', 'Pct.8': 'unknown'})
	df.index.names = ['ID']

	# drop the rows where any of the elements are nan
	df.dropna(axis=0, how='any')

	return df

