"""The conversation this process is working on.

The terminal sets it with use(); every other module reads ID and WORKSPACE from here. In the notebook these
were the constants CONVERSATION_ID and WORKSPACE.
"""
from .. import config

ID = None          # conversation name = docker container name = folder name under conversation_dir
WORKSPACE = None   # that folder on this machine = the sandbox's /workspace


def use(conversation_id):
    """Switch to a conversation (None = none loaded)."""
    global ID, WORKSPACE
    ID = conversation_id
    WORKSPACE = config.CONV_DIR / conversation_id if conversation_id else None
