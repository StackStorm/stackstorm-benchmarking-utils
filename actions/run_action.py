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
from st2client.models import LiveAction

__all__ = [
    'RunActionAction'
]


class RunActionAction(Action):
    def run(self, action_ref, parameters=None, count=10, concurrency=None):
        if not concurrency:
            concurrency = count

        pool = GreenPool(concurrency)
        client = Client()
        execution_ids = []

        def schedule_action(action_ref, parameters):
            execution = LiveAction()
            execution.action = action_ref
            execution.parameters = parameters

            execution = client.liveactions.create(execution)
            execution_ids.append(execution.id)

        start_timestamp = time.time()

        for index in range(0, count):
            pool.spawn(schedule_action, action_ref, parameters)

        pool.waitall()

        end_timestamp = time.time()
        delta = (end_timestamp - start_timestamp)

        print('Scheduled %s action executions in %ss.' % (count, delta))
