import csv, random, radix 

print "What??"
# Create a new tree
rtree = radix.Radix()

# Adding a node returns a RadixNode object. You can create
# arbitrary members in its 'data' dict to store your data
rtree.add("0.0.0.0/0")

# You can specify nodes as CIDR addresses, or networks with
# separate mask lengths. The following three invocations are
# identical:
rtree.add("10.0.0.0/16")

# Covered search will return all prefixes inside the given
# search term, as a list (including the search term itself,
# if present in the tree)
print rtree.nodes()
rnodes = rtree.search_covered("10.123.0.0/16")
print rnodes