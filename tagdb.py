#
# Transform an euberant ctags file to a sqlite database
#
import sys
import ctags
import getopt
import os
import os.path
import subprocess
import ConfigParser
import sqlite3

ConfigFile = "tagbank.conf"

class DirWalkArgs:
    def __init__(self, tablename, cursor, filemasks):
        self.cursor = cursor
        self.filemasks = filemasks
        self.tablename = tablename
        
def is_one_of(file_name, filemasks):
    return  "*"+os.path.splitext(file_name)[1] in filemasks

# visit a directory and add all files to the list
def visit_dir(arg, d, filelist):
    insert_cmd = "INSERT INTO " + arg.tablename + "(path, pathtype) VALUES(\"%s\", 1);" % d
    arg.cursor.execute(insert_cmd)
    for name in filelist:
        # ignore the hiding file and directory
        if name[0] == ".":
            continue
        path = os.path.join(d, name)
        if not os.path.isdir(path) and os.path.isfile(path) and is_one_of(path, arg.filemasks):
            insert_cmd = "INSERT INTO " + arg.tablename + "(path, pathtype) VALUES(\"%s\", 0);" % path
            arg.cursor.execute(insert_cmd)
            
def enumerate_dir(arg, d, filelist):
    visit_dir(arg, d, filelist)

def index_filename(name):
    return name + ".files"

def create_index(name, dirs, filetypes):
    conn = sqlite3.connect("projects")
    cur = conn.cursor()
    drop_cmd = "DROP TABLE IF EXISTS " + name + ";"
    cur.execute(drop_cmd)
    create_cmd = "CREATE TABLE " + name + "(path TEXT, pathtype INTEGER);"
    cur.execute(create_cmd)
    for d in dirs:
        os.path.walk(d, enumerate_dir, DirWalkArgs(name, cur, filetypes))
    conn.commit()
    cur.close()
    
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
    
# todo needs to run in the root directory of the project    
def invoke_ctags(prog, flags, project):
    kinds = [ "c", "d", "e", "f", "F", "g", "m", "p", "s", "t", "u", "v" ]
    conn = sqlite3.connect("projects")
    cur = conn.cursor()
    select_cmd = "SELECT path FROM " + project + " WHERE pathtype=0;"
    cur.execute(select_cmd)
    conn.commit()
    taggedfiles = cur.fetchall()
    cur.close()
    conn = sqlite3.connect("%s_TAGS" % project) 
    create_cmd = "CREATE TABLE TAGS (tag TEXT, address TEXT, path TEXT, kind INTEGER, memberof TEXT);"
    flags = "--fields=+knStmi --extra=+q --c++-kinds=cdefgmnpstuvx --c-kinds=cdefglmnpstuvx --extra=+q --filter=yes --format=2" 
    args = [ prog ] + flags 
    taglines = []
    for taggedfile in taggedfiles:
        try:
            ctags = subprocess.Popen(args, shell=True, stdout=subprocess.PIPE, stdin=subprocess.PIPE, stderr=subprocess.PIPE)
            (ctagsout, ctaggserr) = ctags.communicate(input = taggedfile)
            for line in ctagsout:
                taginfo = parse_tag_line(line)
                if taginfo:
                    insert_cmd = 
        except OSError:
            print "Command %s failed." % args
            
        
            
    for line in ctags.stdout:
        taglines.append(line)
    for taggedfile in taggedfiles:
        try:
            tags = subprocess.check_output(args)
        except subprocess.CalledProcessError:
            tags = None
        
        
# todo -- need an update mode for a single project    
if __name__ == "__main__":
    config = ConfigParser.RawConfigParser()
    config.read(ConfigFile)
    ctags_exe = config.get("Global", "ctags")
    for section in config.sections():
        if (section == "Global"):
            continue
        tagpaths  = config.get(section, "tagpaths").split(';')
        wildcards = config.get(section, "wildcards").split(';')
        flags     = config.get(section, "flags").split(';')
        create_index(section, tagpaths, wildcards)
        #invoke_ctags(ctags_exe, flags + [ "-o" ] + [ section + ".TAGS" ] + [ "-L"] + [ index_filename(section) ])
    sys.exit(0)

# C
#     c  classes
#     d  macro definitions
#     e  enumerators (values inside an enumeration)
#     f  function definitions
#     g  enumeration names
#     l  local variables [off]
#     m  class, struct, and union members
#     n  namespaces
#     p  function prototypes [off]
#     s  structure names
#     t  typedefs
#     u  union names
#     v  variable definitions
#     x  external and forward variable declarations [off]
# C++
#     c  classes
#     d  macro definitions
#     e  enumerators (values inside an enumeration)
#     f  function definitions
#     g  enumeration names
#     l  local variables [off]
#     m  class, struct, and union members
#     n  namespaces
#     p  function prototypes [off]
#     s  structure names
#     t  typedefs
#     u  union names
#     v  variable definitions
#     x  external and forward variable declarations [off]
