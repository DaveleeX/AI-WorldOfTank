# IRON FRONT · 废土战线

可游玩的第三人称 3D 坦克歼灭战。运行 `npm run dev` 后访问 http://localhost:3000 。建议使用支持 WebGL2 的桌面浏览器。

## 游玩

选择中国 99A、美国 AbramsX、英国挑战者 2、法国勒克莱尔、德国豹 2A7、日本 10 式，在沙漠、城市、泥泞乡村和雪地展开 5v5 对战。玩家与 4 辆 AI 队友对阵 5 辆敌车；玩家阵亡后继续观战，直到一方全灭。

- W / S：前进 / 倒车；A / D：车身转向。
- 鼠标：独立转动炮塔和第三人称相机；点击战场锁定鼠标。
- 左键：发射，按住可连续装填发射；右键：按住放大瞄准。
- Shift：消耗能量加速，松开恢复；P / Esc：暂停。
- 胜利奖励 500 积分，每辆玩家击毁的敌车额外 100 积分；失败不奖励。
- 炮管、履带、弹药、装甲可永久采购或换装，影响实际伤害、装填、机动、能量、溅射和生命值。
- 积分和装备保存在当前设备浏览器中，初始积分为 0。

## 模型与场景

六款坦克全部使用 Blender 模型。英国、德国、美国复用工程既有资产；中国、法国、日本通过运行中的 Blender MCP，依据实车参考图与原工程的细节建模函数制作。新增模型每款约 1,100 个零件，使用与原车型相同的游戏减面比例。保留独立炮塔，所有车辆不烘焙光照。

四个静态战场通过 Blender MCP 创建，与游戏碰撞数据共用同一份布局。每个环境用 Cycles 烘焙 2048×2048 的纯间接漫反射贴图（16 samples），不包含直接光和材质颜色；游戏中通过线性 lightMap 加载，实时太阳提供直射和阴影。动态车体接受实时天空光；静态材质在着色器中禁用实时天空漫反射，避免与烘焙光重复。坦克、炮弹、爆炸均不在静态烘焙场景中。

- `assets/blender/*.blend`：三款新车；`assets/worlds/*.blend`：四个静态世界的可编辑源文件。
- `assets/REFERENCES.md`：图片来源及外形重建记录。
- `assets/blender/tank-report.json`、`assets/worlds/bake-report.json`：建模与实际烘焙记录。
- `scripts/build_missing_tanks.py`、`build_worlds_final.py`：Blender MCP 建模脚本。
- `lib/battle.mjs`：战斗、AI、装备和结算逻辑。
- `lib/renderer.ts`：Three.js 模型、光照、相机与特效。

## 验证与范围

`node scripts/test-battle.mjs` 验证 5v5、装备、移动能量、遮挡和命中、胜负与四地图 AI 战斗可结束；`node scripts/test-models.mjs` 验证六款实际 GLB 的独立炮塔；`node scripts/test-assets.mjs` 验证单场景导出、精度、UV 和烘焙图。`npx tsc --noEmit` 与 `npm run build` 检查类型和发布构建。

这是单人 AI 对战游戏，不包含联网多人。地图为 360 米开放战场，弹道和命中区为街机化水平模拟。美术保留已有坦克的风格化比例，不是实车精密工程复刻。烘焙采用实时游戏预算，不声称达到商业大作质量。本轮未进行浏览器画面和鼠标操作实测；Blender 资产另有渲染检查。进度不跨设备同步。
