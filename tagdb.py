# -*- mode: Python; tab-width: 4 -*-
#
# Walk the root directory of a project and create a table containing details
# of the files and directories it contains
#
import sys
import getopt
import os
import os.path
import subprocess
import configparser
import cmd
import json
import ctags
import sqlite3

ConfigFile = "tagbank.conf"

def is_one_of(file_name, filemasks):
    return	"*"+os.path.splitext(file_name)[1] in filemasks

def create_index(tablename, projectdirs, filetypes):
    conn = sqlite3.connect("projects.db")
    cursor = conn.cursor()
    # remove the table if it already exists - we are going to regenerate it
    drop_cmd = "DROP TABLE IF EXISTS " + tablename + ";"
    cursor.execute(drop_cmd)
    # recreate table
    create_cmd = "CREATE TABLE " + tablename + "(path TEXT, pathtype INTEGER);"
    cursor.execute(create_cmd)
    for d in projectdirs:
        fullname = d
        insert_cmd = "INSERT INTO " + tablename + "(path, pathtype) VALUES(\"%s\", 1);" % fullname
        cursor.execute(insert_cmd)
        for root, dirs, files in os.walk(d):
            # directories
            for name in dirs:
                fullname = os.path.join(root,name)
                insert_cmd = "INSERT INTO " + tablename + "(path, pathtype) VALUES(\"%s\", 1);" % fullname
                cursor.execute(insert_cmd)
                # files
            for name in files:
                fullname = os.path.join(root, name)
                if is_one_of(fullname, filetypes):
                    insert_cmd = "INSERT INTO " + tablename + "(path, pathtype) VALUES(\"%s\", 0);" % fullname
                    cursor.execute(insert_cmd)
    conn.commit()
    cursor.close()

def parse_tag_line(line):
    if line[0] == '!':
        return None # not a tag line
    fields = line.split('\t')
    tag = fields[0]
    path = fields[1]
    address = fields[2]
    fields = fields[3:]
    tagfields = {}
    for field in fields:
        if ':' in field:
            (name, value) = field.split(":")
            tagfields[name] = value
    else:
        tagfields["kind"] = field
    return ( tag, path, address, tagfields )

def memberof(tagfields):
    fields = [ "class", "struct", "union", "enum", "function" ]
    for field in fields:
        if field in tagfields:
            return tagfields[field]
        else:
            return None

# # todo needs to run in the root directory of the project
# def invoke_ctags(prog, flags, project):
#	  kinds = [ "c", "d", "e", "f", "F", "g", "m", "p", "s", "t", "u", "v" ]
#	  conn = sqlite3.connect("projects")
#	  cur = conn.cursor()
#	  select_cmd = "SELECT path FROM " + project + " WHERE pathtype=0;"
#	  cur.execute(select_cmd)
#	  conn.commit()
#	  taggedfiles = cur.fetchall()
#	  cur.close()
#	  conn = sqlite3.connect("%s_TAGS" % project)
#	  create_cmd = "CREATE TABLE TAGS (tag TEXT, address TEXT, path TEXT, kind INTEGER, memberof TEXT);"
#	  flags = "--fields=+knStmi --extra=+q --c++-kinds=cdefgmnpstuvx --c-kinds=cdefglmnpstuvx --extra=+q --filter=yes --format=2"
#	  args = [ prog ] + flags
#	  taglines = []
#	  for taggedfile in taggedfiles:
#	  try:
#		  ctags = subprocess.Popen(args, shell=True, stdout=subprocess.PIPE, stdin=subprocess.PIPE, stderr=subprocess.PIPE)
#		  (ctagsout, ctaggserr) = ctags.communicate(input = taggedfile)
#		  for line in ctagsout:
#		  taginfo = parse_tag_line(line)
#		  if taginfo:
#			  insert_cmd =
#	  except OSError:
#		  print "Command %s failed." % args



#	  for line in ctags.stdout:
#	  taglines.append(line)
#	  for taggedfile in taggedfiles:
#	  try:
#		  tags = subprocess.check_output(args)
#	  except subprocess.CalledProcessError:
#		  tags = None
#flags=--verbose;-e;--options=u4tags.conf;--c++-kinds=cfnstunedm;--c-kinds=cfnstunedm;--extra=+q

projects = {}

class TagDBCmd(cmd.Cmd):
    def do_add(self, arg):
        args = arg.split()
        if len(args) >= 2:
            if args[0] == "project":
                projectname = args[1]
                if not projectname in projects:
                    project = {"directories" : [], "filetypes" : [], "flags" : ["--verbose", "-e", "--extra=+q"]}
                    for arg in args[2:]:
                        if arg[0] == '*':
                            project["filetypes"].append(arg)
                        elif arg[0] == '-':
                            project["flags"].append(arg)
                        else:
                            project["directories"].append(arg)
                    projects[projectname] = project
                    print("Added project %s." % projectname)
                else:
                    print("%s already exists as project." % projectname)
        else:
            print("Not enough arguments")
        return
    def do_rm(self, arg):
        args = arg.split()
        if len(args) >= 2:
            if args[0] == "project":
                projectname = args[1]
                if projectname in projects:
                    del projects[projectname]
                    print("%s removed from projects." % projectname)
                else:
                    print("%s unrecognized as project." % projectname)
        else:
            print("Not enough arguments")
        return 
    def do_show(self, arg):
        args = arg.split()
        if len(args) >= 2:
            if args[0] == "project":
                projectname = args[1]
                if projectname in projects:
                    project = projects[projectname]
                    print("Directories")
                    print("===========")
                    for pdir in project["directories"]:
                        print(pdir)
                    print("Filetypes:",end = '')
                    for ftype in project["filetypes"]:
                        print(ftype, end =':')
                    print(' ')
                    print("Flags:", end='')
                    for pflag in project["flags"]:
                        print(pflag, end =':')
                    print(" ")
                else:
                    print("%s unrecognized as project." % projectname)
        return   
    def do_save(self, line): 
        confp = open("tagdb.conf", "w")
        json.dump(projects, confp)
        confp.close()
    def	do_EOF(self,line):
        confp = open("tagdb.conf", "w")
        json.dump(projects, confp)
        confp.close()
        return True


# todo -- need an update mode for a single project
if __name__ == "__main__":
    confp = open("tagdb.conf")
    projects = json.load(confp)
    confp.close()
    processor = TagDBCmd()
    config = configparser.ConfigParser()
    config.read(ConfigFile)
    ctags_exe = config.get("Global", "ctags")
    processor.cmdloop()

    # for section in config.sections():
    #     if (section == "Global"):
    #         continue
    # tagpaths  = config.get(section, "tagpaths").split(';')
    # wildcards = config.get(section, "wildcards").split(';')
    # flags	  = config.get(section, "flags").split(';')
    # create_index(section, tagpaths, wildcards)
    # #invoke_ctags(ctags_exe, flags + [ "-o" ] + [ section + ".TAGS" ] + [ "-L"] + [ index_filename(section) ])
    # sys.exit(0)

# C
#	  c	 classes
#	  d	 macro definitions
#	  e	 enumerators (values inside an enumeration)
#	  f	 function definitions
#	  g	 enumeration names
#	  l	 local variables [off]
#	  m	 class, struct, and union members
#	  n	 namespaces
#	  p	 function prototypes [off]
#	  s	 structure names
#	  t	 typedefs
#	  u	 union names
#	  v	 variable definitions
#	  x	 external and forward variable declarations [off]
# C++
#	  c	 classes
#	  d	 macro definitions
#	  e	 enumerators (values inside an enumeration)
#	  f	 function definitions
#	  g	 enumeration names
#	  l	 local variables [off]
#	  m	 class, struct, and union members
#	  n	 namespaces
#	  p	 function prototypes [off]
#	  s	 structure names
#	  t	 typedefs
#	  u	 union names
#	  v	 variable definitions
#	  x	 external and forward variable declarations [off]
