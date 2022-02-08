#!/usr/bin/env python3

# This script walks through a pandoc-generated rst file and improves its
# formatting to fix:
#
# Headings 
#  - First level headings are underlined with '='.
#  - Second level headings are underlined with '~'.
#  - Replace the top-level NAME heading with the name of the man page.
#
# Cross References
#  - Put list of labels from all files into a dictionary, then turn MPI_*
#    and shmem_* into cross reference labels if in that dictionary and 
#    not in a literal section:
#        :ref:`my-reference-label`:
#
# Special sections (code blocks, parameter lists)
#  - Put parameters are on a single line: * ``parameter``:  description
#  - Prefix code blocks with:
#      .. code-block:: [LANGUAGE]
#         :linenos:
#  - Leave other verbatim blocks alone.
#  - Combine bullet items into a single line
#
# See Also
#  - Convert existing "SEE ALSO" sections into ".. :seealso::" 
#  - Note that some SEE ALSO sections still require hand-editing.

import re
import sys
import os
from pathlib import Path

APPNAME=os.path.basename(__file__)
DIRNAME=os.path.dirname(__file__)
ALLREFSFILE=DIRNAME + "/allrefs.txt"

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

# Populate list of all labels 
with open(ALLREFSFILE) as fp:
    allrefs_list = [line.rstrip('\n') for line in fp]

# if current file's CMDNAME is not in list, print out warning
if not CMDNAME.lower() in allrefs_list:
  print("WARNING: {} not in allrefs_list\n".format(CMDNAME.lower()))

# Add a reference for each file to enable cross-references
refline=".. _{}:\n".format(CMDNAME.lower())
output_lines.append(refline)
output_lines.append("")

output_lines.append(f"{CMDNAME}\n{re.sub('[A-Z,a-z,0-9,_,-, ]','=',CMDNAME)}")
output_lines.append("\n.. include_body\n")

# Read input as an array of lines
with open(in_fname) as fp:
    in_lines = fp.readlines()

# PATTERNS
# include file
include_pat = re.compile("\.\. include::")
SYNOPSIS_pat = re.compile("^SYNOPSIS")

# delimiter line (occurs after the heading text)
dline=re.compile("^[=]+")
d2line=re.compile("^[-]+")

# listitem
listitem_pat=re.compile("^[-\*] .*")

# name
name=re.compile("^name$", flags = re.IGNORECASE | re.MULTILINE)

# break out of a literal
# This is an over-simplification because really a literal block
# breaks when we return to the previous indentation level.
unliteral=re.compile("^[A-Za-z]")

# bullet item
bullet=re.compile("^[\s]*[^*]\- ")

# distinguish MPI_Cmd from MPI_ARG
contains_lowercase=re.compile(".*[a-z]")

# Indicates parameters in body
paramsect=re.compile(".*PARAMETER")

# includes ':'
contains_colon=re.compile(".*:")

# find lines that contain the pattern "#include <"
codeblockinclude=re.compile(".*\#include \<")

# codeblock pattern
literalpat=re.compile("^::")

# seealso
seealso = re.compile("^see also$", flags = re.IGNORECASE )
mpicmd = re.compile(".*MPI[_A-Z0-9]", flags = re.IGNORECASE )
mpicmd2 = re.compile(".*MPI", flags = re.IGNORECASE )
shmemcmd = re.compile(".*shmem[_A-Z0-9]", flags = re.IGNORECASE )
shmemcmd2 = re.compile(".*shmem", flags = re.IGNORECASE )
selected = re.compile(".*selected", flags = re.IGNORECASE )
shared = re.compile(".*shared", flags = re.IGNORECASE )
socket = re.compile(".*socket", flags = re.IGNORECASE )
sscanf = re.compile(".*sscanf", flags = re.IGNORECASE )
verbatim = re.compile("::")
dblline = re.compile("========")

# languages
fortran_lang=re.compile(".*Fortran", re.IGNORECASE)
cpp_lang=re.compile(".*C\+\+", re.IGNORECASE)
c_lang=re.compile(".*C[^a-zA-Z]", re.IGNORECASE)

# repl functions
# :ref:`my-reference-label`:
def cmdrepl(match):
    match = match.group()
    match = match.replace('(3)','')
    match = match.replace('(2)','')
    match = match.replace('(1)','')
    match = match.replace('`','')
    match = match.replace('*','')
    if match.lower() in allrefs_list:
        return (':ref:`' + match + '`')
    else:
        return (match)

def seealso_repl(match):
    thecmd = match.group(1)
    thecmd = thecmd.replace('`','')
    thecmd = thecmd.replace('*','')
    if thecmd.lower() in allrefs_list:
        return (':ref:`' + thecmd + '` ')
    else:
        return (match)

# for labeling codeblocks
LANGUAGE="FOOBAR_ERROR"

# We only need to detect languages that ompi supports
# Just pick the first match.
def get_cb_language(aline):
    #LANG="FOOBAR_ERROR: " + aline
    LANG=""
    if fortran_lang.match(aline):
      LANG="fortran" 
    elif cpp_lang.match(aline):
      LANG="c++" 
    elif c_lang.match(aline):
      LANG="c" 
    return(LANG)

# for keeping track of state
BULLETITEM=False
LITERAL=False
INCODEBLOCK=False
INCODEBLOCKINCLUDE = False
INSYNOPSIS = False
PARAM=False
SEEALSO=False
INDENT=""
seealsolist=""

# So we don't repeat combined or replaced lines
SKIP=0

# Walk through all the lines, working on a section at a time
# Leave LITERAL sections alone.
# In PARAMETER sections, combine bullets into a single line.
# If not a LITERAL section, list MPI commands as a reference:
# :ref:`my-reference-label`:
# If a code-block section, add notation.
for i in range(len(in_lines)):
  curline = in_lines[i].rstrip()
  if unliteral.match(curline):
    LITERAL=False
    INCODEBLOCK=False
  if (i > 0):
    prevline = in_lines[i-1].rstrip()
  if (i == len(in_lines) - 1):
    if ((not include_pat.match(curline)) and (not LITERAL)):
      curline = re.sub(r'[\*]*[\`]*MPI_[A-Z][\*,()\[\]0-9A-Za-z_]*[()\[\]0-9A-Za-z_]*[\`]*[\*]*',cmdrepl,curline)
      curline = re.sub(r'[\*]*[\`]*shmem_[A-Z][\*,()\[\]0-9A-Za-z_]*[()\[\]0-9A-Za-z_]*[\`]*[\*]*',cmdrepl,curline)
    if (not SKIP):
      output_lines.append(f"{INDENT}{curline}".rstrip())
  else:
    nextline = in_lines[i+1].rstrip()
    if (i + 3 < len(in_lines)):
      nextnextnextline = in_lines[i+3].rstrip()
    else:
      nextnextnextline = ""
    if dline.match(nextline):
      LITERAL=False
      INCODEBLOCK=False
      PARAM=False
      SKIP+=1
      if (SYNOPSIS_pat.match(curline)):
        INSYNOPSIS = True
      else:
        INSYNOPSIS = False

      if seealso.match(curline):
         output_lines.append('\n.. seealso::')
         SEEALSO=True
         INDENT="   "
         SKIP += 1
      # output from seealso to eof with indentation
      elif paramsect.match(curline):
        PARAM=True
        output_lines.append(f"\n{curline}\n{re.sub('[A-Z,a-z,0-9,_,-, ]','-',curline)}".rstrip())
      elif (curline.isupper()):
        if (name.match(curline)):
          SKIP+=1
        else:
          # level 0 heading
          output_lines.append(f"\n{curline}\n{re.sub('[A-Z,a-z,0-9,_,-, ]','-',curline)}".rstrip())
      else:
          # level 2 heading
          output_lines.append(f"\n{curline}\n{re.sub('=','^',nextline)}".rstrip())
    elif (literalpat.match(curline)):
          LITERAL=True
          prevlangline=prevline
          nextlangline=nextline
          d=1
          while (not prevlangline) or dline.match(prevlangline):
            prevlangline = in_lines[i-d].rstrip()
            curlangline = in_lines[i-d+1].rstrip()
            d += 1
          LANGUAGE = get_cb_language(prevlangline)
          if (not LANGUAGE):
            if not dline.match(nextnextnextline):
              output_lines.append(f"{INDENT}{curline}".rstrip())
          else:
            # output_lines.append(f".. code-block:: {LANGUAGE}\n   :linenos:\n")
            output_lines.append(f".. code-block:: {LANGUAGE}\n")
            INCODEBLOCK = True
            SKIP+=1
    elif listitem_pat.match(curline):
      d=1
      nextpline=in_lines[i+d].rstrip()
      while nextpline and (not listitem_pat.match(nextline)):
        curline=curline + " " + nextpline.rstrip()
        d += 1
        nextpline=in_lines[i+d].rstrip()
        SKIP += 1
      output_lines.append("{INDENT}{curline}")
    else:
      if (SKIP == 0):
        if LITERAL:
          if INCODEBLOCK:
            if INSYNOPSIS:
              curline = re.sub(';','',curline)
            if codeblockinclude.match(curline):
              INCODEBLOCKINCLUDE = True
              output_lines.append(f"{curline}".rstrip())
            else:
              if INCODEBLOCKINCLUDE:
                INCODEBLOCKINCLUDE = False
                if (curline.rstrip() != ""):
                  output_lines.append("")
              output_lines.append(f"{curline}".rstrip())
          else:
              output_lines.append(f"{curline}".rstrip())
        elif PARAM:
          # combine into parameter bullet-item (Note: check if multiline param)
# double check this
          # if not curline:
          #   output_lines.append(f"{curline}".rstrip()) 
          # else:
          if curline:
            paramline2=""
            paramline1 = re.sub('^[ ]*','',curline)
            if (contains_colon.match(curline)):
              paramline1,paramline2 = re.split(r':',paramline1)
            if not paramline2:
              paramline2 = re.sub('^[ ]*','',nextline)
              SKIP+=1
            d=1
            nextpline=in_lines[i+d].rstrip()
            while (nextpline):
              d += 1
              nextpline=in_lines[i+d].rstrip()
              paramline2 += ' ' + re.sub('^[ ]*','',nextpline)
              SKIP += 1
            output_lines.append(f"* ``{paramline1}``: {paramline2}\n".rstrip())
              # e.g., turn **MPI_Abort** and *MPI_Abort* into ``MPI_Abort``
        elif ((not LITERAL) and (not dline.match(nextline))):
          curline = re.sub(r'[\*]*[\`]*MPI_[A-Z][\*,()\[\]0-9A-Za-z_]*[()\[\]0-9A-Za-z_][\`]*[\*]*',cmdrepl,curline)
          curline = re.sub(r'[\*]*[\`]*shmem_[A-Za-z][\*,()\[\]0-9A-Za-z_]*[()\[\]0-9A-Za-z_][\`]*[\*]*',cmdrepl,curline)
          if bullet.match(curline):
            d=1
            nextbline=in_lines[i+d].rstrip()
            bline2 = nextline
            while (nextbline):
              d += 1
              nextbline=in_lines[i+d].rstrip()
              bline2 += ' ' + re.sub('^[ ]*','',nextbline)
              SKIP += 1
            output_lines.append(f"{INDENT}{curline} {bline2}\n".rstrip())
          else:
            output_lines.append(f"{INDENT}{curline}".rstrip())
      else: 
        SKIP-=1

if (out_fname):
  with open(out_fname,'w') as outfile:
    sys.stdout = outfile
    for line in output_lines:
      print(line) 
else:
    for line in output_lines:
      print(line) 
