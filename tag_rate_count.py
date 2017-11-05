#!/usr/bin/python
# Copyright (c) 2017 Christopher Lewis Marshall
# file_summary: stdin->stdout filter demonstrating binning of time series data.  Counts tagged time series data, aggregates values over bin_size, and writes out tagged, binned data.
# input parameters:
#    bin_size
# input and output lines look like this:
#   tag1,tag2,...,tagn,time,value
# where time and value are floating point numbers
#
# FIXME: add an option to set starting time so you can force reporting from a known starting point.  You won't be able to test this until you also implement an initial list of tags.
# FIXME: add an option to force reporting on known list of tags

import sys
import math
import optparse
field_sep=","
key_sep=","

def make_key(*args):
   l= len(args)
   if (l==1):
      return args[0]
   s= str(args[0])
   for i in range(1,l):
      s+= "/"+str(args[i])
   return s   

class tag_line:
   class parse_error(Exception):
      def __init__(self,msg):
         Exception.__init__(self,msg)
         
   def __init__(self,line):
      l= line.split(field_sep)
      self.tag= make_key(*(l[0:-2]))
      self.time= float(l[-2])
      try :
         self.value= float(l[-1])
      except ValueError:
         raise self.parse_error("Couldn't parse line:"+line)

class tag_line_long(tag_line):
   def __init__(self,line):
      l= line.split(field_sep)
      self.tag= make_key(*(l[0:-6]))
      self.time= float(l[-6])
      try :
         self.sum= float(l[-5])
         self.count= float(l[-4])
         self.avg= float(l[-3])
         self.min= float(l[-2])
         self.max= float(l[-1])
      except ValueError:
         raise self.parse_error("Couldn't parse line:"+line)

class tag_counter:
   def __init__(self,tag):
      self.tag= tag
      self.count= 0
      self.sum= 0
      self.min= 0
      self.max= 0
      self.first_value= True

   def add(self,tl):
      if hasattr(tl,"sum"):
         return self.__add_long__(tl)

      if self.first_value:
         self.min= tl.value
         self.max= tl.value
         self.sum+= tl.value
         self.count= 1
         self.first_value= False
      else:
         self.min= min(self.min, tl.value)
         self.max= max(self.max, tl.value)
         self.sum+= tl.value
         self.count+= 1

   def __add_long__(self,tl):
      if self.first_value:
         self.min= tl.min
         self.max= tl.max
         self.sum+= tl.sum
         self.count= tl.count
         self.first_value= False
      else:
         self.min= min(self.min, tl.min)
         self.max= max(self.max, tl.max)
         self.sum+= tl.sum
         self.count+= tl.count

   def report(self,btime,long_report):
      if long_report:
         if self.count>0:
            avg=self.sum/self.count
         else:
            avg= 0
         s= field_sep.join([
            self.tag, btime, str(self.sum),
            str(self.count), str(avg), str(self.min), str(self.max)
         ])
      else:
         s= field_sep.join([
            self.tag, btime, str(self.sum)
         ])
      self.count= 0
      self.sum= 0
      self.first_value= True
      self.min= 0
      self.max= 0
      return s

class tag_rate_counter:
   def __init__(self,bin_size,long_input,long_report,zero_fill,start_time,infile,outfile):
      self.bin_size= bin_size
      if long_input:
         self.tag_line= tag_line_long
      else :
         self.tag_line= tag_line
      self.long_report= long_report
      self.zero_fill= zero_fill
      self.start_time= start_time
      self.infile= infile
      self.outfile= outfile
      self.tag_counter_table= {}
   def process_line(self,line):
      tl= self.tag_line(line)
      if self.tag_counter_table.has_key(tl.tag):
         counter= self.tag_counter_table[tl.tag]
      else :
         counter= tag_counter(tl.tag)
         self.tag_table[tl.tag]= counter
      tl.add(tl)
   def report(self,btime):
      tags= self.tag_counter_table.keys()
      tags.sort()
      for tag in tags:
         self.outfile.write(self.tag_counter_table[tag].report(btime, self.long_report)+"\n")
   def run(self):
      line= self.infile.readline()
      tl= self.tag_line(line)
      if self.start_time:
         last_bin= math.floor(self.start_time/self.bin_size)
      else:
         last_bin= math.floor(tl.time/self.bin_size)
      while line!="":
         try :
            tl= self.tag_line(line)
            bin= math.floor(tl.time/self.bin_size)
         
            if bin==last_bin:
               pass
            elif bin<last_bin:
               bin= last_bin
            else :
               btime= str(last_bin*self.bin_size)
               self.report(btime)
               if self.zero_fill:
                  while last_bin<bin:
                     last_bin+= 1
                     if last_bin<bin:
                        btime= str(last_bin*self.bin_size)
                        self.report(btime)
         
            if self.tag_counter_table.has_key(tl.tag):
               counter= self.tag_counter_table[tl.tag]
            else :
               counter= tag_counter(tl.tag)
               self.tag_counter_table[tl.tag]= counter
            counter.add(tl)

         except self.tag_line.parse_error,e:
            sys.stderr.write(str(e))
      
         last_bin= bin
         line= self.infile.readline()

      # make final report
      btime= str(last_bin*self.bin_size)
      self.report(btime)

usage="""%prog tag_rate_count.py [options]
   input and output line format
      <tag1>,...<tagn>,time,value"""

parser= optparse.OptionParser(usage=usage)
parser.add_option(
   "-b","--bin-size",type="float",dest="bin_size",
   help="the size of the bins used to aggregate the value column"
)
parser.add_option(
   "-I","--long-input",action="store_true",dest="long_input",
   help="input lines in the form: tag,...,tag,time,sum,count,avg,min,max"
)
parser.add_option(
   "-l","--long-report",action="store_true",dest="long_report",
   help="output lines in the form: tag,...,tag,time,sum,count,avg,min,max"
)
parser.add_option(
   "--zero-fill",action="store_true",dest="zero_fill",
   help="fill in time gaps with empty reports"
)
parser.add_option(
   "--start-time",type="float",dest="start_time",
   help="the time from which to start reporting"
)
options,args= parser.parse_args()

if not options.bin_size:
   parser.error("you need to specify a bin size")

trc= tag_rate_counter(
   options.bin_size,
   options.long_input,
   options.long_report,
   options.zero_fill,
   options.start_time,
   sys.stdin,
   sys.stdout
)
trc.run()
