from pathlib import Path
import shutil,json
root=Path('/Users/lee/GPT6test/wasteland_tanks');stage=root/'assets/world-build'
report=json.loads((stage/'assets/blender/bake-report-final.json').read_text());assert len(report)==4
(root/'public/battlefields').mkdir(exist_ok=True);(root/'assets/worlds').mkdir(exist_ok=True)
for d in report:
 slug=d['map']
 for suffix in ['.glb','-indirect.png','-albedo.png']:
  shutil.copy2(stage/f'public/maps/{slug}{suffix}',root/f'public/battlefields/{slug}{suffix}')
 shutil.copy2(stage/f'assets/blender/{slug}-world.blend',root/f'assets/worlds/{slug}.blend')
shutil.copy2(stage/'assets/blender/bake-report-final.json',root/'assets/worlds/bake-report.json')
print('Four final authored worlds copied')
