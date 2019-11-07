# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

import json
import logging
import os

logging.basicConfig(level=logging.INFO)
LOG = logging.getLogger(__name__)

default_name = 'insurance-voice-bot'
default_json = 'data/skill-insurance-voice-bot.json'
description = "Assistant workspace created by watson-voice-bot."


def init_skill(assistant_client):
    """Verify and/or initialize the Assistant workspace.

    If a WORKSPACE_ID is specified in the runtime environment,
    make sure that workspace exists. If no WORKSTATION_ID is
    specified then try to find it using a lookup by name.
    Name will be taken from the global default_name unless overridden
    using the WORKSPACE_NAME environment variable.

    If a workspace is not found by ID or name, then try to
    create one from the JSON in file name specified by default_json.
    Use the name as mentioned above so future lookup will find what
    was created.

    :param assistant_client: Assistant service client
    :param object environ: runtime environment variables
    :return: ID of Assistant workspace to use
    :rtype: str
    :raise Exception: When workspace is not found and cannot be created
    """

    # Get the actual workspaces
    workspaces = assistant_client.list_workspaces().get_result()[
        'workspaces']

    env_workspace_id = os.environ.get('WORKSPACE_ID')
    if env_workspace_id:
        # Optionally, we have an env var to give us a WORKSPACE_ID.
        # If one was set in the env, require that it can be found.
        LOG.info("Using WORKSPACE_ID=%s" % env_workspace_id)
        for workspace in workspaces:
            if workspace['workspace_id'] == env_workspace_id:
                ret = env_workspace_id
                break
        else:
            raise Exception("WORKSPACE_ID=%s is specified in a runtime "
                            "environment variable, but that workspace "
                            "does not exist." % env_workspace_id)
    else:
        # Find it by name. We may have already created it.
        name = os.environ.get('WORKSPACE_NAME', default_name)
        for workspace in workspaces:
            if workspace['name'] == name:
                ret = workspace['workspace_id']
                LOG.info("Found WORKSPACE_ID=%(id)s using lookup by "
                         "name=%(name)s" % {'id': ret, 'name': name})
                break
        else:
            # Not found, so create it.
            LOG.info("Creating workspace from " + default_json)

            with open(default_json) as workspace_file:
                workspace = json.load(workspace_file)

            created = assistant_client.create_workspace(
                name=name,
                description=description,
                language=workspace['language'],
                metadata=workspace['metadata'],
                intents=workspace['intents'],
                entities=workspace['entities'],
                dialog_nodes=workspace['dialog_nodes'],
                counterexamples=workspace['counterexamples']).get_result()
            ret = created['workspace_id']
            LOG.info("Created WORKSPACE_ID=%(id)s with "
                     "name=%(name)s" % {'id': ret, 'name': name})
    return ret
