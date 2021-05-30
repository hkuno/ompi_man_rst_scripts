#!/usr/bin/env python3

# This script walks through a man output file (e.g., man ./foobar > output),
# and extracts just the text following a line beginning with "See also"
#
import re
import sys
import os
from pathlib import Path

APPNAME=os.path.basename(__file__)
DIRNAME=os.path.dirname(__file__)

def usage():
    print(f"{APPNAME} <input_file> [<output_file>]\n")

# Get input and optional output files
in_fname = sys.argv[1]
CMDNAME = os.path.basename(in_fname).rsplit('.',100)[0]
PARENTPATH = os.path.dirname(in_fname)

out_fname=""
if (len(sys.argv) > 2):
    out_fname=sys.argv[2]

output_lines = list()

# Read input as an array of lines
with open(in_fname) as fp:
    in_lines = fp.readlines()

# seealso
seealso = re.compile("[ ]*see also", flags = re.IGNORECASE )

SEEALSO=False
seealsolist=""

# Walk through all the lines, looking for "see also". 
# Output all lines after "See Also"

for i in range(len(in_lines)):
  curline = in_lines[i].rstrip()
  curline = curline.lstrip()
  if seealso.match(curline):
    SEEALSO=True

  if SEEALSO:
    output_lines.append(curline)

if (out_fname):
  with open(out_fname,'w') as outfile:
    sys.stdout = outfile
    for line in output_lines:
      
      print(line) 
else:
    for line in output_lines:
      print(line) 
