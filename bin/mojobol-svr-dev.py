#!/usr/bin/python3
# -*- coding: utf-8 -*-
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parents[1] / "libs"))
from mojoasteriskplayer import *
from datetime import *
from mojobol import *
if __name__ == "__main__":
    env = read_agi_environment()
    config = resolve_config_path(sys.argv[1] if len(sys.argv) > 1 else None)
    ms = MojoBolResponder(config)
    call = MojoBolCall(ms, env)
    p = call.responder.parse_workflow(call)
    call.endcall()
    call.updatedf()