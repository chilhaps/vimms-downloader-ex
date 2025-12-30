import requests
import os
import zipfile
import py7zr
import re
import shutil
import multiprocessing
from tqdm import tqdm
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.support.ui import Select

def get_media(url):
    print("Getting media information...")
    print(url)

    dl_formats_num = 0
    dl_versions_num = 0

    response = requests.get(url, verify=False)
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')

        dl_format_dd = soup.find('select', {'id': 'dl_format'})
        if dl_format_dd:
            dl_formats_num = len(dl_format_dd.find_all('option'))

        dl_version_dd = soup.find('select', {'id': 'dl_version'})
        if dl_version_dd:
            dl_versions_num = len(dl_version_dd.find_all('option'))

        if dl_versions_num > 1:
            driver = webdriver.Firefox()
            driver.get(url)

            # dl_format_dd = driver.find_element('id', 'dl_format')
            dl_version_dd = driver.find_element('id', 'dl_version')

            # dl_format_select = Select(dl_format_dd)
            dl_version_select = Select(dl_version_dd)

            # dl_format_select.select_by_index(len(dl_format_select.options) - 1)
            dl_version_select.select_by_index(len(dl_version_select.options) - 1)

            soup = BeautifulSoup(driver.page_source, 'html.parser')
            driver.quit()

    media_id_element = soup.find('input', {'name': 'mediaId'})
    url_element = soup.find('form', {'id': 'dl_form'})

    if media_id_element:
        media_id = media_id_element['value']
        url = url_element['action']
        return {'id': media_id, 'url': url, 'formats': dl_formats_num}
    else:
        print("Unable to find media")
        return None

def download(media):
    downloadUrl = "https:" + media['url'] + "?mediaId=" + media['id']
    
    if media['formats'] > 1:
        downloadUrl += "&alt=1"
    
    print(downloadUrl)
    headers = {
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
        "Accept-Encoding": "gzip, deflate, br, zstd",
        "Accept-Language": "pt-BR,pt;q=0.9,en;q=0.8",
        "Connection": "keep-alive",
        "Cookie": "__qca=I0-1342370008-1747309780452; _ga=GA1.1.1175809765.1747138134; AWSUSER_ID=awsuser_id1747138134137r3241; usprivacy=1N--; _sharedID=198ad7f1-fc13-4031-94d5-b6248fb04e22; _lr_env_src_ats=false; _cc_id=f56dab5fa81316ab7f8c5abe46e1505b; panoramaId_expiry=1747742924246; panoramaId=ba332d2f58c66aeb74f3c16a4ef94945a702ee765cb2aaf02c55a93ee0b84699; panoramaIdType=panoIndiv; _pbjs_userid_consent_data=3524755945110770; pbjs-unifiedid=%7B%22TDID%22%3A%2284398995-efdb-40ef-ae45-9de85e5e000b%22%2C%22TDID_LOOKUP%22%3A%22FALSE%22%2C%22TDID_CREATED_AT%22%3A%222025-05-14T11%3A25%3A57%22%7D; pbjs-unifiedid_cst=VyxHLMwsHQ%3D%3D; pbjs-unifiedid_last=Wed%2C%2014%20May%202025%2011%3A26%3A00%20GMT; FCNEC=%5B%5B%22AKsRol8DsZXR94uXRzLKroxC1CUagbaD_GhBXRlrDd5HLvdAkv_aYvAG-36Of4VhLMCFdJOpCKrI7L0jIHT70w9mZc-cQNSWxGTlVfla-rD9aEQEi2foimmzRCqDm0x2luPk5Q3rkPQ30LITKlhNqsLOvVLrJZog8g%3D%3D%22%5D%5D; _sharedID=198ad7f1-fc13-4031-94d5-b6248fb04e22; _sharedID_cst=kSylLAssaw%3D%3D; _sharedID_last=Wed%2C%2014%20May%202025%2019%3A03%3A14%20GMT; _ga_4BESX0QC2N=deleted; counted=1; PHPSESSID=m35imrfpejp9c8psd194r5fho8; AWSSESSION_ID=awssession_id1747309696995r3939; _ga_4BESX0QC2N=GS2.1.s1747309697$o11$g0$t1747309697$j0$l0$h0; _awl=2.1747309694.5-667ce87a3ddf36164610146f28534810-6763652d75732d6561737431-0; _sharedID_cst=kSylLAssaw%3D%3D; cto_bidid=rUpChV9PNlRhTU9PUWxXSCUyRkthcUF2YXVjQTRUQyUyQld1eE1qWVBoJTJGY1NZakp6MUh2TUYxcVVzaWIyN08ySFN4d3Z3MlJRdXlzWnpNMmlvRFNHb3hZU0ZJS2dGc29FVnp2VnFlMTJhV0NVQmlTV0R3NCUzRA; cto_dna_bundle=luzugV9RVGdDQ0ZKak9sUEtQM1RpVzdVdFA0dmJtQUdYVWwlMkZyWW1jZmlTWUdOZ3JPd21PSnRrR3hnNWhrWDRwYjUwaTBZVWxyWjVVNjlaT2k3bTBDaE1rTVNBJTNEJTNE; cto_bundle=nbAY6F9RVGdDQ0ZKak9sUEtQM1RpVzdVdFA2UVJNWENkWE5Qc3g1cGtoNUE1JTJCY2NpSlUyMzJkNUdLJTJCeTdsMEtMVFElMkJJNnh1QXlUUE9XN0huMXFtODJzeGt0eCUyQk5xd0phU2xZaDJrNm1XMm4lMkZLU0kzcFEzcyUyQjhyRzJPelVqUnRXWW02VXpOaFBRRngzNlJvVWxnbXJQd1V4aEElM0QlM0Q; __gads=ID=c82e2ea87bee2953:T=1747138125:RT=1747311707:S=ALNI_MaH5U2VXdlREnRpIqJsVCM9JyW6cA; __eoi=ID=241794a8d0acedda:T=1747138125:RT=1747311707:S=AA-AfjZvrpIAAE8ZfDsr6IZCeEtZ",
        "Host": media['url'].replace("/", ""),
        "Referer": "https://vimm.net/vault/8415",
        "Sec-Ch-Ua": "\"Chromium\";v=\"136\", \"Microsoft Edge\";v=\"136\", \"Not.A/Brand\";v=\"99\"",
        "Sec-Ch-Ua-Mobile": "?0",
        "Sec-Ch-Ua-Platform": "\"Windows\"",
        "Sec-Fetch-Dest": "document",
        "Sec-Fetch-Mode": "navigate",
        "Sec-Fetch-Site": "same-site",
        "Sec-Fetch-User": "?1",
        "Upgrade-Insecure-Requests": "1",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36 Edg/136.0.0.0"
    }
    with requests.get(downloadUrl, headers=headers, stream=True, verify=False) as response:
        if response.status_code == 200 or response.status_code == 304:
            total_size = int(response.headers.get('content-length', 0))
            content_disposition = response.headers.get('content-disposition')
            filename = None
            match = re.search(r'filename="(.+?)"', content_disposition)
            if match:
                filename = match.group(1)
            file_path = os.path.join("downloading", filename)
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            with tqdm(total=total_size, unit='B', unit_scale=True, desc=file_path) as pbar:
                with open(file_path, 'wb') as file:
                    for chunk in response.iter_content(chunk_size=1024):
                        if chunk:
                            file.write(chunk)
                            pbar.update(len(chunk))
            print("Download finished!")
            finished_dir = os.path.join("finished")

            os.makedirs(finished_dir, exist_ok=True)
            shutil.move(file_path, os.path.join(finished_dir, filename))
            return os.path.join(finished_dir, filename)
        else:
            print("Error downloading media:", response.text, response.status_code)
        
        response.close()
        return response.status_code

def extract_and_delete(records):
    while True:
        if records:
            archive_path = records.pop(0)
            extract_dir = os.path.join("extracted")

            try:
                os.makedirs(extract_dir, exist_ok=True)

                if archive_path.endswith('.zip'):
                    with zipfile.ZipFile(archive_path, 'r') as zip_ref:
                        zip_ref.extractall(extract_dir)
                        print(f"Extracted zip: {archive_path} to {extract_dir}")

                    os.remove(archive_path)
                    print(f"Deleted original file: {archive_path}")
                elif archive_path.endswith('.7z'):
                    with py7zr.SevenZipFile(archive_path, 'r') as seven_zip:
                        seven_zip.extractall(extract_dir)
                        print(f"Extracted 7z: {archive_path} to {extract_dir}")
                        
                    os.remove(archive_path)
                    print(f"Deleted original file: {archive_path}")
                elif archive_path == "END":
                    print("Extraction process ending.")
                    break
                else:
                    print(f"Unsupported message received: {archive_path}")
            except Exception as e:
                print(f"Error extracting {archive_path}: {e}")

def download_from_txt(records, file):
    with open(file, 'r') as f:
        lines = f.readlines()
        for line in lines:
            print(f"URL: {line.strip()}")
            url = line.strip()
            media = get_media(url)
            if media:
                print(f"Media found: {media['id']} {media['url']}")
                records.append(download(media))
            else:
                print(f"Media not found")

    records.append("END")

if __name__ == "__main__":
    with multiprocessing.Manager() as manager:
        # creating a list in server process memory
        records = manager.list([])

        # creating new processes
        p1 = multiprocessing.Process(target=download_from_txt, args=(records, "links.txt"))
        p2 = multiprocessing.Process(target=extract_and_delete, args=(records,))

        p1.start()
        p2.start()

        p1.join()
        p2.join()
