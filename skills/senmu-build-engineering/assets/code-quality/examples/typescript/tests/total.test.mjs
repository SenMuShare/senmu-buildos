import test from "node:test";
import assert from "node:assert/strict";
import { total } from "../.build/pricing/index.js";

test("discount", () => assert.equal(total(100, 20), 80));
test("zero", () => assert.equal(total(100, 0), 100));
test("negative total", () => assert.throws(() => total(10, 20), /negative total/));
