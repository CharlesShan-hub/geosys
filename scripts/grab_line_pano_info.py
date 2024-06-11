#!/usr/bin/env python
from pathlib import Path
from functools import partial
import click
from geosys.utils import request_data
import os
import json
import warnings

class BMapPanoGrabber():
    def __init__(self, out, **kwargs):
        """
        Initialize the BMapPanoGrabber instance.

        If the download fails, please try to change the base_url
        because Baidu may modify the url

        cache dictionary is used to save json files
        tmp dictionary is used to save pids.txt files
        pano dictionary is used to save pano photos

        Args:
            out (str): The output directory where the data will be saved.
            **kwargs: Additional keyword arguments to set as instance attributes.
        """
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
        """
        Generate the URL for the JSON data of a panorama.

        Eg. https://mapsv0.bdimg.com/?qt=sdata&sid=02015800001407191123100206A
        """
        return f"{self.base_url}{pid}"

    def _local_json(self, pid):
        """
        Generate the local path for the JSON data of a panorama.

        Eg. .../data/XinjiangTaZhiXiLu/cache/02015800001407191123100206A.json
        """
        return Path(self.out,"cache",f"{pid}.json")

    def _save_json(self, pid):
        """
        Save the JSON data of a panorama to the local cache.

        Download the corresponding json according to the pid.
        If the json has been downloaded, no changes will be made.

        Returns:
            bool: True if the JSON data was saved successfully, False otherwise.
        """
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
        """
        Load the JSON data of a panorama from the local cache or the internet.

        Returns:
            dict or None: The JSON data as a dictionary, or None if the data is not available.
        """
        out_path = self._local_json(pid)
        if os.path.exists(out_path) == False:
            if self._save_json(pid) == False:
                return None
        with open(out_path, 'r', encoding='utf-8') as file:
            data = json.load(file)
            return None if data["result"]["error"] == 404 else data["content"]

    def get_road_pids(self, pid, save=False):
        """
        Get the panorama IDs of the roads connected to a given panorama.

        Args:
            pid (str): The panorama ID.
            save (bool): Whether to save the JSON data of the panoramas.

        Returns:
            list: A list of panorama IDs.
        """
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
        """
        Get the panorama IDs linked to a given panorama.

        Args:
            pid (str): The panorama ID.
            save (bool): Whether to save the JSON data of the panoramas.

        Returns:
            list: A list of panorama IDs.
        """
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
        """
        获取扩展 pids，采用 DFS 算法实现
        """
        # 限制级别的最大(小)值
        assert level >= 1
        assert level <= 5

        # 加载全景ID对应的数据
        data = self.load_json(pid)
        if data is None:
            return []

        # 初始化栈、已访问节点集合和结果列表
        stack = [(pid, level)]
        visited = set()
        pids = []

        # 当栈非空时，继续遍历
        while stack:
            # 获取当前全景ID的路节点列表
            current_pid, current_level = stack.pop()
            road_pids = self.get_road_pids(current_pid, save)
            for road_pid in road_pids:
                # 如果路节点未被访问过，则将其添加到结果列表中
                if road_pid in visited:
                    continue
                visited.add(road_pid)
                pids.append(road_pid)
                # 如果当前级别大于1，则需要进一步扩展
                if current_level == 1:
                    continue
                # 遍历与路节点相连的其他节点
                for link_pid in self.get_link_pids(road_pid, save):
                    # 如果链接节点未被访问过，则将其推入栈中
                    if link_pid not in visited:
                        stack.append((link_pid, current_level - 1))

        return pids

    def write_pids(self, pids):
        """
        Write a list of unique panorama IDs to a file in the tmp directory.
        """
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
    print(pids)

    # 写到文件里边
    # grabber.write_pids(pids)

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
