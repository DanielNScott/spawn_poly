#! /usr/bin/env python3.3

#=============================================================================================#
# This script is meant to replace the clunky bash script spawn_poly.sh with a more flexible 
# implementation. It takes a joborder.txt file, reads the column headers which should be
# namelist names, then creates polygons and supplies them with ED2IN files as specified by 
# the column values.
#=============================================================================================#
import ed_defs                                     # Simple data structs & routines for dealing
from os.path import isfile                         # with ED2INs and joborder.txt files.

input_file_object  = ed_defs.input_file_object     # Basically a dictionary
copy_anything      = ed_defs.copy_anything         # For copying folders

demolish           = True                          # Callously overwrite old folders?
debugging          = True                          # Want debugging output from this script?
disp_set_opts      = False                         # See which options were found AND SET?
disp_unset_opts    = False                         # See which options were found BUT UNSET?

#---------------------------------------------------------------------------------------------#
#    Get user intput for file locations if they aren't where expected...                      #
#---------------------------------------------------------------------------------------------#
if isfile('./joborder.txt'):
   joborder = input_file_object('./joborder.txt')
else:
   prompt        = 'Please enter the relative path of the joborder file, including filename.\n'
   joborder_path = input(prompt)
   joborder      = input_file_object(joborder_path)
   
if isfile('./template/ED2IN'):
   ED2IN_template = input_file_object('./template/ED2IN')
else:
   prompt         = 'Please enter the relative path of the ED2IN, including filename.\n'
   ED2IN_path     = input(prompt)
   ED2IN_template = input_file_object(ED2IN_path)
#---------------------------------------------------------------------------------------------#


#---------------------------------------------------------------------------------------------#
#    Print a message to inform users about this script                                        #
#---------------------------------------------------------------------------------------------#
print("--------------------------------------------------------------------------------------")
print("NOTICE:")
print("   This script reads a joborder.txt file in which column headers are EXACTLY")
print("those strings following 'NL%' in the ED2IN, and replaces EXACTLY those      ")
print("options in the ED2IN file when generating polygons. If it finds a header    ")
print("with a name that doesn't match anything in the ED2IN it will complain.      ")
print("--------------------------------------------------------------------------------------")
print(" ")
print("[Step Id] (Description) follows:")
#=============================================================================================#


#=============================================================================================#
# Read the joborder file into this python script                                              #
#=============================================================================================#
print("[1.0] Opening joborder file: ",joborder.fname)
if debugging:
   print("!--------------------------------------------------------------------------------------!")
   print("!    Debugging Output: joborder                                                        !")
   print("!--------------------------------------------------------------------------------------!")

with open(joborder.fname, "r", errors="replace") as f:
      searchlines = f.readlines()
      print("[1.1] Open successful, reading options...")
      print(" ")
      
      # Loop through lines
      for lnum, line in enumerate(searchlines):
         
         # Skip lines 0 and 2 which are formatting
         if (lnum in [0,2] ): continue
         
         # Skip lines that have nothing on them.
         if line.strip() == '':
            continue
         
         # Skip lines that are commented out using #
         if line.strip()[0] == '#':
            continue
         
         # Determine model option names from 2nd line. Remove the polygon name.
         if (lnum == 1):
            model_options = line.split()[1:]
            continue
            
         # For every other line, populate dictionary of polygon options.         
         polyname = line.split()[0].strip()
         joborder.create_polygon(polyname)
            
         for option_index, option in enumerate(model_options):
            joborder.polys[polyname].set_opt(option, line.split()[option_index + 1].strip())

if debugging:
   joborder.print()
   print("!--------------------------------------------------------------------------------------!")
   print(" ")
#=============================================================================================#







#=============================================================================================#
# Read the ED2IN option names from the ED2IN file into this script. (AS LOWERCASE)            #
# Also, remember the line numbers these options came from so we can easily replace them.      #
#=============================================================================================#
polyname = 'this'
ED2IN_template.create_polygon(polyname)
print("[Step 2.0] File closed, opening ",ED2IN_template.fname ,"...")

# Open ED2IN and process
with open(ED2IN_template.fname, "r", errors="replace") as f:
      searchlines = f.readlines()
      print("[2.1] Open successful, reading options...")
      print(" ")
      
      # Loop through lines
      for lnum, line in enumerate(searchlines):

         # Discard lines that start with "!" i.e. comments
         if line.strip() == '':
            continue

         if line.strip()[0] == '!':
            continue
         
         # Pull namelist option names out
         if "NL%" in line:
            
            # Read out just the option name and save it with the line number
            line   = line.strip()[3:]
            option = line[:line.index('=')].strip().lower()
            ED2IN_template.polys[polyname].set_opt(option, '')
            ED2IN_template.polys[polyname].set_opt_lnum(option, lnum)

if debugging:
   print("!--------------------------------------------------------------------------------------!")
   print("!    Debugging Output: ED2IN                                                           !")
   print("!--------------------------------------------------------------------------------------!")
   ED2IN_template.print()
   print("!--------------------------------------------------------------------------------------!")
   print(" ")
#=============================================================================================#



#=============================================================================================#
# Check that the options specified in the joborder file are recognized. They will be sorted   #
# into lists 'found', 'not_found'. 'exclusions' will be used to identify special options.     #
#=============================================================================================#
print("[3.0] Checking options are compatible with ED2IN...")
print(" ")

found      = []    # Options from joborder.txt found in template ED2IN
not_found  = []    # As above, but not found.

if debugging:
   print("!--------------------------------------------------------------------------------------!")
   print("!    Debugging Output: ED2IN vs Joborder                                               !")
   print("!--------------------------------------------------------------------------------------!")
   print(" - Stepping through joborder polygon list...")

# Polygon Loop
for polyname in joborder.polys.keys():

   if debugging:
      print(" ")
      print('   - Current Polygon: ',polyname)
      print('     - Stepping through polygon options...')
      
   # Option Loop
   for opt in joborder.polys[polyname].opts:
      if opt in ED2IN_template.polys['this'].opts: 
         found.append(opt)
      else:
         not_found.append(opt)
         if debugging:
            print('     - Opt. NOT found: ',opt)

if debugging:
   print("!--------------------------------------------------------------------------------------!")
   print(" ")
#=============================================================================================#




#=============================================================================================#
# Copy the template folder and replace ED2IN contents.                                        #
#=============================================================================================#
print("[4.0] Creating directories for polygons...")

#--- Polygon Loop ----------------------------------------------------------------------------#
for polygon in joborder.polys.keys():
   
   poly_path = "%s/%s"%("./", polygon)
   copy_anything('./template',poly_path,demolish)
   ED2IN = "%s/%s"%(poly_path,"ED2IN")
   
   run_opt = "%s/%s"%(poly_path,"wrap_script.sh")
   with open(run_opt, "r", errors="replace") as rf:
      lines = rf.readlines()
      for lnum, line in enumerate(lines):
         if "#SBATCH -J" in line:            
            job_name_lnum = lnum
      
   with open(run_opt, "w", errors="replace") as wf:
      lines[job_name_lnum] = "%s%s%s"%("#SBATCH -J ", polygon, " # Job Name \n")
      if disp_set_opts:
         print('   - New wrap_script.sh line: ', lines[job_name_lnum])
      
      wf.writelines(lines)   
      
   if debugging:
      print(" - Modifying ED2IN for polygon", polygon)

   with open(ED2IN, "r", errors="replace") as rf:
      lines = rf.readlines()
      
   with open(ED2IN, "w", errors="replace") as wf:
      #--- Set output paths ------------------------------------------------------------------#
      ffilout_lnum = ED2IN_template.polys['this'].opts['ffilout'][1]
      sfilout_lnum = ED2IN_template.polys['this'].opts['sfilout'][1]
      lines[ffilout_lnum] = "%s%s%s" % ("   NL%FFILOUT = './analy/", polygon, "'\n")
      lines[sfilout_lnum] = "%s%s%s" % ("   NL%SFILOUT = './histo/", polygon, "'\n")
      
      #--- Option Loop -----------------------------------------------------------------------#
      for opt in found:
         newline = "%s%s%s%s%s"%("   NL%", opt.upper(), " = ", joborder.polys[polygon].opts[opt][0], "\n")
         lines[ED2IN_template.polys['this'].opts[opt][1]] = newline
         
         if disp_set_opts:
            print('   - Setting option', opt, ' = ', joborder.polys[polygon].opts[opt])
            print('   - New ED2IN Line: ', newline)
      #---------------------------------------------------------------------------------------#

      wf.writelines(lines)
#---------------------------------------------------------------------------------------------#


if disp_unset_opts:
   print("!-------------------------------------------------------------------------------------!")
   print("! Printing options found in ED2IN which joborder/spawn_poly did not attempt to set... !")
   print("! There should probably be a lot of these, but it's just for reference. This message  !")
   print("! can be turned off by changing the 'disp_unset_opts' var to 0 in this script.        !")
   print("!-------------------------------------------------------------------------------------!")
   for opt in ED2IN_template.polys['this'].opts:
      if opt == 'sfilout' or opt == 'ffilout':
         continue
      if opt not in found and opt not in not_found:
         print(" - ", opt)
#=============================================================================================#

print(" ")
print("Finished!")
