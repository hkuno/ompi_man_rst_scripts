#!/usr/bin/env python3

# This script walks through an rst file generated from md and improves its
# formatting. 
#
# Headings 
#  - Replace initial NAME with the name fo the man page.
#  - Leave first level headings underlined with '='.
#  - Leave second level headings underlined with '-'.
#
# Cross References
#  - Turn MPI_* and shmem_* into cross references if not in a literal section.
#  - Add reference labels to rst files:   :ref:`my-reference-label`:
#
# See Also
#  - Convert existing "SEE ALSO" sections into ".. :seealso::" 
#  - Note that some SEE ALSO sections still require hand-editing.

import re
import sys
import os

APPNAME=os.path.basename(__file__)
DIRNAME=os.path.dirname(__file__)

def usage():
    print(f"{APPNAME} <input_file> [<output_file>]\n")

# Get input and optional output files
in_fname = sys.argv[1]
CMDNAME = os.path.basename(in_fname).rsplit('.',100)[0]

# optionally print to output file
out_fname=""
if (len(sys.argv) > 2):
    out_fname=sys.argv[2]

# append to output_lines instead of printing lines
output_lines = list()

# Add a reference for each file
refline=".. _{}:\n".format(CMDNAME)
output_lines.append(refline)

# delimiter line (occurs after the heading text)
dline=re.compile("^[=]+")

# literal
codeblock=re.compile("\.\. .*code::")

# distinguish MPI_Cmd from MPI_ARG
contains_lowercase=re.compile(".*[a-z]")

# name
name=re.compile("^name$", flags=re.IGNORECASE | re.MULTILINE)

# see also
seealso = re.compile("^see also$", flags = re.IGNORECASE )
mpicmd = re.compile(".*MPI[_A-Z0-9]", flags = re.IGNORECASE )
shmemcmd = re.compile(".*shmem[_A-Z0-9]", flags = re.IGNORECASE )

# repl functions
# :ref:`my-reference-label`:
def mpicmdrepl(match):
    match = match.group()
    match = match.replace('`','')
    match = match.replace('*','')
#    if (contains_lowercase.match(match)):
#        seealsodict[match]=match
    return (':ref:`' + match + '` ')

def seealso_repl(match):
    thecmd = match.group(2)
    thecmd = thecmd.replace('`','')
    thecmd = thecmd.replace('*','')
    return (':ref:`' + thecmd + '`')

# Read input as an array of lines
with open(in_fname) as fp:
    in_lines = fp.readlines()

# PATTERNS
# delimiter line (occurs after the heading text)
dline=re.compile("^[=]+")

# So we don't repeat combined or replaced lines
SKIP=0

# keep track of state
LITERAL=True
seealsolist=""

# Walk through all the lines, working on a section at a time
# If the current line contains 'code::' then LITERAL=True 
# If we hit a delimiter, then LITERAL=False
# If LITERAL == False, then add references to all MPI commands. 
for i in range(len(in_lines)):
  curline = in_lines[i].rstrip()
  nextline = curline

  if (i < (len(in_lines) - 1)):
      nextline = in_lines[i+1].rstrip()

  if name.match(curline) and dline.match(nextline):
      # Substitute program name because html index needs it.
      # Only substitute delimeter for the first NAME heading because 
      # build-doc seems to expect a single-rooted hierarchy.
      output_lines.append(f"{CMDNAME}\n{re.sub('[A-Z,a-z,0-9,_,-]','~',CMDNAME)}")
      SKIP += 1
      LITERAL=False
  if seealso.match(curline) and dline.match(nextline):
      SKIP += 2
      LITERAL=False
      SEEALSO=True
      d=1
      seealsoline=""
      while (d+i < len(in_lines)):
        sline=in_lines[i+d].rstrip()
        cmdline=""
        if mpicmd.match(sline):
          cmdline=re.sub(r'([^A-Za-z]*)([Mm][Pp][Ii][^\\ (]*)(.*)',seealso_repl,sline)
        elif shmemcmd.match(sline):
          cmdline=re.sub(r'([^A-Za-z]*)([Ss][Hh][Mm][Ee][Mm][^\\ (]*)(.*)',seealso_repl,sline)
        else: 
          SKIP += 1
        seealsolist=f"{seealsolist}{cmdline}"
        SKIP += 1
        d+=1
      output_lines.append(f'\n.. seealso:: {seealsolist}')
      break

  elif (SKIP == 0):
      if codeblock.match(curline):
        LITERAL=True
      elif dline.match(curline):
        LITERAL=False

      if not LITERAL and curline:
        curline = re.sub(r'[\*]*[\`]*MPI_[A-Z][\*,()\[\]0-9A-Za-z_]*[()\[\]0-9A-Za-z_][\`]*[\*]*',mpicmdrepl,curline)

      output_lines.append(f"{curline}")
  else: 
      SKIP -= 1

#seealso='\n.. seealso::'
#for k, v in seealsodict.items():
#    if ( k != CMDNAME ):
#        seealso=seealso + ' :ref:`' + k + '`'
#
#output_lines.append(seealso)

if (out_fname):
  with open(out_fname,'w') as outfile:
    sys.stdout = outfile
    for line in output_lines:
      print(line) 
else:
    for line in output_lines:
      print(line) 
