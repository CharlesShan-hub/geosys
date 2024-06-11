#!/bin/bash

# Set the PYTHONPATH to include the current directory
export PYTHONPATH=.:$PYTHONPATH

# Define the base directory for the samples and scripts
# BASE_DIR="/path/to/geosys/directory" # Replace with the actual base directory
BASE_DIR=$(pwd)

# Define the location name as a variable
LOCATION_NAME="XinjiangTaZhiXiLu"

# Define the output directory for the panorama data
# OUTPUT_DIR="$BASE_DIR/samples/data/$LOCATION_NAME"
OUTPUT_DIR="$BASE_DIR/../data/$LOCATION_NAME"

# Create the output directory if it does not exist
mkdir -p "$OUTPUT_DIR/cache"
mkdir -p "$OUTPUT_DIR/tmp"
mkdir -p "$OUTPUT_DIR/pano"

# Run the grab_line_pano_info.py script and store the output
echo "Gathering panorama information..."
python "$BASE_DIR/scripts/grab_line_pano_info.py" 02015800001407191122520306A -o "$OUTPUT_DIR" || {
    echo "Error: grab_line_pano_info.py failed."
    exit 1
}

# Check if the pids.txt file exists before proceeding
PID_FILE="$OUTPUT_DIR/tmp/pids.txt"
if [ ! -f "$PID_FILE" ]; then
    echo "Error: $PID_FILE not found."
    exit 1
fi

# Download the panoramas using the download_map_pano.py script
echo "Downloading panoramas..."
while IFS= read -r pid; do
    python "$BASE_DIR/scripts/download_map_pano.py" -t bmap "$pid" -o "$OUTPUT_DIR/pano" || {
        echo "Error: download_map_pano.py failed for PID $pid."
    }
done < "$PID_FILE"

echo "🍺Panorama download complete."



# export PYTHONPATH=.:$PYTHONPATH
# # 柏油路大路 新疆 巴音郭楞蒙古自治州 塔指西路 XinjiangTaZhiXiLu
# ./scripts/grab_line_pano_info.py 02015800001407191122520306A -o samples/data/XinjiangTaZhiXiLu
# cat ./samples/data/XinjiangTaZhiXiLu/tmp/pids.txt | xargs -I {} ./scripts/download_map_pano.py -t bmap {} -o samples/data/XinjiangTaZhiXiLu/pano


# ./scripts/grab_line_pano_info.py 09002200121902171548254582G -o samples/data/test
# 路中间
# ./scripts/grab_line_pano_info.py 09002200121902031112297132L -o samples/data/test
# 路尽头
# ./scripts/grab_line_pano_info.py 09002200121902031112027092L -o samples/data/test
# 路口
# ./scripts/grab_line_pano_info.py 09002200122104201441584797C -o samples/data/test
# cat ./samples/data/test/tmp/pids.txt | xargs -I {} ./scripts/download_map_pano.py -t bmap {} -o samples/data/test/pano
# 柏油路大路 北京 西四环北路 BeijingXiSiHuanBeiLu
# ./scripts/grab_line_pano_info.py 09002200001504160309468516P -o samples/data/BeijingXiSiHuanBeiLu
# cat ./samples/data/BeijingXiSiHuanBeiLu/tmp/pids.txt | xargs -I {} ./scripts/download_map_pano.py -t bmap {} -o samples/data/BeijingXiSiHuanBeiLu/pano
# # 柏油路大路 新疆 巴音郭楞蒙古自治州 塔指西路 XinjiangTaZhiXiLu
# ./scripts/grab_line_pano_info.py 02015800001407191122520306A -o samples/data/XinjiangTaZhiXiLu
# cat ./samples/data/XinjiangTaZhiXiLu/tmp/pids.txt | xargs -I {} ./scripts/download_map_pano.py -t bmap {} -o samples/data/XinjiangTaZhiXiLu/pano
# # 柏油路大路 青海 格尔木市 盐桥南路 QinghaiYanQiaoNanLu
# ./scripts/grab_line_pano_info.py 01014400001406040759561596B -o samples/data/QinghaiYanQiaoNanLu
# cat ./samples/data/QinghaiYanQiaoNanLu/tmp/pids.txt | xargs -I {} ./scripts/download_map_pano.py -t bmap {} -o samples/data/QinghaiYanQiaoNanLu/pano
# # 柏油路适中 北京 石门路 BeijingShiMenLu
# ./scripts/grab_line_pano_info.py 09002200122305061129498735Q -o samples/data/BeijingShiMenLu
# cat ./samples/data/BeijingShiMenLu/tmp/pids.txt | xargs -I {} ./scripts/download_map_pano.py -t bmap {} -o samples/data/BeijingShiMenLu/pano
# # 柏油路小路 北京 西绦南巷 BeijingXiDiNanXiang
# ./scripts/grab_line_pano_info.py 09002200122212311225302271C -o samples/data/BeijingXiDiNanXiang
# cat ./samples/data/BeijingXiDiNanXiang/tmp/pids.txt | xargs -I {} ./scripts/download_map_pano.py -t bmap {} -o samples/data/BeijingXiDiNanXiang/pano
# # 柏油路小路 西藏 拉萨 军民路 XiZangJunMinLu
# ./scripts/grab_line_pano_info.py 09023700122108061413129035R -o samples/data/XiZangJunMinLu
# cat ./samples/data/XiZangJunMinLu/tmp/pids.txt | xargs -I {} ./scripts/download_map_pano.py -t bmap {} -o samples/data/XiZangJunMinLu/pano
# # 柏油路小路 甘肃兰州 青兰线 GansuQingLanXian
# ./scripts/grab_line_pano_info.py 01022400001405211115577146G -o samples/data/GansuQingLanXian
# cat ./samples/data/GansuQingLanXian/tmp/pids.txt | xargs -I {} ./scripts/download_map_pano.py -t bmap {} -o samples/data/GansuQingLanXian/pano
# # 水泥路大路 青海林芝 深圳大道 QinghaiShenZhenDaDao
# ./scripts/grab_line_pano_info.py 09023900011609101552411462R -o samples/data/QinghaiShenZhenDaDao
# cat ./samples/data/QinghaiShenZhenDaDao/tmp/pids.txt | xargs -I {} ./scripts/download_map_pano.py -t bmap {} -o samples/data/QinghaiShenZhenDaDao/pano
# # 水泥路适中 青海 玉树 中铁工街 QinghaiZhongTieGongJie
# ./scripts/grab_line_pano_info.py 09014500011609031348337562L -o samples/data/QinghaiZhongTieGongJie
# cat ./samples/data/QinghaiZhongTieGongJie/tmp/pids.txt | xargs -I {} ./scripts/download_map_pano.py -t bmap {} -o samples/data/QinghaiZhongTieGongJie/pano
# # 水泥路适中 青海 格尔木市 公安巷 QinghaiGongAnXiang
# ./scripts/grab_line_pano_info.py 09014400011609151530059467M -o samples/data/QinghaiGongAnXiang
# cat ./samples/data/QinghaiGongAnXiang/tmp/pids.txt | xargs -I {} ./scripts/download_map_pano.py -t bmap {} -o samples/data/QinghaiGongAnXiang/pano
# # 水泥路小路 海南琼中 水潮巷 HainanShuiChaoXiang
# ./scripts/grab_line_pano_info.py 01027200001311261334575525J -o samples/data/HainanShuiChaoXiang
# cat ./samples/data/HainanShuiChaoXiang/tmp/pids.txt | xargs -I {} ./scripts/download_map_pano.py -t bmap {} -o samples/data/HainanShuiChaoXiang/pano
# # 水泥路小路 海南五指山 甘工路 HainanGanGongLu
# ./scripts/grab_line_pano_info.py 01027200001311251413470695J -o samples/data/HainanGanGongLu
# cat ./samples/data/HainanGanGongLu/tmp/pids.txt | xargs -I {} ./scripts/download_map_pano.py -t bmap {} -o samples/data/HainanGanGongLu/pano
# # 水泥路小路 青海 玉树 双拥巷 QinghaiShuangYongXiang
# ./scripts/grab_line_pano_info.py 09014500011609031355010322L -o samples/data/QinghaiShuangYongXiang
# cat ./samples/data/QinghaiShuangYongXiang/tmp/pids.txt | xargs -I {} ./scripts/download_map_pano.py -t bmap {} -o samples/data/QinghaiShuangYongXiang/pano
# # 水泥路小路 西藏 山南市 吉波巷 XizangJiBoGang
# ./scripts/grab_line_pano_info.py 01024000001310071409157755B -o samples/data/XizangJiBoGang
# cat ./samples/data/XizangJiBoGang/tmp/pids.txt | xargs -I {} ./scripts/download_map_pano.py -t bmap {} -o samples/data/XizangJiBoGang/pano
# # 水泥路小路 河南 平顶山 新程街 HenanPingDingShan
# ./scripts/grab_line_pano_info.py 09028000121807151128137185A -o samples/data/HainanShuiChaoXiang
# cat ./samples/data/HenanPingDingShan/tmp/pids.txt | xargs -I {} ./scripts/download_map_pano.py -t bmap {} -o samples/data/HainanShuiChaoXiang/pano
# # 水泥路小路 黑龙江五大连池市 农财路 HeilongjiangNongCaiLu
# ./scripts/grab_line_pano_info.py 09031600011605161701061171B -o samples/data/HeilongjiangNongCaiLu
# cat ./samples/data/HeilongjiangNongCaiLu/tmp/pids.txt | xargs -I {} ./scripts/download_map_pano.py -t bmap {} -o samples/data/HeilongjiangNongCaiLu/pano
# # 土路小路 海南琼中 水潮巷 HainanShuiChaoXiang2
# ./scripts/grab_line_pano_info.py 01027200001311261335126065J -o samples/data/HainanShuiChaoXiang2
# cat ./samples/data/HainanShuiChaoXiang2/tmp/pids.txt | xargs -I {} ./scripts/download_map_pano.py -t bmap {} -o samples/data/HainanShuiChaoXiang2/pano
# # 地砖路 西藏 拉萨 北京中路 XizangBeijingZhongLu
# ./scripts/grab_line_pano_info.py 9ba6471e54ffab581df74dab -o samples/data/XizangBeijingZhongLu
# cat ./samples/data/XizangBeijingZhongLu/tmp/pids.txt | xargs -I {} ./scripts/download_map_pano.py -t bmap {} -o samples/data/XizangBeijingZhongLu/pano
