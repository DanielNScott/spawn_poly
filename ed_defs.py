'''
Created on Jul 7, 2014

@author: DanielNScott
'''
import shutil, errno
import os

#---------------------------------------------------------------------------------------------#
# Define a "polygon" object for holding simulation ED2IN/joborder options.                    #
#---------------------------------------------------------------------------------------------#
class polygon:
   def __init__(self):
      self.opts = {}                         # Dictionary for ED2IN/joborder options
   
   def set_opt(self,opt_name,opt_val):       # Method for setting an option
      self.opts[opt_name] = [opt_val,'']
      
   def set_opt_lnum(self,opt_name,lnum):     # Method for saving an namelist var's line number
      self.opts[opt_name][1] = lnum
         
   def print_options(self):                  # A method for printing the options that have been
      print('Options: ')                     # set in a formatted way.
      for opt in self.opts:
         print('  -',opt,self.opts[opt])
#---------------------------------------------------------------------------------------------#
         



#---------------------------------------------------------------------------------------------#
# Define an input file object which has a name and contains a set of polygons. Reading a      #
# joborder.txt file will populate it with many polygons. Reading an ED2IN will populate it    #
# with one. This is really just a dictionary with a name and a print method.                  #
#---------------------------------------------------------------------------------------------#
class input_file_object:
   """Content from ED2IN or joborder.txt"""
   
   def __init__(self,file_name):
      self.fname = file_name                 # The name of the file that's read.
      self.polys = {}                        # Dictionary as mentioned.

   def create_polygon(self,polyname):        # Wrapper for populating the dict. with polygons
      self.polys[polyname] = polygon()
   
   def print(self):                          # A print method for displaying what's in here.
      print('Filename: ',self.fname)
      print(' ')
      for key in self.polys.keys():
         print('Polygon: ',key)
         self.polys[key].print_options()
         print(' ')
#---------------------------------------------------------------------------------------------#


#---------------------------------------------------------------------------------------------#
# A safe routine for copying folders (this will create polygon directories.)                  #
#---------------------------------------------------------------------------------------------#
def copy_anything(src, dst, demolish):
   
   if os.path.exists(dst):
      if demolish:
         message = "%s%s%s" %("Directory ", dst, " found, are you SURE you want to DEMOLISH it? (Y/N):  ")
         print(' ')
         user_demo_approval = input(message)
         
         if user_demo_approval == 'Y':
            shutil.rmtree(dst)
            print('Folder ', dst, 'demolished.')
         else:
            print('Script aborted, no user approval of demolition supplied. ')
            raise
      else:
         print('Demolish is set to false in spawn_poly.py but you are trying to overwrite folders...')
         raise

   try:
      shutil.copytree(src, dst)
   except OSError as exc: # python >2.5
         if exc.errno == errno.ENOTDIR:
            shutil.copy(src, dst)
         else: raise

   print(' ')
#---------------------------------------------------------------------------------------------#



#---------------------------------------------------------------------------------------------#
# Short routine for adding options to input_file_type polygons.                               #
#---------------------------------------------------------------------------------------------#
def set_add_opt(opts, new_opt, val, record):
   opts[new_opt] = [val, '']
   record.append(new_opt)
#---------------------------------------------------------------------------------------------#

