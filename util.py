#!/usr/bin/python3
import sys
from datetime import datetime
stdout = sys.stdout #backup stdout, avoid redirection
def printToShell(*args):
    """
    print to shell
    """
    nowStr = datetime.now().strftime("%F %T.%f")[:-3]
    stdout.write("[{}] ".format(nowStr))
    line = " ".join(map(str, args))
    stdout.write(line)
    stdout.write("\n")