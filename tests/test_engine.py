"""End-to-end-ish checks that the engine actually initializes and runs the
post-call bookkeeping without telephony (issues #1 and #3).

We drive real code: build a config, construct MojoBolResponder against the
in-repo sample flow, then run the call-teardown path (updatedf) that used
to crash on the missing pandas import.
"""
import os

import pytest

import mojobol

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SAMPLE_FLOW = os.path.join(ROOT, "samplecallflows", "mojobolsamplecallflow")

CONFIG_TEMPLATE = """\
[Server]
servername = TestServer
serverdir = {serverdir}
playertype = asterisk
tts = espeak
language = en
workflowpath = {workflowpath}
loglevel = info
logfile = logs/test.log
callsdir = calls/
reportsdir = reports/
callkey = call_id
tsformat = %Y-%b-%d-%H-%M-%S
"""


@pytest.fixture
def responder(tmp_path):
    serverdir = tmp_path / "server"
    configfile = tmp_path / "test.conf"
    configfile.write_text(
        CONFIG_TEMPLATE.format(serverdir=serverdir, workflowpath=SAMPLE_FLOW)
    )
    ms = mojobol.MojoBolResponder(str(configfile))
    return ms


def test_responder_loads_sample_workflow(responder):
    assert os.path.isdir(responder.directory)
    assert isinstance(responder.workflow.steps, list)
    assert responder.workflow.steps, "sample workflow.yml should yield steps"


def test_updatedf_uses_stdlib_csv(responder):
    call = mojobol.MojoBolCall(responder, {"agi_callerid": "5551234"})
    call.endcall()
    call.updatedf()

    datafile = os.path.join(responder.directory, "mojobol_data.csv")
    assert os.path.isfile(datafile), "updatedf should write a CSV (no pandas)"
    contents = open(datafile).read()
    assert "caller_id" in contents  # header
    assert "5551234" in contents    # the row


def test_updatedf_appends_second_call(responder):
    for cid in ("1111", "2222"):
        call = mojobol.MojoBolCall(responder, {"agi_callerid": cid})
        call.endcall()
        call.updatedf()
    datafile = os.path.join(responder.directory, "mojobol_data.csv")
    lines = [ln for ln in open(datafile).read().splitlines() if ln.strip()]
    # header + two data rows
    assert len(lines) == 3


def test_unknown_callerid_is_tolerated(responder):
    # env without agi_callerid must not raise (KeyError-handled).
    call = mojobol.MojoBolCall(responder, {})
    assert call.callerid == "Unknown"
