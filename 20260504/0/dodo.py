#!/usr/bin/env python3

def task_erase():
    return {
        "actions": ["rm -f po/*/*/*.mo"],
    }

def task_dist():
	return {
		"actions": ["pyproject-build -s"],
		"task_dep": ["erase"]
	}
