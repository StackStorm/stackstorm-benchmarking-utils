# Licensed to the StackStorm, Inc ('StackStorm') under one or more
# contributor license agreements.  See the NOTICE file distributed with
# this work for additional information regarding copyright ownership.
# The ASF licenses this file to You under the Apache License, Version 2.0
# (the "License"); you may not use this file except in compliance with
# the License.  You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import time

from eventlet.greenpool import GreenPool

from st2actions.runners.pythonrunner import Action
from st2client.client import Client
from st2client.models.core import Resource as Rule


class CreateRulesAction(Action):
    def run(self, count=100):
        pool = GreenPool(count)
        client = Client()
        rule_ids = []

        name_patterns = ['key1', 'key2', 'key3', 'key4', 'key5']

        def create_rule(rule):
            try:
                rule = client.rules.create(rule)
            except Exception as e:
                # Rule already exists, ignore the error
                print(e)
                return

            rule_ids.append(rule.id)

        start_timestamp = time.time()

        index_name_pattern = 0
        for index in range(0, count):
            rule = Rule()
            rule.name = 'rule_%s' % (index)
            rule.pack = 'default'
            rule.trigger = {
                'type': 'core.st2.key_value_pair.create'
            }

            # Use uniform distribution of names so if COUNT is 100, each key
            # will be used COUNT / len(KEYS)
            if index_name_pattern >= len(name_patterns):
                index_name_pattern = 0

            pattern = name_patterns[index_name_pattern]
            rule.criteria = {
                'trigger.object.name': {
                    'pattern': (pattern),
                    'type': 'equals'
                }
            }
            rule.action = {
                'ref': 'core.noop'
            }
            index_name_pattern += 1

            pool.spawn(create_rule, rule)

        pool.waitall()

        end_timestamp = time.time()
        delta = (end_timestamp - start_timestamp)

        print('Created %d rules in %ss.' % (count, delta))
