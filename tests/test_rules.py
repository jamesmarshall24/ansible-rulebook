#  Copyright 2022 Red Hat, Inc.
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.

import asyncio
import os
from queue import Queue

import pytest
import yaml
from drools.ruleset import assert_fact as set_fact, post

from ansible_rulebook.rule_generator import generate_rulesets
from ansible_rulebook.rules_parser import parse_rule_sets

HERE = os.path.dirname(os.path.abspath(__file__))


@pytest.mark.asyncio
async def test_generate_rules():
    os.chdir(HERE)
    with open("rules/rules.yml") as f:
        data = yaml.safe_load(f.read())
    with open("playbooks/inventory.yml") as f:
        inventory = yaml.safe_load(f.read())

    rulesets = parse_rule_sets(data)
    print(rulesets)
    ruleset_queues = [(ruleset, Queue()) for ruleset in rulesets]
    durable_rulesets = generate_rulesets(ruleset_queues, dict(), inventory)

    durable_rulesets[0].plan.queue = asyncio.Queue()
    print(durable_rulesets[0].ruleset.define())
    set_fact("Demo rules", {"payload": {"text": "hello"}})

    assert durable_rulesets[0].plan.queue.get_nowait().action == "slack"
    assert durable_rulesets[0].plan.queue.get_nowait().rule == "assert fact"
    assert durable_rulesets[0].plan.queue.get_nowait().ruleset == "Demo rules"


@pytest.mark.asyncio
async def test_generate_rules_multiple_conditions_any():
    os.chdir(HERE)
    with open("rules/rules_with_multiple_conditions.yml") as f:
        data = yaml.safe_load(f.read())
    with open("playbooks/inventory.yml") as f:
        inventory = yaml.safe_load(f.read())

    rulesets = parse_rule_sets(data)
    print(rulesets)
    ruleset_queues = [(ruleset, Queue()) for ruleset in rulesets]
    durable_rulesets = generate_rulesets(ruleset_queues, dict(), inventory)

    durable_rulesets[0].plan.queue = asyncio.Queue()
    print(durable_rulesets[0].ruleset.define())

    post("Demo rules multiple conditions any", {"i": 0})
    assert durable_rulesets[0].plan.queue.get_nowait().action == "debug"
    post("Demo rules multiple conditions any", {"i": 1})
    assert durable_rulesets[0].plan.queue.get_nowait().action == "debug"


@pytest.mark.asyncio
async def test_generate_rules_multiple_conditions_all():
    os.chdir(HERE)
    with open("rules/rules_with_multiple_conditions2.yml") as f:
        data = yaml.safe_load(f.read())
    with open("playbooks/inventory.yml") as f:
        inventory = yaml.safe_load(f.read())

    rulesets = parse_rule_sets(data)
    print(rulesets)
    ruleset_queues = [(ruleset, Queue()) for ruleset in rulesets]
    durable_rulesets = generate_rulesets(ruleset_queues, dict(), inventory)

    durable_rulesets[0].plan.queue = asyncio.Queue()
    print(durable_rulesets[0].ruleset.define())

    post("Demo rules multiple conditions all", {"i": 0})
    assert durable_rulesets[0].plan.queue.qsize() == 0
    post("Demo rules multiple conditions all", {"i": 1})
    assert durable_rulesets[0].plan.queue.qsize() == 1
    assert durable_rulesets[0].plan.queue.get_nowait().action == "debug"


@pytest.mark.asyncio
async def test_generate_rules_multiple_conditions_all_3():
    os.chdir(HERE)
    with open("rules/rules_with_multiple_conditions3.yml") as f:
        data = yaml.safe_load(f.read())
    with open("playbooks/inventory.yml") as f:
        inventory = yaml.safe_load(f.read())

    rulesets = parse_rule_sets(data)
    print(rulesets)
    ruleset_queues = [(ruleset, Queue()) for ruleset in rulesets]
    durable_rulesets = generate_rulesets(ruleset_queues, dict(), inventory)

    durable_rulesets[0].plan.queue = asyncio.Queue()
    print(durable_rulesets[0].ruleset.define())

    post("Demo rules multiple conditions reference assignment", {"i": 0})
    assert durable_rulesets[0].plan.queue.qsize() == 0
    post("Demo rules multiple conditions reference assignment", {"i": 1})
    assert durable_rulesets[0].plan.queue.qsize() == 0
    post("Demo rules multiple conditions reference assignment", {"i": 2})
    assert durable_rulesets[0].plan.queue.qsize() == 1
    assert durable_rulesets[0].plan.queue.get_nowait().action == "debug"
