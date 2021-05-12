import subprocess
import asyncio
import os

def local_clean_up(paths):
    if len(paths) > 0:
        for path in paths:
            if os.path.isdir(path.parents[0]):
                subprocess.run(["rm", "-r", path.parents[0]])

async def async_clean_up(paths, nodes):
    local_clean_up(paths)
    for node in nodes:
        await node.clean_up()

def clean_up(paths, nodes):
    print("Cleaning up...")
    local_clean_up(paths)
    # We need create a new asyncio event loop and set it as the global event loop
    # As when an exception is thrown asyncio will kill the existing event loop automatically
    asyncio.set_event_loop(asyncio.new_event_loop())
    asyncio.run(clean_up_nodes(nodes))

async def clean_up_nodes(nodes):
    #AsyncSSH has already closed the connections so we need to set them up again to clean the nodes
    node_setup = [node.connect() for node in nodes]
    await asyncio.wait(node_setup)

    node_clean = [node.clean_up() for node in nodes]
    await asyncio.wait(node_clean)