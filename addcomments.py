#!/usr/bin/python3.8

import sys
import csv

USAGE = [
    "",
    "USAGE",
    "",
    "  $ ./addcomments.py albumfile commentfile",
    "",
    "  ex)",
    "      $ ./addcomments.py hoge.createalbum comments.csv | nkf -s --msdos",
    "",
    "COMMENT FILE FORMAT",
    "",
    "  filename, comment, comment, ...",
    "",
]

# check commandline options
if 3 != len(sys.argv):
    for row in USAGE:
        print(row)
    exit(-1)
albfile = sys.argv[1]
cmtfile = sys.argv[2]


# find file in comments file
def ffic(name, array):
    for row in array:
        if name.lower() == row[0].lower():
            return row[1:]
    return None


# read comments file
comments = []
with open(cmtfile) as csvfile:
    for row in csv.reader(csvfile, delimiter=','):
        comments.append(row)

# add comments to album file
with open(albfile) as csvfile:
    for row in csv.reader(csvfile, delimiter=','):
        text = ','.join(row)

        if (find := ffic(row[0], comments)) is not None:
            for col in find:
                text += ',' + col

        print(text)
