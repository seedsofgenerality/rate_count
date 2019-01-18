#!/usr/bin/env python
# Copyright (c) 2019 Christopher Lewis Marshall
# file_summary: inserts fixed text values listed column numbers
# for example:
#    col_add.py 0,abc 5,def

import sys

col= []
text= []
for arg in sys.argv[1:]:
   l= arg.split(',')
   col.append(int(l[0]))
   text.append(l[1])
col.append(-1)

line= sys.stdin.readline().rstrip()
while line!="":
   j= 0
   l_in= line.split(',')
   l_out= []
   for i in range(0,len(l_in)):
      while i==col[j]:
         l_out.append(text[j])
         if j<len(col):
            j+= 1
      l_out.append(l_in[i])
   if col[j]==len(l_in):
      l_out.append(text[j])
   sys.stdout.write(",".join(l_out)+"\n")
   line= sys.stdin.readline().rstrip()
