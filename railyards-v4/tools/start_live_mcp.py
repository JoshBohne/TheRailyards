import bpy
def _start():
    try:
        srv=getattr(bpy.types,'blendermcp_server',None)
        if srv:
            try:srv.stop()
            except Exception:pass
        import blender_mcp
        bpy.context.scene.blendermcp_port=9877
        bpy.types.blendermcp_server=blender_mcp.BlenderMCPServer(port=9877)
        bpy.types.blendermcp_server.start()
        bpy.context.scene.blendermcp_server_running=True
        print('Blender MCP server started on 9877',flush=True)
    except Exception as e:
        print('start failed',repr(e),flush=True)
    return None
bpy.app.timers.register(_start,first_interval=3.0)
