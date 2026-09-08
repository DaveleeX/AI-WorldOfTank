# 美术参考与重建记录

2026-09-08 搜索并依据图像中的可见外形进行 Blender 参数化重建，不将网页图片直接用作游戏纹理。

- 中国 99A：[军博实车正前侧图](https://commons.wikimedia.org/wiki/File:ZTZ-99A_tank_front_right_20170902.jpg)：楔形炮塔、分块反应装甲、六对负重轮、车顶观瞄与反制设备。
- 法国勒克莱尔：[索米尔坦克博物馆](https://thearmoredpatrol.com/2016/03/10/saumur-tank-museum-part-5/)：窄炮塔、尾部自动装填舱、前部装甲模块、六对负重轮。
- 日本 10 式：[车辆照片](https://motor-fan.jp/mf/article/17102/04_img_6843/)：低矮折面炮塔、模块侧装甲、紧凑车体、五对负重轮。搜索摘要中的轮数可能错误，建模未采用摘要的六轮说法。
- 场景：[World of Tanks 地图改进](https://worldoftanks.com/en/news/updates/update-1-18-map-rebalance/) 与 [Winterberg](https://wargaming.com/en/news/tips-for-world-of-tanks-update/)：破损立面、宽主干道、横向射界、散布掩体、冷暖空气透视。

废土风使用自制锈蚀钢材、低饱和涂装、裸露楼板、枯树和废弃油井；没有复制《无主之地》《疯狂麦克斯》或《坦克世界》的模型、贴图或游戏地图。

## 精度与渲染

三款新增坦克使用原工程 common.py 同一套倒角、轮组、闭环履带、舱盖、炮管、螺栓、光学设备函数；每车超过 1,100 个源零件。导出使用原有三车一致的 0.38 decimation 比例。源模型保存在 assets/blender 和 assets/worlds；外形属于同系列风格化重建，不是工程测量模型。

四个静态世界在 Blender MCP 中创建。碰撞数据与地图建模共用 maps.json。Cycles DIFFUSE 烘焙仅勾选 INDIRECT，不勾选 DIRECT 或 COLOR；2048²、16 samples。场景里没有坦克、炮弹或爆炸。Three.js 将烘焙图作为线性 lightMap，动态坦克另用实时天空光和太阳阴影；静态材质的实时天空漫反射在着色器中关闭。
