#!/usr/bin/python3
import sys
from datetime import datetime
def printToShell(*args):
    """
    print to shell
    """
    nowStr = datetime.now().strftime("%F %T.%f")[:-3]
    sys.__stdout__.write("[{}] ".format(nowStr))
    line = " ".join(map(str, args))
    sys.__stdout__.write(line)
    sys.__stdout__.write("\n")
