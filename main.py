import os
import numpy as np
import pandas as pd
import xml.etree.ElementTree as ET
import argparse
import glob
import pickle


def get_building_info(bldg):

    measuredHeight = np.nan
    lod0FootPrint = np.nan
    usage = np.nan
    for i in range(len(bldg)):
        if "measuredHeight" in bldg[i].tag:
            measuredHeight = np.float64(bldg[i].text)
        elif "lod0FootPrint" in bldg[i].tag:
            lod0FootPrint = bldg[i]
        elif "usage" in bldg[i].tag:
            usage = np.int32(bldg[i].text)

    # lod0FootPrintからlon/latを取得
    footprint = lod0FootPrint[0][0][0][0][0][0].text
    lat = footprint.split(" ")[0]
    lon = footprint.split(" ")[1]

    return measuredHeight, lon, lat, usage


def main(bldg_dir, arg2):
    bldg_dir = os.path.join(bldg_dir, '')
    gml_list = sorted(glob.glob(bldg_dir + "*.gml"))

    matched = []
    df_matched = pd.DataFrame(data=None, columns=["lat", "lon", "measuredHeight"], dtype=np.float64)
    # 全てのgmlファイルに対して検索
    for gmlfile in gml_list:
        tree = ET.parse(gmlfile)
        root = tree.getroot()

        # 最初のchildはbuildingではないので、2つ目以降を処理
        for child in root:
            if not "cityObjectMember" in child.tag:
                continue

            if "consistsOfBuildingPart" in child[0][0].tag:
                for bldg_part in range(len(child[0])):
                    target_bldg = child[0][bldg_part][0]

                    # buildingの情報を取得
                    # print(gmlfile, target_bldg)
                    measuredHeight, lon, lat, usage = get_building_info(target_bldg)

                    # 高さが25m以上のもののlon, latをリストに追加
                    if (measuredHeight >= 25.0) and (usage == 421):
                        matched.append(target_bldg)
                        df_matched = df_matched.append({"measuredHeight":measuredHeight, "lon":lon, "lat":lat}, ignore_index=True)
                        print("measuredHeight:", measuredHeight)
                        print("lon, lat:", lon, lat)
                        print("usage:", usage)

            else:

                # target buildingを取得
                target_bldg = child[0]

                # buildingの情報を取得
                measuredHeight, lon, lat, usage = get_building_info(target_bldg)

                # 高さが25m以上のもののlon, latをリストに追加
                if (measuredHeight >= 25.0) and (usage == 421):
                    matched.append(target_bldg)
                    df_matched = df_matched.append({"measuredHeight": measuredHeight, "lon": lon, "lat": lat},
                                                   ignore_index=True)
                    print("measuredHeight:", measuredHeight)
                    print("lon, lat:", lon, lat)
                    print("usage:", usage)

    f = open('matched.pkl', 'wb')
    pickle.dump(matched, f)
    df_matched.to_csv(arg2, index=False)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='')
    parser.add_argument('arg1', help='入力ファイル名')
    parser.add_argument('arg2', help='出力ファイル名')

    # 引数を解析
    args = parser.parse_args()
    print('arg1=' + args.arg1)
    print('arg2=' + args.arg2)

    main(args.arg1, args.arg2)