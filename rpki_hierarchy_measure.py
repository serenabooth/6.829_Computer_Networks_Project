import csv, random, radix 
from netaddr import *

# https://netaddr.readthedocs.io/en/latest/tutorial_03.html
# https://pypi.org/project/py-radix/
# https://stuffivelearned.org/doku.php?id=programming:python:pyradix_search_all_patch

def read_ip_ranges_into_radix(file_to_read):
    rtree = radix.Radix()

    with open(file_to_read) as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=",")
        next(csv_reader, None)  # skip the headers
        for row in csv_reader:
            cidr_address = row[1]
            rnode = rtree.add(cidr_address)
            rnode.data["issuing_as"] = row[0]
    return rtree

def count_hierarchy(ip_address_tree):
    count_number_overlaps = 0
    max_hierarchy_depth = 0
    for node in ip_address_tree.nodes():
        hierarchy = ip_address_tree.search_covering(node.prefix)
        if len(hierarchy) > 1:
            count_number_overlaps += 1
            max_hierarchy_depth = max(max_hierarchy_depth, len(hierarchy))
            print "\n\n\n"
            print "Covered node: " + str(node.data["issuing_as"]) + ", " + str(node.prefix)
            for ipaddr_node in hierarchy:
                print ipaddr_node.data["issuing_as"]
                print ipaddr_node.prefix

    print max_hierarchy_depth
    print count_number_overlaps


all_ip_addresses_tree = read_ip_ranges_into_radix('RPKI_announcements/2018-10-30_18:38_RPKI_announcements.csv')
count_hierarchy(all_ip_addresses_tree)