#!/usr/bin/python
# Copyright 2015 Mirantis, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
# Collectd plugin for getting statistics from Keystone
if __name__ == '__main__':
    import collectd_fake as collectd
else:
    import collectd

import collectd_openstack as openstack

PLUGIN_NAME = 'openstack_keystone'
INTERVAL = openstack.INTERVAL


class KeystoneStatsPlugin(openstack.CollectdPlugin):
    """ Class to report the statistics on Keystone service.

        number of tenants, users broken down by state
        number of roles
    """

    def __init__(self, *args, **kwargs):
        super(KeystoneStatsPlugin, self).__init__(*args, **kwargs)
        self.plugin = PLUGIN_NAME
        self.interval = INTERVAL

    def itermetrics(self):

        def groupby(d):
            return 'enabled' if d.get('enabled') else 'disabled'

        # tenants
        r = self.get('keystone', 'projects')
        if not r:
            self.logger.warning('Could not find Keystone tenants')
            return
        tenants_details = r.json().get('projects', [])
        status = self.count_objects_group_by(tenants_details,
                                             group_by_func=groupby)
        for s, nb in status.iteritems():
            yield {
                'plugin': PLUGIN_NAME + '_' + 'tenants',
                'type_instance': s,
                'values': nb,
                'meta': {'state': s, 'discard_hostname': True},
            }

        # users
        r = self.get('keystone', 'users')
        if not r:
            self.logger.warning('Could not find Keystone users')
            return
        users_details = r.json().get('users', [])
        status = self.count_objects_group_by(users_details,
                                             group_by_func=groupby)
        for s, nb in status.iteritems():
            yield {
                'plugin': PLUGIN_NAME + '_' + 'users',
                'type_instance': s,
                'values': nb,
                'meta': {'state': s, 'discard_hostname': True},
            }

        # roles
        r = self.get('keystone', 'roles')
        if not r:
            self.logger.warning('Could not find Keystone roles')
            return
        roles = r.json().get('roles', [])
        yield {
            'plugin': PLUGIN_NAME + '_' + 'roles',
            'type_instance': s,
            'values': len(roles),
            'meta': {'discard_hostname': True},
        }

plugin = KeystoneStatsPlugin(collectd, PLUGIN_NAME,
                             disable_check_metric=True)


def config_callback(conf):
    plugin.config_callback(conf)


def notification_callback(notification):
    plugin.notification_callback(notification)


def read_callback():
    plugin.conditional_read_callback()

if __name__ == '__main__':
    collectd.load_configuration(plugin)
    plugin.read_callback()
else:
    collectd.register_config(config_callback)
    collectd.register_notification(notification_callback)
    collectd.register_read(read_callback, INTERVAL)