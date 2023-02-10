import requests
import requests.exceptions
import os
import json
import argparse
import time

from datetime import datetime

parser = argparse.ArgumentParser()
parser.add_argument("--token", help="The value of the Authorization header found from Chrome developer tools while browsing photobucket.com")
parser.add_argument("--count", type=int, help="The number of photos in the album")
parser.add_argument("--album_id", help="The UUID of the album from the URL when browsing the album on photobucket.com")
parser.add_argument("--out_dir", help="The output directory for the photos")
args = parser.parse_args()

try:
    os.mkdir(args.out_dir)
except:
    pass

url = "https://app.photobucket.com/api/graphql/v2"

graphql = ("query GetAlbumImagesV2($albumId: String!, $pageSize: Int, $scrollPointer: String, $sortBy: Sorter) {"
"getAlbumImagesV2("
"albumId: $albumId,"
"pageSize: $pageSize,"
"scrollPointer: $scrollPointer,"
"sortBy: $sortBy"
") {"
    "scrollPointer "
    "items {"
        "...MediaFragment "
        "__typename"
        "}"
        "__typename"
        "}"
        "}"
        ""
        "fragment MediaFragment on Image {"
            "id "
            "title "
            "dateTaken "
            "uploadDate "
            "isVideoType "
            "username "
            "isBlurred "
            "nsfw "
            "status "
            "image {"
                "width "
                "size "
                "height "
                "url "
                "isLandscape "
                "exif {"
                    "longitude "
                    "eastOrWestLongitude "
                    "latitude "
                    "northOrSouthLatitude "
                    "altitude "
                    "altitudeRef "
                    "cameraBrand "
                    "cameraModel "
                    "__typename"
                    "}"
                    "__typename"
                    "}"
                    "thumbnailImage {"
                        "width "
                        "size "
                        "height "
                        "url "
                        "isLandscape "
                        "__typename "
                        "}"
                        "originalImage {"
                            "width "
                            "size "
                            "height "
                            "url "
                            "isLandscape "
                            "__typename "
                            "}"
                            "livePhoto {"
                                "width "
                                "size "
                                "height "
                                "url "
                                "isLandscape "
                                "__typename"
                                "}"
                                "albumId "
                                "description "
                                "userTags "
                                "clarifaiTags "
                                "uploadDate "
                                "originalFilename "
                                "isMobileUpload "
                                "albumName "
                                "attributes "
                                "deletionState {"
                                    "deletedAt "
                                    "__typename"
                                    "}"
                                    "__typename"
                                    "}")

payload = {"operationName": "GetAlbumImagesV2",
           "query": graphql,
           "variables": {
               "albumId": args.album_id,
               "pageSize": args.count,    # Set to however many images are in the album
           }
}

headers = {
    "Authorization": args.token,
    "Referer": "https://photobucket.com/",
    "Origin": "https://photobucket.com",
    "Content-Type": "application/json",
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36",
    "apollographql-client-name": "iphotobucket-web",
    "apollographql-client-version": "1.118.0",
    "accept-encoding": "gzip, deflate, br",
    "accept": "*/*",
    "x-correlation-id": "043f52c9-06ad-4cc6-a766-03d676f463ef",
}

response = requests.post(url, json=payload, headers=headers)

if response.ok:
    print("200 OK")
    #print(len(photo_list))
    #print(json.dumps(photo_list[0], indent=4, sort_keys=True))

    data = response.json()
    if data.get("errors"):
        print(json.dumps(data, indent=4, sort_keys=True))
    else:
        start = datetime.now()
        count = 0
        
        photo_list = data["data"]["getAlbumImagesV2"]["items"]
        for entry in photo_list:
            url = entry["originalImage"]["url"]

            success = False
            while not success:
                try:
                    with open(args.out_dir + url.split("/")[-1], "wb") as img:
                        response = requests.get(url)
                        img.write(response.content)

                    print(f"Downloaded {url}")

                    count += 1
                    time.sleep(1)
                    success = True
                except requests.exceptions.ConnectionError:
                    print("Failure, retrying...")
                    time.sleep(1)

        end = datetime.now()

        print(f"Downloaded {count} images in:")
        print(end - start)
else:
    print(f"Failure: {response.status_code}")
    print(json.dumps(response.json(), indent=4, sort_keys=True))
