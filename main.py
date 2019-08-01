#! /usr/bin/env python
import networkx as nx
from datetime import datetime as dati
import datetime
import dateutil.relativedelta
import argparse
from collections import defaultdict
import statistics
from multiprocessing import Pool, Manager
import random
import sys


def parse_args():
    p = argparse.ArgumentParser()
    p.add_argument("-s", help="starting number of nodes", default=100,
                   type=int)
    p.add_argument("-e", help="ending number of nodes", default=1000, type=int)
    p.add_argument("-d", help="delta from one test to the other", default=100,
                   type=int)
    p.add_argument("-r", help="runs per size", default=10, type=int)
    p.add_argument("-p", help="processes", default=1, type=int)
    p.add_argument("-S", help="save the generated graph", default='',
            type=str, nargs='?', const='/tmp')
    args = p.parse_args()
    return args


def gen_graph(x):
    start_time = dati.now()
    g = nx.internet_as_graph(x)
    end_time = dati.now()
    return x, g, (end_time-start_time).total_seconds()


def print_res(times, runs):
    padding = 20
    if not times:
        print("size".ljust(padding), "average time (s)".ljust(padding),
              "std dev (s)".ljust(padding), "human readable".ljust(padding))
        return
    for x in times:
        if len(times[x]) == runs and x not in printed_res:
            human_r = str(datetime.timedelta(seconds=sum(times[x])/len(times[x])))
            print(str(x).ljust(padding),
                  str(round(statistics.mean(times[x]), 5)).ljust(padding),
                  str(round(statistics.stdev(times[x]), 5)).ljust(padding),
                  human_r.ljust(padding))
            printed_res.add(x)
    sys.stdout.flush()


args = parse_args()
times = defaultdict(list)
graphs = defaultdict(list)
printed_res = set()


arg_list = []
for x in range(args.s, args.e+1, args.d):
    arg_list += [x]*args.r
pool = Pool(args.p)
print_res(times, args.r)
for x, g, t in pool.imap_unordered(gen_graph, arg_list):
    times[x].append(t)
    graphs[x].append(g)
    print_res(times, args.r)
    if args.S:
        nx.write_graphml(g, "%s/internet-AS-graph-%d-%d.graphml" % (
                    args.S, x, len(graphs[x])))
