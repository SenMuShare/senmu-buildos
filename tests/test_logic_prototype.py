"""Exercise the actual embedded model, not a reimplementation of its transitions."""
from html.parser import HTMLParser
from pathlib import Path
import subprocess
import unittest

ROOT = Path(__file__).resolve().parents[1]
PAGE = ROOT / "skills/senmu-build-engineering/assets/logic-prototype/job-state.html"


class ModelScript(HTMLParser):
    def __init__(self):
        super().__init__()
        self.inside = False
        self.parts = []

    def handle_starttag(self, tag, attrs):
        if tag == "script":
            self.inside = dict(attrs).get("id") == "model"

    def handle_endtag(self, tag):
        if tag == "script":
            self.inside = False

    def handle_data(self, data):
        if self.inside:
            self.parts.append(data)


class LogicPrototypeTests(unittest.TestCase):
    def model(self, assertions):
        parser = ModelScript()
        parser.feed(PAGE.read_text())
        self.assertEqual(len(parser.parts), 1)
        result = subprocess.run(["node", "-e", parser.parts[0] + "\nconst assert=require('node:assert/strict');\n" + assertions], capture_output=True, text=True, timeout=15)
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_all_guided_scenarios_have_independent_expected_outcomes(self):
        self.model("""
const expected = [["completed",1,true],["completed",2,true],["cancelled",1,false],["created",0,false]];
assert.equal(JobPrototype.scenarios.length, expected.length);
JobPrototype.scenarios.forEach((scenario,index) => {
  let state=JobPrototype.initial(), last;
  for (const action of scenario.actions) { last=JobPrototype.apply(state,action); state=last.state; }
  assert.deepEqual([state.status,state.attempt,last.accepted],expected[index]);
});
""")

    def test_rejection_preserves_state_and_inputs_are_not_mutated(self):
        self.model("""
const state=Object.freeze({status:"cancelled",attempt:2});
for(const action of [...JobPrototype.actions,"toString","__proto__"]) {
 const result=JobPrototype.apply(state,action);
 assert.equal(result.accepted,false); assert.deepEqual(result.state,state);
}
const start=Object.freeze(JobPrototype.initial());
assert.deepEqual(JobPrototype.apply(start,"submit").state,{status:"queued",attempt:1});
assert.deepEqual(start,{status:"created",attempt:0});
assert.deepEqual(JobPrototype.initial(),{status:"created",attempt:0});
""")

    def test_cancel_then_complete_does_not_revive_job(self):
        self.model("""
let state=JobPrototype.initial();
for(const action of ["submit","start","cancel"]) state=JobPrototype.apply(state,action).state;
const late=JobPrototype.apply(state,"complete");
assert.equal(late.accepted,false); assert.equal(late.state.status,"cancelled");
""")


if __name__ == "__main__":
    unittest.main()
