import os
from pathlib import Path
from fastai.vision.utils import download_images, verify_images


def download_images_fastai(
    input_path: Path, output_path: Path
) -> None:

    output_path.mkdir(parents=True, exist_ok=True)

    print("  - Downloading Images -   ")
    download_images(url_file=input_path, dest=output_path)
    print("  - Done -   ")


def check_images_fastai(
    output_path: Path
) -> None:

    print("  - Checking Images -   ")
    # verify_images(output_path, delete=True, img_format=f"{c} %d")
    li = verify_images(output_path.ls())
    print(li)
    print("  - Done -   ")


# if __name__ == "__main__":
# 
#     classes_list = ['roof', 'taillight']
# 
#     for c in classes_list:
#         try:
#             input_path = pathlib.Path("inputs", f"{c}_urls.txt")
#             output_path = pathlib.Path("output", f"{c}_damages")
# 
#             download_images_fastai(input_path, output_path)
#             check_images_fastai(output_path)
# 
#         except Exception as e:
#             print(e)

if __name__ == "__main__":

    input_path = Path("inputs")
    output_path = Path("output")

    urls = []
    for p in os.listdir(input_path):
        print(p)
 
        with open(Path(input_path, p), "r") as src_file:
            data = src_file.read()
            data_into_list = data.replace('\n', ' ').split(" ")
            urls.extend(data_into_list)

    print('before:', len(urls))
    urls = set(urls)
    print('after:', len(urls))
    print(urls)

    print("  - Downloading Images -   ")
    download_images(urls=list(urls), dest=output_path)
    print("  - Done -   ")
