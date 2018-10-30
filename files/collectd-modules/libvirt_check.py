#!/usr/bin/python
# Copyright 2016 Mirantis, Inc.
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

if __name__ == '__main__':
    import collectd_fake as collectd
else:
    import collectd

import libvirt
import collectd_base as base

NAME = 'libvirt_check'
URI = 'qemu:///system'


class LibvirtCheckPlugin(base.Base):

    def __init__(self, *args, **kwargs):
        super(LibvirtCheckPlugin, self).__init__(*args, **kwargs)
        self.plugin = NAME
        self.uri = URI

    def config_callback(self, conf):
        super(LibvirtCheckPlugin, self).config_callback(conf)

        for node in conf.children:
            if node.key == 'Uri':
                self.uri = node.values[0]
        self.logger.info("%s module initialized with URI %s" % (self.plugin, self.uri))    

    def read_callback(self):
        try:
            cnx = libvirt.openReadOnly(self.uri)
            cnx.numOfDomains()
            self.dispatch_check_metric(self.OK)
        except libvirt.libvirtError as e:
            msg = 'Fail to query libvirt ({}): {}'.format(self.uri, e)
            self.dispatch_check_metric(self.FAIL, msg)


plugin = LibvirtCheckPlugin(collectd)


def config_callback(conf):
    plugin.config_callback(conf)


def read_callback():
    plugin.read_callback()

if __name__ == '__main__':
    collectd.load_configuration(plugin)
    plugin.read_callback()
else:
    collectd.register_config(config_callback)
    collectd.register_read(read_callback)
