"""
cse6242 s21
wrangling.py - utilities to supply data to the templates.

This file contains a pair of functions for retrieving and manipulating data
that will be supplied to the template for generating the table. """
import csv

def username():
    return 'szhao343'

def data_wrangling():
    with open('data/movies.csv', 'r', encoding='utf-8') as f:
        reader = csv.reader(f)
        table = list()
        # Feel free to add any additional variables
        ...
        
        # Read in the header
        for header in reader:
            break
        
        # Read in each row
        for row in reader:
            #print(row[2])
            table.append(row)
            
            # Only read first 100 data rows - [2 points] Q5.a
            table_100 = table[:100]
        
        #table_sorted = table_100.sort(key = lambda row: row[2], reverse = True)# Order table by the last column - [3 points] Q5.b
        table_sorted = sorted(table_100, key = lambda row: float(row[2]), reverse = True)
        #print(len(table_100))
    return header, table_sorted


