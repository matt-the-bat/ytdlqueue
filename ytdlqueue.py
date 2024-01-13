#!/usr/bin/env python3
# coding: utf-8
""" Queue for single-instance youtube_dl """
from pathlib import Path
import sys
import subprocess
import urllib.parse as ul
import socket

queueFile = Path().home() / ".ytdlqueue"

""" HTTP unquote CLI arg
    If blank, assume script was called to restart
    the download queue """
vid = None
try:
    vid = ul.unquote_plus(sys.argv[1])
except IndexError:
    vid = None

# Strings for matching
ytstrings = ["youtu.be", "youtube", "http"]


def appendQueue():
    """Add vid to queueFile"""
    if vid:
        with queueFile.open("a") as qf:
            qf.write(f"{vid}\n")


SOCKET = None


def run_once(uniq_name):
    """Ensure only one instance is running.
     Create an abstract socket by prefixing it with null.
    Append queue in either instance.
    """
    try:
        global SOCKET
        SOCKET = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        SOCKET.bind("\0" + uniq_name)

        appendQueue()
        return True
    except OSError:  # Socket already in use
        appendQueue()  # 1st script call will pick up queue
        raise SystemExit


def queueEmpty():
    """True if empty, False if not"""
    with queueFile.open("r") as qf:
        if any(x in qf.readline() for x in ytstrings):
            return False
        else:
            return True


def delQueueTopVid():
    """Erase all lines with vid id,
    via omission on a temp file"""
    tmpq = Path().home() / ".tempq"
    with tmpq.open("w") as tmp:
        with queueFile.open("r") as qf:
            for line in qf:
                if vid not in line:
                    tmp.write(line)
    tmpq.replace(queueFile)


def getQueueTopVid():
    """Grab next vid url from queueFile"""
    vURL = None
    if queueFile.exists():
        with queueFile.open("r") as qf:
            for line in qf:
                vURL = line.rstrip()
                break
    return vURL


run_once("ytdllock")


""" Call yt-dlp in a while loop.
    Open queueFile each time ytdl is called.
    When complete delete vid from queue. """
vid = getQueueTopVid()
while vid:
    print(f"Running ytdl with url: {vid}")
    subprocess.run(["yt-dlp", "--", vid], shell=False, check=True)
    # Don't del queue entry, in case DL is interrupted
    delQueueTopVid()
    vid = getQueueTopVid()

# Clean up trailing newlines in file
with open(queueFile, "r") as file:
    lines = file.readlines()
    non_empty_lines = [_ for _ in lines if _.strip() != ""]
with open(queueFile, "w") as file:
    file.writelines(non_empty_lines)
