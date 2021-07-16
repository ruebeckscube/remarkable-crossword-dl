#!/usr/bin/env python3

import argparse
import nyt2rM
import datetime
import sys

parser = argparse.ArgumentParser(description="Syncs a copy of the New York Times Crossword to your Remarkable")
parser.add_argument("start", help="Start Date in ISO format (YYYY-MM-DD)", default=None, nargs='?')
parser.add_argument("end", help="End Date in ISO format (YYYY-MM-DD)", default=None, nargs='?')
parser.add_argument("-t", "--today", help="Just get today's crossword. NOTE: Will ignore start/end arguments.", action='store_true')
args = parser.parse_args()

if not args.today:
  dateStart = datetime.date.fromisoformat(args.start)
  dateEnd = datetime.date.fromisoformat(args.end)
else:
  dateStart = datetime.date.today()
  dateEnd = None

nyt2rM.downloadNytCrosswords(dateStart,dateEnd)
