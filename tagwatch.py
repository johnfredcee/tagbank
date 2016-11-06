# -*- mode: Python; tab-width: 4 -*-
#
# Read a description of a project from an sqlite database
# and commence watching all directories present in it for
# changes
#
import sys
import ctags
import getopt
import os
import os.path
import subprocess
import configparser
import sqlite3
import time
import logging
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

ConfigFile = "tagbank.conf"

class TagHandler(FileSystemEventHandler):
	def on_modified(self, event):
		print("Got it!")
		print("Event type %s path %s." % ( event.event_type, event.src_path))

def watch_section(conn, cursor, section):
	# fetch directories
	query = "SELECT * FROM " + section + " WHERE pathtype=1;"
	cursor.execute(query)
	dirnames = cursor.fetchall()
	# fetch files
	query = "SELECT * FROM " + section + " WHERE pathtype=0;"
	cursor.execute(query)
	filenames = cursor.fetchall()
	for dirname, _ in dirnames:
		event_handler = TagHandler()
		observer = Observer()
		observer.schedule(event_handler, dirname, recursive=False)
	return observer

if __name__ == "__main__":
	conn = sqlite3.connect("projects.db")
	cursor = conn.cursor()
	config = configparser.ConfigParser()
	config.read(ConfigFile)
	observers = []
	for section in config.sections():
		if (section == "Global"):
			continue
		observers += [ watch_section(conn, cursor, section) ]
	conn.commit()
	cursor.close()
	for o in observers:
		o.start()
	try:
		while True:
			time.sleep(1)
	except KeyboardInterrupt:
		for o in observers:
			o.stop()
