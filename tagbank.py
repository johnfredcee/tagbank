
import sys
import getopt
import os
import os.path
import subprocess
import configparser

# Example config
# [Global]
# ctags=c:\wsr\apps\ctags58\ctags.exe
# [Carmageddon]
# wildcards=*.cpp;*.c;*.h;*.inl
# tagpaths=c:\Dev\LoveBucket\Development\Beelzebub\SOURCE;c:\Dev\LoveBucket\Development\Build\Source
# flags=--c++-kinds=cfnstunedm;--c-kinds=cfnstunedm;--extra=+q

ConfigFile = "tagbank.conf"

def is_one_of(file_name, filemasks):
	return	"*"+os.path.splitext(file_name)[1] in filemasks

def index_filename(name):
	return name + ".files"

def create_index(name, dirs, filetypes):
	index_file = open(index_filename(name), "w")
	for d in dirs:
		for root, dirs, files in os.walk(d):
			for name in files:
				fullname = os.path.join(root, name)
				if is_one_of(fullname, filetypes):
					index_file.write(fullname + '\n')
	index_file.close()

def invoke_ctags(prog, flags):
	args = [ prog ] + flags
	subprocess.call(args)

if __name__ == "__main__":
	config = configparser.ConfigParser()
	config.read(ConfigFile)
	ctags_exe = config.get("Global", "ctags")
	for section in config.sections():
		if (section == "Global"):
			continue
		tagpaths  = config.get(section, "tagpaths").split(';')
		wildcards = config.get(section, "wildcards").split(';')
		flags	  = config.get(section, "flags").split(';')
		create_index(section, tagpaths, wildcards)
		invoke_ctags(ctags_exe, flags + [ "-o" ] + [ section + ".TAGS" ] + [ "-L"] + [ index_filename(section) ])
		sys.exit(0)
