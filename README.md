# Vimm's Lair Downloader

## Description

This is a simple script to download and extract files from Vimm's Lair. It uses the `requests` library to make HTTP requests, `BeautifulSoup` to parse HTML, and `Selenium` to handle JavaScript content. The script downloads all the files from the specified page and saves them to a local directory. It also extracts them to a specified directory to avoid duplicates.

## Requirements

- Python 3.x

## Usage

Clone the repository and install the required packages:

```bash
git clone REPOSITORY_URL_HERE
cd vimms-downloader
pip install -r requirements.txt
```

Create a file named `links.txt` in the same directory as the script. This file should contain the URLs of the pages you want to download from, one per line. For example:

```text
https://vimm.net/vault/7836
https://vimm.net/vault/7970
https://vimm.net/vault/8000
```

Create three folders in this script root, one named `downloading` to store temp files, one named `finished`to store downloaded files, and one named `extracted` to store extracted files. Then, run the script:

```bash
python3 run.py
```

That's it! The script will download all the files from the specified pages and save them to "finished" folder, then extract to "extracted" folder and delete the compressed file.
