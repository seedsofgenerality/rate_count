#!/usr/bin/env python
# Copyright (c) 2019 Christopher Lewis Marshall
# file_summary: unlike the standard unit cut, this allows you to re-order columns.

import sys

class cutter:
   def __init__(self,delim,columns):
      self.delim= delim
      self.columns= columns
   def process_line(self,line):
      ls= line.split(self.delim)
      l= []
      for j in self.columns:
         l.append(ls[j])
      return self.delim.join(l)
   def run(self):
      line= sys.stdin.readline()
      while line!="":
         sys.stdout.write(self.process_line(line.strip())+"\n")
         line= sys.stdin.readline()

if len(sys.argv)<3:
   sys.stderr.write("usage: <delimiter> <column> ...\n")
   sys.exit(1)
delim= sys.argv[1]
columns= map(lambda x: x-1, map(int,sys.argv[2:]))
cutter(delim,columns).run()
