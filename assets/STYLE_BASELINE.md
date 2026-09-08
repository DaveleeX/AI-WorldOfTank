# 坦克风格基准

用户明确要求沿用本工程已有坦克风格。风格依据：

- `/Users/lee/GPT6test/tank_series/README.md`
- `/Users/lee/GPT6test/tank_series/01_challenger2.blend` 与同名 PNG
- `/Users/lee/GPT6test/tank_series/02_leopard2a7.blend` 与同名 PNG
- `/Users/lee/GPT6test/tank_series/04_abramsx.blend` 与同名 PNG
- 首辆参考：`/Users/lee/GPT6test/reference_tank.blend`、`tank_final.png`

保留原工程 Q 版比例、柔和倒角、哑光涂装、履带轮组形式和设备造型。已有国家直接使用原资产；补充国家和装备沿用工程建模函数、材料和细节密度。参考实车用于辨识特征，不据此改成另一种美术风格。废土场景与氛围要求不等于授权重新设计坦克。

曾擅自拉长/压低六辆车、重造轮组并添加自定义迷彩；这些修改已整体撤回。游戏导出必须保留源材质的实际颜色，不能用 material.diffuse_color 覆盖原程序化涂装。

`restore-source-finishes.py` 通过 Blender MCP 从原始文件重新导出，原图案使用材质本色贴图，其他表面采样顶点本色；只采样材质本色，保留原模型尺寸、分组及原 LOD 设置，不烘焙动态车辆的光照。导出结果需要与上述原图对照检查，不能只凭战斗逻辑测试宣称视觉合格。

验证记录：浏览器对照原图查看中国车、豹 2 和 AbramsX；豹 2 原迷彩图案与 AbramsX 灰白涂装/蓝侧条已保留。六车模型、18 种装备组合的炮口一致性、资源检查与生产构建通过。运行环境光照与原图棚拍光照不同，未声称画面逐像素一致。
