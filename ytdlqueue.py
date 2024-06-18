#!/usr/bin/env python3
# coding: utf-8
""" Queue for single-instance youtube_dl """
from pathlib import Path
from yt_dlp import YoutubeDL  # type: ignore
import urllib.parse as ul
import socket
import argparse

queueFile = Path.home() / ".ytdlqueue"

""" HTTP unquote CLI arg
    If blank, assume script was called to restart
    the download queue """
vid = None
# Strings for matching
ytstrings = ["youtu.be", "youtube", "http"]


def appendQueue():
    """Add vid to queueFile"""
    if vid:
        with queueFile.open("a") as qf:
            qf.write(f"{vid}\n")


''' File Locking '''
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


def queueEmpty() -> bool:
    """True if empty, False if not"""
    with queueFile.open("r") as qf:
        if any(x in qf.readline() for x in ytstrings):
            return False
        else:
            return True


def delQueueTopVid(vid: str) -> None:
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


if __name__ == '__main__':
    """ Call yt-dlp in a while loop.
        Open queueFile each time ytdl is called.
        When complete delete vid from queue. """

    parser = argparse.ArgumentParser()

    parser.add_argument(
            "input", nargs="?",
            type=str,
            help="Video to download." +
            "Any url or video ID accepted by yt-dlp")
    args = parser.parse_args()
    if args.input:
        vid = ul.unquote_plus(args.input)

    run_once("ytdllock")

    vid = getQueueTopVid()
    """ Call yt-dlp """
    while vid:
        print(f"Running ytdl with url: {vid}")
        with YoutubeDL() as yt:
            yt.download([vid])
            # Don't del queue entry, in case DL is interrupted
            delQueueTopVid(vid)
            vid = getQueueTopVid()

    # Clean up trailing newlines in file
    with open(queueFile, "r") as file:
        lines = file.readlines()
        non_empty_lines = [_ for _ in lines if _.strip() != ""]
    with open(queueFile, "w") as file:
        file.writelines(non_empty_lines)
