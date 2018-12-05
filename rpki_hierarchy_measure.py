import csv, random, radix, os
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from netaddr import *

SMALL_SIZE = 24
MEDIUM_SIZE = 48
BIGGER_SIZE = 56
BIGGEST_SIZE = 112

plt.rc('font', size=BIGGER_SIZE)         # controls default text sizes
plt.rc('axes', titlesize=BIGGER_SIZE)     # fontsize of the axes title
plt.rc('axes', labelsize=BIGGER_SIZE)    # fontsize of the x and y labels
plt.rc('xtick', labelsize=MEDIUM_SIZE)    # fontsize of the tick labels
plt.rc('ytick', labelsize=BIGGER_SIZE)    # fontsize of the tick labels
plt.rc('legend', fontsize=BIGGER_SIZE)    # legend fontsize
plt.rc('figure', titlesize=BIGGEST_SIZE)  # fontsize of the figure title

# https://netaddr.readthedocs.io/en/latest/tutorial_03.html
# https://pypi.org/project/py-radix/
# https://stuffivelearned.org/doku.php?id=programming:python:pyradix_search_all_patch

def read_ip_ranges_into_radix(file_to_read):
    """
    Parameters:
        file_to_read: CSV containing all ROAs for a given date

    Output: 
        rtree: a radix tree containing all ROAs 
        num_duplicates: a count of the number of duplicate ROAs in the input data
        num_overlaps: a count of the number of IP address blocks with authentication from multiple ASes
    """
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


def count_hierarchy(day, ip_address_tree, num_duplicates, num_overlaps):
    """
    Parameters:
        day: String indicating a given date
        ip_address_tree: Radix tree of all ROAs
        num_duplicates: a count of the number of duplicate ROAs in the input data
        num_overlaps: a count of the number of IP address blocks with authentication from multiple ASes

    Output: 
        none. Prints information about the radix tree 
    """
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


def compare_radix_trees(tree1, tree2):
    """
    Parameters:
        tree1: a radix tree of IP addresses 
        tree2: a radix tree of IP addresses 

    Output: 
        added_prefixes: prefixes in tree2, not present in tree1
        removed_prefixes: prefixes not present in tree2, present in tree1 
    """
    tree1_prefixes = tree1.prefixes()
    tree2_prefixes = tree2.prefixes() 

    added_prefixes = list(set(tree2_prefixes) - set(tree1_prefixes))
    removed_prefixes = list(set(tree1_prefixes) - set(tree2_prefixes))
    return (added_prefixes, removed_prefixes)


def write_ROA_churn_to_graph(all_trees):
    """
    Parameters: 
        all_trees: a list of tuples of the form (date, radix tree of ROAs from that date) 
    
    Create a graph of change in the number of ROAs over time  
    """
    date_of_entries = []
    added_prefixes_over_time = []
    removed_prefixes_over_time = []
    for i in range(0, len(all_trees)): 
        date_of_entries.append(all_trees[i][0][0:10])
        if "2018-11-06" in all_trees[i][0][0:10]: 
            added_prefixes_over_time.append(None)
            removed_prefixes_over_time.append(None)
        elif "2018-11-13" in all_trees[i][0][0:10]:
            added_prefixes_over_time.append(None)
            removed_prefixes_over_time.append(None)
        else: 
            added_prefixes, removed_prefixes = compare_radix_trees(all_trees[0][1], all_trees[i][1])
            added_prefixes_over_time.append(len(added_prefixes))
            removed_prefixes_over_time.append(-1 * len(removed_prefixes))

    print added_prefixes_over_time
    print removed_prefixes_over_time


    # Number of ROAs
    plt.xticks(np.arange(0, len(date_of_entries)), date_of_entries, rotation=90)
    
    date_range = np.arange(0, len(date_of_entries))
    # https://stackoverflow.com/questions/14399689/matplotlib-drawing-lines-between-points-ignoring-missing-data
    added_prefixes_series = np.array(added_prefixes_over_time).astype(np.double)
    added_mask = np.isfinite(added_prefixes_series)

    removed_prefixes_series = np.array(removed_prefixes_over_time).astype(np.double)
    removed_mask = np.isfinite(removed_prefixes_series)

    plt.axhline(linewidth=10, color='b')

    plt.plot(date_range[added_mask], added_prefixes_series[added_mask],  linestyle='-', marker='o', label="Added ROAs", linewidth=10, markersize=15)
    plt.plot(date_range[removed_mask], removed_prefixes_series[removed_mask],  linestyle='-', marker='o', label="Removed ROAs", linewidth=10, markersize=15)
    plt.title("ROA Churn: Number of ROA Entries Added or Removed")
    plt.legend(loc="upper left")
    plt.ylim(-1000, 5000)
    plt.show()


def histogram_of_hierarchy_depth(all_trees):
    """
    Parameters: 
        all_trees: a list of tuples of the form (date, radix tree of ROAs from that date) 
    
    Create a graph of hierarchy depth. 
    """
    # 1. combine all radix trees into one 
    combined_radix_tree = all_trees[0][1]
    print combined_radix_tree
    for i in range(0, len(all_trees)): 
        added_prefixes, _ = compare_radix_trees(all_trees[0][1], all_trees[i][1])
        for cidr_address in added_prefixes: 
            tmp = combined_radix_tree.search_exact(cidr_address) 
            if tmp: 
                as_list = all_trees[i][1].search_exact(cidr_address).data["issuing_as"]
                tmp.data["issuing_as"].append(as_list)
            else: 
                rnode = combined_radix_tree.add(cidr_address)
                as_list = all_trees[i][1].search_exact(cidr_address).data["issuing_as"]
                rnode.data["issuing_as"] = as_list
        #combined_radix_tree = associate_prefixes_and_issuing_ases(added_prefixes, all_trees[i][1], combined_radix_tree)


    # 2. for each node in the tree, see how many parents and grandparents nodes cover it
    # 3. for those nodes, find their issuing ASes
    number_covering_nodes = []
    number_covering_roas = []
    for node in combined_radix_tree.nodes():
        set_of_covering_ases = set()
        # get all parent nodes, including self
        hierarchy = combined_radix_tree.search_covering(node.prefix)
        for entry in hierarchy: 
            print entry.data["issuing_as"]
            for as_issuer in entry.data["issuing_as"]:
                set_of_covering_ases.add(as_issuer)
            print set_of_covering_ases
        #if len(set_of_covering_ases) > 1: 
        number_covering_nodes.append(len(set_of_covering_ases))
        number_covering_roas.append(len(hierarchy))

    # 4. graph that (by # ASes with revocation rights)
    plt.xticks(np.arange(0, 11))
    plt.title("Hierarchy of the RPKI: Number of ASes with Revocation Rights Per ROA")
    sns.distplot(number_covering_nodes, bins=10, kde=False, label="Number of parent ASes with revocation rights")
    plt.xlabel("Number of Parent ASes with Revocation Rights")
    plt.show()

    # 4. graph that (by # Certificates)
    plt.xticks(np.arange(0, 11))
    plt.title("Hierarchy of the RPKI: Number of Certificates with Revocation Rights Per ROA")
    sns.distplot(number_covering_roas, bins=10, kde=False, label="IP space owners with revocation rights")
    plt.xlabel("Number of Certificates with Revocation Rights")
    plt.show()

def anomaly_evaluation(all_trees):
    """
    A bunch of ROAs are removed on 11-09 and then returned on 11-11. Why?  
    """
    roas_removed_then_added = []
    set_of_roas = set()
    new_roas = []
    for i in range(0, len(all_trees)): 
        if  "11-09" in all_trees[i][0]: 
            added_prefixes, removed_prefixes = compare_radix_trees(all_trees[i-1][1], all_trees[i][1])
            print "REMOVED ROAs 11-08 to 11-09"
            print removed_prefixes
            for prefix in removed_prefixes:
                set_of_roas.add(prefix)
        if "11-11" in all_trees[i][0]:
            added_prefixes, removed_prefixes = compare_radix_trees(all_trees[i-1][1], all_trees[i][1])
            print "ADDED ROAs 11-10 to 11-11"
            print added_prefixes
            for prefix in added_prefixes: 
                try: 
                    set_of_roas.remove(prefix)
                    roas_removed_then_added.append(prefix)
                except: 
                    new_roas.append(prefix)
    print "SET OF CHANGE: " + str(roas_removed_then_added)
    print len(roas_removed_then_added)


def main():
    """
    Main control logic
    Read in each day of ROAs
    Convert from CSV -> radix trees 
    Then, analyze for changes, hierarchy depth, etc. 
    """
    rpki_announcements_per_day = os.listdir('RPKI_announcements/')
    rpki_announcements_per_day.sort()
    radix_trees = []

    # i = 0 
    for day_of_roas in rpki_announcements_per_day: 
        if ".csv" in day_of_roas: 
            all_ip_addresses_tree, num_duplicates, num_overlaps = read_ip_ranges_into_radix('RPKI_announcements/' + day_of_roas)
            count_hierarchy(day_of_roas, all_ip_addresses_tree, num_duplicates, num_overlaps)

            radix_trees.append((day_of_roas, all_ip_addresses_tree))

            # if i >= 1: 
            #     added_prefixes, removed_prefixes = compare_radix_trees(radix_trees[i-1], radix_trees[i])
            #     print "    Added prefixes: " + str(len(added_prefixes))
            #     print "    Removed prefixes: " + str(len(removed_prefixes))

            # i += 1

    write_ROA_churn_to_graph(radix_trees)
    #write_ROA_size_churn_to_graph(radix_trees)
    histogram_of_hierarchy_depth(radix_trees)
    anomaly_evaluation(radix_trees)

if __name__ == "__main__":
    main()
