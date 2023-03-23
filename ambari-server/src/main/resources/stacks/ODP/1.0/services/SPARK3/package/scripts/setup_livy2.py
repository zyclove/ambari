#!/usr/bin/python2
"""
Licensed to the Apache Software Foundation (ASF) under one
or more contributor license agreements.  See the NOTICE file
distributed with this work for additional information
regarding copyright ownership.  The ASF licenses this file
to you under the Apache License, Version 2.0 (the
"License"); you may not use this file except in compliance
with the License.  You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.

"""

import os
from resource_management.libraries.functions.default import default
from resource_management.libraries.functions.generate_logfeeder_input_config import generate_logfeeder_input_config
from resource_management import Directory, File, PropertiesFile, Template, InlineTemplate, format


def setup_livy(env, type, upgrade_type = None, action = None):
  import params

  Directory([params.livy3_pid_dir, params.livy3_log_dir],
            owner=params.livy3_user,
            group=params.user_group,
            mode=0775,
            cd_access='a',
            create_parents=True
  )
  if type == 'server' and action == 'config':
    params.HdfsResource(params.livy3_hdfs_user_dir,
                        type="directory",
                        action="create_on_execute",
                        owner=params.livy3_user,
                        mode=0775
    )
    params.HdfsResource(None, action="execute")

    if params.livy3_recovery_store == 'filesystem':
      params.HdfsResource(params.livy3_recovery_dir,
                          type="directory",
                          action="create_on_execute",
                          owner=params.livy3_user,
                          mode=0700
         )
      params.HdfsResource(None, action="execute")

    generate_logfeeder_input_config('spark3', Template("input.config-spark3.json.j2", extra_imports=[default]))

  # create livy-env.sh in etc/conf dir
  File(os.path.join(params.livy3_conf, 'livy-env.sh'),
       owner=params.livy3_user,
       group=params.livy3_group,
       content=InlineTemplate(params.livy3_env_sh),
       mode=0644,
  )

  # create livy-client.conf in etc/conf dir
  PropertiesFile(format("{livy3_conf}/livy-client.conf"),
                properties = params.config['configurations']['livy3-client-conf'],
                key_value_delimiter = " ",
                owner=params.livy3_user,
                group=params.livy3_group,
  )

  # create livy.conf in etc/conf dir
  PropertiesFile(format("{livy3_conf}/livy.conf"),
                properties = params.config['configurations']['livy3-conf'],
                key_value_delimiter = " ",
                owner=params.livy3_user,
                group=params.livy3_group,
  )

  # create log4j.properties in etc/conf dir
  File(os.path.join(params.livy3_conf, 'log4j.properties'),
       owner=params.livy3_user,
       group=params.livy3_group,
       content=params.livy3_log4j_properties,
       mode=0644,
  )

  # create spark-blacklist.properties in etc/conf dir
  File(os.path.join(params.livy3_conf, 'spark-blacklist.conf'),
       owner=params.livy3_user,
       group=params.livy3_group,
       content=params.livy3_spark_blacklist_properties,
       mode=0644,
  )

  Directory(params.livy3_logs_dir,
            owner=params.livy3_user,
            group=params.livy3_group,
            mode=0755,
  )

