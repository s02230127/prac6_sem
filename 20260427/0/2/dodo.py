#!/usr/bin/env python3
from pathlib import Path
from zipfile import ZipFile
DOIT_CONFIG = {"default_tasks": ["docs"]}


def task_docs():
	"""Create doc"""
	rtspy = list(Path(".").glob("**/*.rst")) + \
		list(Path(".").glob("**/*.py"))
	return {
		"actions": ["cd docs/source && sphinx-build -M html . build"],
		"file_dep": rtspy,
	}


def task_erase():
	"""Clean all junk"""

	return {
		"actions": ["rm -rf docs/source/build"],
	}
	
	
def task_zip():
	"""Create ZIP"""
	
	def create_zip(filename, files):
		with ZipFile(filename, "w") as zf:
			for f in files:
				zf.write(f)
				
	files = list(Path("docs/source/build/html").glob("**"))
	
	return {
		"actions": [(create_zip, ["docs.zip", files])],
		"targets": ["docs/source/build/html/index.html"],
		"task_dep": ["docs"],
	}
			
	 

	
