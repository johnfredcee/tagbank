# tagbank
Small python utility for generating tags tables for large projects.

This is just a small utility that I use for indexing large codebases.

In this case, the Unreal 4 Engine. It should be pretty self-explanatory
from examination of the .conf file. To run, all is needed is to run
python tagbank.py and the indexes are updated. The tag files are named
after the headings in the .conf file, so the example will generate tag
files named UE4Editor.TAGS, UE4Developer.TAGS and UE4Runtime.TAGS

Dependencies:

* python-ctags3