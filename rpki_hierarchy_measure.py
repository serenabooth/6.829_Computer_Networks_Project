import csv 
from netaddr import *
import random 
import radix
# https://netaddr.readthedocs.io/en/latest/tutorial_03.html
# https://pypi.org/project/py-radix/

count_overlap_no_hierarchy = 0 

all_roas = []

roas_to_check = []

all_ipaddresses = IPSet()
#with open('RPKI_announcements/2018-11-15_05:08_RPKI_announcements.csv') as csv_file:
with open('test.csv') as csv_file:

    csv_reader = csv.reader(csv_file, delimiter=",")
    next(csv_reader, None)  # skip the headers
    for row in csv_reader:
        if (random.random() < 0.01):
            print row
        ip_intersect = all_ipaddresses & IPSet(IPNetwork(row[1]))
        if ip_intersect != IPSet():
            count_overlap_no_hierarchy += 1 
            roas_to_check.append(IPNetwork(row[1]))
            print roas_to_check
        all_roas.append(IPNetwork(row[1]))
        all_ipaddresses = all_ipaddresses | IPSet(IPNetwork(row[1]))

print roas_to_check


overlapping_roas = []
for entry_1 in roas_to_check:
    overlap_list = [entry_1]
    for entry_2 in all_roas: 
        if entry_1 == entry_2:
            continue 
        elif IPSet(entry_1).issubset(IPSet(entry_2)):
            overlap_list.append(entry_2)
        elif IPSet(entry_1).issuperset(IPSet(entry_2)):
            roas_to_check.append(entry_2)
    if len(overlap_list) > 1:
        overlapping_roas.append(overlap_list)


print overlapping_roas
print count_overlap_no_hierarchy
