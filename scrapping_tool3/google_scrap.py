import bs4
import requests
import shutil
import os
import argparse
import pathlib
from uuid import uuid4

GOOGLE_IMAGE = (
    "https://www.google.com/search?site=&tbm=isch&source=hp&biw=1873&bih=990&"
)


def extract(searchterm, quantity):

    if not os.path.exists(searchterm):
        os.mkdir(searchterm)

    URL_input = GOOGLE_IMAGE + "q=" + searchterm
    print("Fetching from url =", URL_input)
    URLdata = requests.get(URL_input)
    soup = bs4.BeautifulSoup(URLdata.text, "html.parser")
    ImgTags = soup.find_all("img")
    i = 0
    print("Please wait..")
    while i < quantity:

        for link in ImgTags:
            try:
                images = link.get("src")
                ext = images[images.rindex(".") :]
                if ext.startswith(".png"):
                    ext = ".png"
                elif ext.startswith(".jpg"):
                    ext = ".jpg"
                elif ext.startswith(".jfif"):
                    ext = ".jfif"
                elif ext.startswith(".com"):
                    ext = ".jpg"
                elif ext.startswith(".svg"):
                    ext = ".svg"
                data = requests.get(images, stream=True)
                filename = str(i) + ext
                with open(os.path.join(searchterm, filename), "wb") as file:
                    shutil.copyfileobj(data.raw, file)
                i += 1
            except:
                pass
    print("\t\t\t Downloaded Successfully..\t\t ")


def download_images(img_list: pathlib.Path, output_path: pathlib.Path) -> None:
    headers = {
            'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.0.0 Safari/537.36',
            }

    if not output_path.exists():
        os.mkdir(output_path)

    i = 0
    with open(img_list, "r") as f:
        for url in f:
            i += 1
            urlo = pathlib.Path(url)
            new_name = f"{str(uuid4())}.jpg"
            print("Download:", url, "--->", new_name, "||||", urlo.stem, "||", urlo.suffix)
            # r = requests.get(url, allow_redirects=True)
            r = requests.get(url, headers=headers, allow_redirects=False)
            open(str(pathlib.Path(output_path, new_name)), 'wb').write(r.content)
            if i > 10:
                break

if __name__ == "__main__":

    download_images("roof_urls.txt", pathlib.Path('output'))

#     parser = argparse.ArgumentParser()
# 
#     parser.add_argument(
#         "--size",
#         type=int,
#         help="Setting how many pictures you want to get",
#         default=1000,
#     )  # This number is the amount images that will be downloaded; change the value if you need more or fewer pictures.
# 
#     args = parser.parse_args()
# 
#     list_test = (
#         ["tail light damage", "car roof damage", "car rear glass damage"]
#     )  # Enter the words or objects that you want to search for and download images e.i ["banana", "apple fruit"].
# 
#     for item in list_test:
#         extract(item, args.size)
