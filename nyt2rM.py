import os
import http.cookiejar
import datetime
import time
import io
import requests
import rmapy.api as rmapi

XWFOLDERNAME = "Crosswords"


def getNytInfo(dateStart: datetime.date, dateEnd: datetime.date):
    params = {'publish_type': 'daily',
              'sort_order': 'asc',
              'sort_by': 'print_date',
              'date_start': str(dateStart),
              'date_end': str(dateEnd),
              'limit': '100', }
    url = 'https://nyt-games-prd.appspot.com/svc/crosswords/v3/36569100/puzzles.json'
    req = requests.get(url, params)
    req.raise_for_status()
    return req.json()['results']


def downloadNytPdf(puzzId: str) -> requests.Response:
    filePath = os.path.join(os.path.dirname(__file__), "nyt-cookies.txt")
    cookieJar = http.cookiejar.MozillaCookieJar(filePath)
    cookieJar.load()

    url = 'https://www.nytimes.com/svc/crosswords/v2/puzzle/' + puzzId + '.pdf'
    pdfResponse = requests.get(url,cookies=cookieJar)
    pdfResponse.raise_for_status()

    return pdfResponse


def findOrCreateXwSubFolder(rmClient,folderName) -> rmapi.Folder:
    crosswordFolder = findOrCreateXwFolder(rmClient)
    folders = [f for f in rmClient.get_meta_items(True)
               if f.VissibleName == folderName
               and f.Parent == crosswordFolder.ID
               and isinstance(f,rmapi.Folder)]
    destFolder = None
    if len(folders) == 0:
        destFolder = rmapi.Folder(folderName)
        destFolder.Parent = findOrCreateXwFolder(rmClient).ID
        rmClient.create_folder(destFolder)
        rmClient.get_meta_items(False)
    else:
        destFolder = folders[0]
    return destFolder


def findOrCreateXwFolder(rmClient) -> rmapi.Folder:
    folders = [ f for f in rmClient.get_meta_items(True)
                        if f.VissibleName == XWFOLDERNAME
                        and f.Parent != "trash"
                        and isinstance(f,rmapi.Folder) ]
    crosswordFolder = None
    if len(folders)== 0:
        crosswordFolder = rmapi.Folder(XWFOLDERNAME)
        rmClient.create_folder(crosswordFolder)
        rmClient.get_meta_items(False)
    else:
        crosswordFolder = folders[0]
    return crosswordFolder


def docExists(rmClient, docName, folder) -> bool:
    docs = [d for d in rmClient.get_meta_items(1)
            if d.VissibleName == docName
            and d.Parent == folder.ID
            and isinstance(d, rmapi.Document)]
    return len(docs) > 0


class ZipDocFromBytesIO(rmapi.ZipDocument):
    def __init__(self, name: str, IO: io.BytesIO, fileType: str):
        super().__init__()
        if fileType == "pdf":
            self.content["fileType"] = "pdf"
            self.pdf = IO
        if fileType == "epub":
            self.content["fileType"] = "epub"
            self.epub = IO
        self.metadata["VissibleName"] = name


def mostRecentDownloadDate(rmClient: rmapi.Client, folder: rmapi.Folder) -> datetime.date:
    docs = [d for d in rmClient.get_meta_items(1)
            if d.Parent == folder.ID
            and isinstance(d, rmapi.Document)]
    return max([datetime.date.fromisoformat(d.VissibleName) for d in docs])


def downloadNytCrosswords(dateStart: datetime.date, dateEnd: datetime.date):
    '''
    Download a range of NYT crossword puzzles for the specified
    date range.

    :param datetime.date dateStart: defaults to last unimported puzzle, up to ten days
    :param datetime.date dateEnd: defaults to the most recent released NYT puzzle
    '''
    rmClient = rmapi.Client()

    # Try a few times, this will sometimes excute on wakeup so internet might not be connected yet.
    success = False
    for i in range(5):
        try:
            rmClient.renew_token()
            success = True
            break
        except(requests.exceptions.ConnectionError):
            time.sleep(60)
    if not success:
        print("Failed to renew token from reMarkable after five" +
              " minutes. Probably internet is down.")
        return

    destFolder = findOrCreateXwSubFolder(rmClient, "New York Times")

    today = datetime.date.today()
    if dateEnd is None:
        dateEnd = today + datetime.timedelta(1)
    if dateStart is None:
        dateStart = mostRecentDownloadDate(rmClient, destFolder) + datetime.timedelta(1)
        dateStart = max(dateStart, today - datetime.timedelta(10))
    if dateStart > dateEnd:
        print("No new puzzles to download")
        return

    nytInfo = getNytInfo(dateStart, dateEnd)

    for metadata in nytInfo:
        puzzId = str(metadata['puzzle_id'])
        printDate = str(metadata['print_date'])

        name = printDate
        if docExists(rmClient, name, destFolder):
            print("Already downloaded " + name)
            continue
        pdfResponse = downloadNytPdf(puzzId)
        doc = ZipDocFromBytesIO(name, io.BytesIO(pdfResponse.content), "pdf")
        rmClient.upload(doc, destFolder)
        print("Successfully downloaded " + name)
