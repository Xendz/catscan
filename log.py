#log.py - util module for logging

import datetime

#self explanatory
logfile = "log.txt"


def write_log(action):
    """ writes action to logfile """

    with open(logfile, "a") as logger:
        logger.write("[%s] %s\n" % (str(datetime.datetime.now()), action))


def clear_log():
    """ clears logfile """

    open(logfile, 'w').close()


def get_log(n):
    """ returns n last lines of logfile """

    lines = [line.rstrip('\n') for line in open(logfile)]

    if n < len(lines):
        return lines[-n:]
    else:
        return lines
