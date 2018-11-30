import csv, random, radix, os
from netaddr import *

# https://netaddr.readthedocs.io/en/latest/tutorial_03.html
# https://pypi.org/project/py-radix/
# https://stuffivelearned.org/doku.php?id=programming:python:pyradix_search_all_patch

"""
Parameters:
    file_to_read: CSV containing all ROAs for a given date

Output: 
    rtree: a radix tree containing all ROAs 
    num_duplicates: a count of the number of duplicate ROAs in the input data
    num_overlaps: a count of the number of IP address blocks with authentication from multiple ASes
"""
def read_ip_ranges_into_radix(file_to_read):
    rtree = radix.Radix()
    num_duplicates = 0 
    num_overlaps = 0 

    with open(file_to_read) as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=",")
        next(csv_reader, None)  # skip the headers
        for row in csv_reader:
            cidr_address = row[1]
            # see if the IP address block is already in the tree 
            # if so, the ROA is either duplicate or overlapping 
            # otherwise, add the new IP address block to the tree
            tmp = rtree.search_exact(cidr_address) 
            if tmp: 
                if row[0] in tmp.data["issuing_as"]:
                    num_duplicates += 1
                else:
                    tmp.data["issuing_as"].append(row[0])
                    num_overlaps += 1
            else: 
                rnode = rtree.add(cidr_address)
                rnode.data["issuing_as"] = [row[0]]

    return (rtree, num_duplicates, num_overlaps) 

"""
Parameters:
    day: String indicating a given date
    ip_address_tree: Radix tree of all ROAs
    num_duplicates: a count of the number of duplicate ROAs in the input data
    num_overlaps: a count of the number of IP address blocks with authentication from multiple ASes

Output: 
    none. Prints information about the radix tree 
"""
def count_hierarchy(day, ip_address_tree, num_duplicates, num_overlaps):
    count_number_overlaps = 0
    max_hierarchy_depth = 0
    for node in ip_address_tree.nodes():
        hierarchy = ip_address_tree.search_covering(node.prefix)
        if len(hierarchy) > 1:
            count_number_overlaps += 1
            max_hierarchy_depth = max(max_hierarchy_depth, len(hierarchy))
            # print "\n\n\n"
            # print "Covered node: " + str(node.data["issuing_as"]) + ", " + str(node.prefix)
            # for ipaddr_node in hierarchy:
            #     print ipaddr_node.data["issuing_as"]
            #     print ipaddr_node.prefix

    print "Data: " + str(day)
    print "    Max heirarchy depth: " + str(max_hierarchy_depth)
    print "    Overlapping addresses: " + str(count_number_overlaps)
    print "    Number of duplicate ROAs: " + str(num_duplicates)
    print "    Number of overlapping ROAs: " + str(num_overlaps)


"""
Parameters:
    tree1: a radix tree of IP addresses 
    tree2: a radix tree of IP addresses 

Output: 
    added_prefixes: prefixes in tree2, not present in tree1
    removed_prefixes: prefixes not present in tree2, present in tree1 
"""
def compare_radix_trees(tree1, tree2):
    tree1_prefixes = tree1.prefixes()
    tree2_prefixes = tree2.prefixes() 

    added_prefixes = list(set(tree2_prefixes) - set(tree1_prefixes))
    removed_prefixes = list(set(tree1_prefixes) - set(tree2_prefixes))
    return (added_prefixes, removed_prefixes)

"""
Main control logic
Read in each day of ROAs
Convert from CSV -> radix trees 
Then, analyze for changes, hierarchy depth, etc. 
"""
def main():
    rpki_announcements_per_day = os.listdir('RPKI_announcements/')
    rpki_announcements_per_day.sort()
    radix_trees = []

    i = 0 
    for day_of_roas in rpki_announcements_per_day: 
        if ".csv" in day_of_roas: 
            all_ip_addresses_tree, num_duplicates, num_overlaps = read_ip_ranges_into_radix('RPKI_announcements/' + day_of_roas)
            count_hierarchy(day_of_roas, all_ip_addresses_tree, num_duplicates, num_overlaps)

            radix_trees.append(all_ip_addresses_tree)

            if i >= 1: 
                added_prefixes, removed_prefixes = compare_radix_trees(radix_trees[i-1], radix_trees[i])
                print "    Added prefixes: " + str(len(added_prefixes))
                print "    Removed prefixes: " + str(len(removed_prefixes))

            i += 1




    # for i in range(0, 1):#len(rpki_announcements_per_day) - 2):
    #     added_prefixes, removed_prefixes = compare_radix_trees(radix_trees[i], radix_trees[i+1])
    #     #print added_prefixes
    #     #print removed_prefixes
    #     print "Added prefixes: " + str(len(added_prefixes))
    #     print "Removed prefixes: " + str(len(removed_prefixes))

if __name__ == "__main__":
    main()
