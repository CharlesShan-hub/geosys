#!/usr/bin/env python
from pathlib import Path
from functools import partial
import click
import sys
import os
# from geosys.utils import request_data
try:
    from geosys.utils import request_data
except: # For Scons Build
    sys.path.append(os.getcwd())
    from geosys.utils import request_data
import json
import warnings
from typing import Any, Optional, Tuple, List

class BMapPanoGrabber():
    def __init__(self, out: str, **kwargs: Any) -> None:
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

    def _url_json(self, pid: str) -> str:
        """
        Generate the URL for the JSON data of a panorama.

        Eg. https://mapsv0.bdimg.com/?qt=sdata&sid=02015800001407191123100206A
        """
        return f"{self.base_url}{pid}"

    def _local_json(self, pid: str) -> Path:
        """
        Generate the local path for the JSON data of a panorama.

        Eg. .../data/XinjiangTaZhiXiLu/cache/02015800001407191123100206A.json
        """
        return Path(self.out,"cache",f"{pid}.json")

    def _save_json(self, pid: str) -> bool:
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

    def load_json(self, pid: str) -> Optional[dict]:
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
            # return None if data["result"]["error"] != 0 else data["content"]

    def get_position(self, pid: str) -> Optional[Tuple[int, int]]:
        """
        Get Position of a pano by inputting pid
        Eg. (959157787, 509606743)
        """
        data = self.load_json(pid)
        if data is None:
            raise ValueError(f"Fail to Load json of:{pid}")
        try:
            return (data[0]["RX"],data[0]["RY"])
        except:
            warnings.warn(f"{pid} dose not have position information! (omitted)")
            return None

    def get_road_pids(self, pid: str, save: bool = False) -> List[str]:
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

    def get_link_pids(self, pid: str, save: bool = False) -> List[str]:
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
        if hasattr(data[0],"Links") == False: return []
        road_data = data[0]["Links"]
        pids = []
        for node in road_data:
            pids.append(node['PID'])
        if save == True:
            for pid in pids:
                self._save_json(pid)
        return pids

    def get_expend_pids(self, pid: str, level: int = 1, dis: int = 0,
        save: bool = False) -> List[str]:
        """
        Expand the panorama IDs using a depth-first search (DFS) algorithm.

        * The default number of layers is 1, which results in a panoramic view of this street.
        * level can be set from 1 to 5. A larger number of layers will eventually lead to an
            uncontrollable number of panoramas.
        * The distance defaults to 0, which means no filtering based on distance is performed.
        * Distance is measured in meters.
        """
        # 限制级别的最大(小)值
        assert level >= 1
        assert level <= 5

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

        # 对距离进行筛选
        if dis == 0:
            return pids
        center = self.get_position(pid)
        assert isinstance(center,tuple)
        def is_within_distance(item):
            point = self.get_position(item)
            return False if not isinstance(point, tuple) else \
                (point[0]-center[0])**2+(point[1]-center[1])**2 < (100*dis)**2
        return list(filter(is_within_distance, pids))

    def write_pids(self, pids: List[str]) -> None:
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
@click.option('-o', '--out', default='', help="output path")
@click.option('-d', '--dis', default=0, help="distance filter")
@click.option('-l', '--level', default=2, help="expand level")
def main(pid, out, dis, level):
    # 初始化下载器
    grabber = BMapPanoGrabber(out)

    # 路中间: 得到某条道路的 PID，可以保存某条街道所有 pid 对应的 json
    # print(grabber.get_road_pids(pid))

    # 路口: 得到某个道路尽头节点的相连的节点的 PID，可以保存节点对应的所有 pid的 json
    # print(grabber.get_link_pids(pid))

    # 递归扩展 PID(别设置的太大，防止死循环)
    # pids = grabber.get_expend_pids(pid, level=2, save=True)
    # print(pids)

    # 递归扩展 PID(别设置的太大，防止死循环),设置距离200米
    # pids = grabber.get_expend_pids(pid, level=5,dis=200, save=True)
    # print(pids)

    # 进行下载
    pids = grabber.get_expend_pids(pid, level=level,dis=dis, save=True)

    # 写到文件里边
    grabber.write_pids(pids)

if __name__ == "__main__":
    main()
