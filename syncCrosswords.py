#!/usr/bin/env python3

import nyt2rM
import datetime
import sys

dateStart,dateEnd = None,None
if len(sys.argv) > 1: dateStart = datetime.date.fromisoformat(sys.argv[1])
if len(sys.argv) > 2: dateEnd = datetime.date.fromisoformat(sys.argv[2])
nyt2rM.downloadNytCrosswords(dateStart,dateEnd)
