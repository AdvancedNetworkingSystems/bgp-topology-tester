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


def gen_graph(arg):
    x, r, t, gr = arg
    for i in range(r):
        start_time = dati.now()
        g = nx.internet_as_graph(x)
        gr[x].append(g)
        end_time = dati.now()
        t[x].append((end_time-start_time).total_seconds())


def print_res(times):
    padding = 20
    print("size".ljust(padding), "average time (s)".ljust(padding),
          "std dev (s)".ljust(padding), "human readable".ljust(padding))
    for x in times:
        human_r = str(datetime.timedelta(seconds=sum(times[x])/len(times[x])))
        print(str(x).ljust(padding),
              str(round(statistics.mean(times[x]), 5)).ljust(padding),
              str(round(statistics.stdev(times[x]), 5)).ljust(padding),
              human_r.ljust(padding))


args = parse_args()
m = Manager()
times = m.dict()
graphs = m.dict()

for x in range(args.s, args.e+1, args.d):
    times[x] = m.list()
    graphs[x] = m.list()
 
args_list = [[x, args.r, times, graphs] for x in
             range(args.s, args.e+1, args.d)]
pool = Pool(args.p)
pool.map(gen_graph, args_list)
print_res(times)

if args.S:
    for x in graphs:
        for g in graphs[x]:
            nx.write_graphml(g, "%s/internet-AS-graph-%d-%d.graphml" % (
                args.S, x, int(random.random()*10000)))
