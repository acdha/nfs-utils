#!/usr/bin/env python
# encoding: utf-8
"""
Export detailed NFS mount statistics in the Prometheus node_exporter text file format
"""

from __future__ import absolute_import, division, print_function, unicode_literals

from warnings import warn
import sys

# FIXME: decide how to handle the nfs-utils dependency:
mountstats = __import__('mountstats')


def get_device_data():
    with open('/proc/self/mountstats', 'r') as f:
        stats = mountstats.parse_stats_file(f)

    for device, descr in stats.items():
        device_data = mountstats.DeviceData()
        device_data.parse_stats(descr)
        if device_data.is_nfs_mountpoint():
            yield device_data.get_data()


def print_mount_data(mount_data):
    '''Emit lines in Prometheus format for the passed NFS mount'''

    common_labels = ','.join('%s="%s"' % (k, mount_data[k]) for k in ('version', 'mountpoint', 'export'))

    for k in ('age', ):
        print('nfs_mountstat_%s{%s}' % (k, common_labels), mount_data[k])

    for name, value in mount_data['events'].items():
        print('nfs_mountstat_events_%s{%s}' % (name, common_labels), value)

    for name, value in mount_data['bytes'].items():
        print('nfs_mountstat_%s{%s}' % (name, common_labels), value)

    for name, value in mount_data['transport'].items():
        print('nfs_mountstat_transport_%s{%s}' % (name, common_labels), value)

    for op, counters in mount_data['operations'].items():
        for name, value in counters.items():
            if name == 'name':
                continue
            print('nfs_mountstat_op_%s_%s{%s}' % (op, name, common_labels), value)

if __name__ == '__main__':
    for mount_data in get_device_data():
        print_mount_data(mount_data)
