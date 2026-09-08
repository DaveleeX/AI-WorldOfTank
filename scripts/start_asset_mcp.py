import sys
sys.path.insert(0,'/Users/lee/Library/Application Support/Blender/5.2/scripts/addons')
import blender_mcp_addon
from blender_mcp_addon.cli import cli_execute
cli_execute(['--host','127.0.0.1','--port','9881'])
