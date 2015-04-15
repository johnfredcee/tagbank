
import sys
import getopt
import os
import os.path
import subprocess
import ConfigParser

# Example config
# [Global]
# ctags=c:\wsr\apps\ctags58\ctags.exe
# [Carmageddon]
# wildcards=*.cpp;*.c;*.h;*.inl
# tagpaths=c:\Dev\LoveBucket\Development\Beelzebub\SOURCE;c:\Dev\LoveBucket\Development\Build\Source
# flags=--c++-kinds=cfnstunedm;--c-kinds=cfnstunedm;--extra=+q 

ConfigFile = "tagbank.conf"

class DirWalkArgs:
    def __init__(self, fileobj, filemasks):
        self.fileobj = fileobj
        self.filemasks = filemasks

def is_one_of(file_name, filemasks):
    return  "*"+os.path.splitext(file_name)[1] in filemasks

# visit a directory and add all files to the list
def visit_dir(arg, d, filelist):
#   print "Visiting d " + d
    for name in filelist:
        # ignore the hiding file and directory
        if name[0] == ".":
            continue
        path = os.path.join(d, name)
        if not os.path.isdir(path) and os.path.isfile(path) and is_one_of(path, arg.filemasks):  
            arg.fileobj.write(path + '\n')

def enumerate_dir(arg, d, filelist):
    visit_dir(arg, d, filelist)

def index_filename(name):
    return name + ".files"

def create_index(name, dirs, filetypes):
    index_file = open(index_filename(name), "w")
    for d in dirs:
        os.path.walk(d, enumerate_dir, DirWalkArgs(index_file, filetypes))
    
def invoke_ctags(prog, flags):
    args = [ prog ] + flags
    subprocess.call(args)

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
        invoke_ctags(ctags_exe, flags + [ "-o" ] + [ section + ".TAGS" ] + [ "-L"] + [ index_filename(section) ])
    sys.exit(0)
