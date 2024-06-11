#!/usr/bin/env python
from pathlib import Path
from functools import partial
import click
from geosys.utils import request_data
import os
import json

class BMapPanoGrabber():
    def __init__(self, out, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)
        self.out = out
        self.base_url = "https://mapsv0.bdimg.com/?qt=sdata&sid="
        if os.path.exists(self.out) == False:
            os.mkdir(self.out)
            os.mkdir(Path(self.out,"cache"))
            os.mkdir(Path(self.out,"pano"))
            os.mkdir(Path(self.out,"tmp"))

    def _url_json(self, pid):
        return f"{self.base_url}{pid}"

    def _local_json(self, pid):
        return Path(self.out,"cache",f"{pid}.json")

    def _save_json(self, pid):
        out_path = self._local_json(pid)
        if os.path.exists(out_path):
            return True
        data = request_data(self._url_json(pid),verbose=True)
        if data == None:
            return False
        with open(out_path, 'w', encoding='utf-8') as file:
            json.dump(data, file, ensure_ascii=False, indent=4)
        return True

    def load_json(self, pid):
        out_path = self._local_json(pid)
        if os.path.exists(out_path) == False:
            if self._save_json(pid) == False:
                return None
        with open(out_path, 'r', encoding='utf-8') as file:
            data = json.load(file)
            return None if data["result"]["error"] == 404 else data["content"]

    def get_road_pids(self, pid, save=False):
        data = self.load_json(pid)
        if data is None: return []
        road_data = data[0]["Roads"]
        pids = []
        for road in road_data:
            if road['IsCurrent'] == 0:
                continue
            for pano in road['Panos']:
                pids.append(pano['PID'])
        if save == True:
            for pid in pids:
                self._save_json(pid)
        return pids

    def get_link_pids(self, pid, save=False):
        data = self.load_json(pid)
        if data is None: return []
        road_data = data[0]["Links"]
        pids = []
        for node in road_data:
            pids.append(node['PID'])
        if save == True:
            for pid in pids:
                self._save_json(pid)
        return pids

    def get_expend_pids(self, pid, level=1, save=False):
        assert level >= 1
        data = self.load_json(pid)
        if data is None: return []
        if level == 1:
            return self.get_road_pids(pid, save)
        else:
            pids = []
            current_road_pids = self.get_road_pids(pid, save)

            for link in self.get_link_pids(current_road_pids[0],save):
                pids = pids + self.get_expend_pids(link,level=level-1,save=save)
            if len(current_road_pids) != 1:
                for link in self.get_link_pids(current_road_pids[-1],save):
                    pids = pids + self.get_expend_pids(link,level=level-1,save=save)
            return pids + current_road_pids

    def write_pids(self, pids):
        with open(Path(self.out,"tmp","pids.txt"), "w") as f:
            unique_pids = list(dict.fromkeys(pids))
            lines = [f"{item}\n" for item in unique_pids]
            f.writelines(lines)

click.option = partial(click.option, show_default=True)
@click.command()
@click.argument("pid")
@click.option('-o', '--out', default='')
@click.option('-n', '--num', default=20)
def main(pid, out, num):
    grabber = BMapPanoGrabber(out)

    # 通过指定 PID 得到对应 json, 可确保本地保存备份
    # print(grabber.load_json(pid) is None) # get dict
    # print(grabber.load_json("12345") is None) # get None

    # 路中间: 得到某条道路的 PID，可以保存某条街道所有 pid 对应的 json
    # print(grabber.get_road_pids(pid))

    # 路口: 得到某个道路尽头节点的相连的节点的 PID，可以保存节点对应的所有 pid的 json
    # print(grabber.get_link_pids(pid))

    # 递归扩展 PID(别设置的太大，防止死循环)
    pids = grabber.get_expend_pids(pid, level=2, save=True)

    # 写到文件里边
    grabber.write_pids(pids)

    # 脚本案例
    # export PYTHONPATH=.:$PYTHONPATH
    # # ./scripts/grab_line_pano_info.py 09002200121902171548254582G -o samples/data/test
    # # 路中间
    # # ./scripts/grab_line_pano_info.py 09002200121902031112297132L -o samples/data/test
    # # 路尽头
    # # ./scripts/grab_line_pano_info.py 09002200121902031112027092L -o samples/data/test
    # # 路口
    # ./scripts/grab_line_pano_info.py 09002200122104201441584797C -o samples/data/test
    # cat ./samples/data/test/tmp/pids.txt | xargs -I {} ./scripts/download_map_pano.py -t bmap {} -o samples/data/test/pano


if __name__ == "__main__":
    main()
