import urllib2
import numpy as np 
import matplotlib.pyplot as plt
import pandas as pd 
import math

SMALL_SIZE = 24
MEDIUM_SIZE = 24
BIGGER_SIZE = 24

plt.rc('font', size=SMALL_SIZE)          # controls default text sizes
plt.rc('axes', titlesize=SMALL_SIZE)     # fontsize of the axes title
plt.rc('axes', labelsize=MEDIUM_SIZE)    # fontsize of the x and y labels
plt.rc('xtick', labelsize=SMALL_SIZE)    # fontsize of the tick labels
plt.rc('ytick', labelsize=SMALL_SIZE)    # fontsize of the tick labels
plt.rc('legend', fontsize=SMALL_SIZE)    # legend fontsize
plt.rc('figure', titlesize=BIGGER_SIZE)  # fontsize of the figure title


# data pulled from https://rpki-read.realmv6.org/stats
IPV6_ORIGINS_START_STRING = "var data_ipv6_origins = google.visualization.arrayToDataTable(["
IPV6_COVERAGE_START_STRING = "var data_ipv6_coverage = google.visualization.arrayToDataTable(["

IPV4_ORIGINS_START_STRING = "var data_ipv4_origins = google.visualization.arrayToDataTable(["
IPV4_COVERAGE_START_STRING = "var data_ipv4_coverage = google.visualization.arrayToDataTable(["

DATA_END_STRING = "var pc_opts = {"


rpki_read_response = urllib2.urlopen('https://rpki-read.realmv6.org/stats')
rpki_read = rpki_read_response.read()


ipv6_start_position = rpki_read.find(IPV6_ORIGINS_START_STRING) + len(IPV6_ORIGINS_START_STRING)
ipv6_end_data = rpki_read[ipv6_start_position:].find(DATA_END_STRING)
ipv6_end_position = ipv6_start_position + ipv6_end_data
ipv6_data = rpki_read[ipv6_start_position:ipv6_end_position]


ipv4_start_position = rpki_read.find(IPV4_ORIGINS_START_STRING) + len(IPV4_ORIGINS_START_STRING)
ipv4_end_data = rpki_read[ipv4_start_position:].find(DATA_END_STRING)
ipv4_end_position = ipv4_start_position + ipv4_end_data
ipv4_data = rpki_read[ipv4_start_position:ipv4_end_position]


ipv6_coverage = {'valid': 1795875000979046852621075650510863.0, 'invalid_length': 2972967575531301425873887954748.0, 'invalid_as': 6025720332198786685910298656790.0, 'not_found': 516003706925393611947532449399940062802}
#ipv4_coverage = {}
print ipv6_coverage.values()
print ipv6_coverage.keys()

print ipv4_data
ipv4_coverage = {'valid': 487856011, 'invalid_length': 91119887, 'invalid_as': 11312873, 'not_found': 9206798812}

plt.pie(ipv4_coverage.values(), labels=ipv4_coverage.keys())
plt.show()
