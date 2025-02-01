# remarkable-crossword-dl

NOTE 2/1/2025: This project now archived. It's been broken due to changes in reMarkable's cloud API. If it's going to be re-done it will probably have to be through the USB web interface, as the cloud API has gotten less accessible to developers.

This is a script for syncing crosswords to a reMarkable device. It doesn't need to be run on the reMarkable itself, since it sends PDFs of the crosswords to the cloud. It requires already having a subscription to the crosswords you want to download.

## Crosswords supported
- New York Times

## Setup
0. Use pip to install `rmapy` and `requests`. Follow the instructions at [rmapy](https://github.com/subutux/rmapy) for getting a reMarkable cloud token for use with this script.
1. Download the repository
2. Use a Chrome or Firefox extension to get a copy of your cookies from the NYT website as a .txt file
3. Copy that file into `remarkable-crossword-dl/` and name it `nyt-cookies.txt`
4. To run the executable manually, while in the `remarkable-crossword-dl/` folder, enter `./syncCrosswords.py <start_date> <end_date>`. The dates should be in ISO format (YYYY-MM-DD), and if not provided have defaults. `end_date` defaults to tomorrow, since NYT crosswords are published the evening before, and `start_date` defaults to the last undownloaded puzzle on your reMarkable cloud, with a max of 10 days ago.
5. You can also schedule it with your choice of script scheduler. An example plist for use with launchd is included in this project.

## Usage

```
$ ./syncCrosswords.py --help
usage: syncCrosswords.py [-h] [-t] [start] [end]

Syncs a copy of the New York Times Crossword to your Remarkable

positional arguments:
  start        Start Date in ISO format (YYYY-MM-DD)
  end          End Date in ISO format (YYYY-MM-DD)

optional arguments:
  -h, --help   show this help message and exit
  -t, --today  Just get today's crossword. NOTE: Will ignore start/end arguments.
```

## Sources
[HTTP requests for NYT Crossword](https://www.reddit.com/r/crossword/comments/dqtnca/my_automatic_nyt_crossword_downloading_script/)

[rmapy, Python API for accessing reMarkable cloud](https://github.com/subutux/rmapy)
