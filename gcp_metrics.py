#!/usr/bin/env python

##########################################################################################################################
#                                                                                                                        #
# Google Cloud Infrastructure Monitoring Script                                                                          #
# Python version 2.7                                                                                                     #
# Created By - Pritish Debnath                                                                                                  #
# Creation Date - 11/27/2020                                                                                             #
# Usage: gcp_metrics.py --project <project_name> --host {HOST.HOST} ----metric <kubernetes api>                          #
# Example :                                                                                                              #
#           To Fetch Metrics for an stackdriver endpoint -                                                               #
#           gcp_metrics.py --project {$PROJECT_ID} --metric kubernetes.io/container/cpu/limit_utilization                #
#   --host {Cluster Host}                                                                                                #
#                                                                                                                        #
#           To Discover containers --                                                                                    #
#           gcp_metrics.py --project {$PROJECT_ID} --metric kubernetes.io/container/cpu/limit_utilization                #
#   --host {Cluster Host} --discover containerkey                                                                        #
#                                                                                                                        #
#           To view Data in dataframe   --                                                                               #
#           gcp_metrics.py --project {$PROJECT_ID} --metric kubernetes.io/container/cpu/limit_utilization                #
#   --host {Cluster Host} --iloc00                                                                                       #
#                                                                                                                        #
#           To Discover Cluster --                                                                                       #
#            gcp_metrics.py --project {$PROJECT_ID} --metric kubernetes.io/node/cpu/allocatable_utilization              #
#            --subdomain {$SUBDOMAIN} --discover cluster                                                                 #
#                                                                                                                        #
##########################################################################################################################

# Importing Module

import sys
import argparse
from gcloud import monitoring
import datetime
import collections
import subprocess
import json
import os

PARSER = argparse.ArgumentParser(
    description='Google Cloud Monitoring API Command Line\nWebsite: https://github.com/odin-public/gcpmetrics',
    formatter_class=argparse.RawDescriptionHelpFormatter
)

PARSER.add_argument('--keyfile', help='Goolge Cloud Platform service account key file.', metavar='FILE')
PARSER.add_argument('--project', help='Project ID.', metavar='ID')
PARSER.add_argument('--preset', help='Preset ID, like http_response_5xx_sum, etc.', metavar='ID')
PARSER.add_argument('--metric', help='Metric ID as defined by Google Monitoring API.', metavar='ID')
PARSER.add_argument('--service', help='Service ID.', metavar='ID')
PARSER.add_argument('--days', default=0, help='Days from now to calculate the query start date.', metavar='INT')
PARSER.add_argument('--hours', default=0, help='Hours from now to calculate the query start date.', metavar='INT')
PARSER.add_argument('--minutes', default=5, help='Minutes from now to calculate the query start date.', metavar='INT')
PARSER.add_argument('--resource-filter', default=None, help='Filter of resources in the var:val[,var:val] format.', metavar='S')
PARSER.add_argument('--metric-filter', default=None, help='Filter of metrics in the var:val[,var:val] format.', metavar='S')
PARSER.add_argument('--align', default=None, help='Alignment of data ALIGN_NONE, ALIGN_SUM. etc.', metavar='A')
PARSER.add_argument('--reduce', default='REDUCE_NONE', help='Reduce of data REDUCE_NONE, REDUCE_SUM, etc.', metavar='R')
PARSER.add_argument('--reduce-grouping', default=None, help='Reduce grouping in the var1[,var2] format.', metavar='R')
PARSER.add_argument('--iloc00', default=True, action='store_false', help='Print value from the table index [0:0] only.')
PARSER.add_argument('--label', default=None, help='Provide labels on metrics to fetch',metavar='S')
PARSER.add_argument('--host', default=None, help='gcp node',metavar='S')
PARSER.add_argument('--discover', default=None, help='Discovery of kubernetes cluster and nodes and pods', metavar='S')
PARSER.add_argument('--subdomain', default=None, help='subdomain like cloud.opentext.com')
PARSER.add_argument('--count', default=None, action='store_true', help='Counts Number of cluster resources')

# Classs for fetching GCP Metrices using google cloud python module
class fetchmetrics():

    # Performing the query for provided api end-point
    def perform_query(self, client, metric_id, labels, align, reduce, days, hours, minutes,resource_filter, metric_filter, reduce_grouping, iloc00):
        query = client.query(
            metric_type=metric_id,
            days=days,
            hours=hours,
            minutes=minutes
        )

        if resource_filter:
            query = query.select_resources(**resource_filter)

        if metric_filter:
            query = query.select_metrics(**metric_filter)

        if align:
            delta = datetime.timedelta(days=days, hours=hours, minutes=minutes)
            seconds = delta.total_seconds()
            if not iloc00:
                print 'ALIGN: {} seconds: {}'.format(align, seconds)
            query = query.align(align, seconds=seconds)

        if reduce:
            if not iloc00:
                print 'REDUCE: {} grouping: {}'.format(reduce, reduce_grouping)
            if reduce_grouping:
                query = query.reduce(reduce, *reduce_grouping)
            else:
                query = query.reduce(reduce)

        # Checking if any labels is provided to reduce the columns in dataframe and filter only relevant column.
        # Please note: Use it only if needed in extreme case as it leads removal of non-unique data which is highly possible

        if len(labels) !=0:
            dataframe = query.as_dataframe(labels=labels)

        else:
            dataframe = query.as_dataframe()

        # If iloc00 is set it will print the dataframe.
        # Without iloc00 (defaut is true as per argparse) will provide dictionary data can be queried against its key for single value which can
        # be used in zabbix

        if iloc00:
            if len(dataframe) == 0:
                return 0

            else:
                dataframe = (dataframe.to_dict(orient='lines'))

                # Function to remove unicode character from dictionary
                def convert(dataframe):
                    if isinstance(dataframe, basestring):
                        return str(dataframe)
                    elif isinstance(dataframe, collections.Mapping):
                        return dict(map(convert, dataframe.iteritems()))
                    elif isinstance(dataframe, collections.Iterable):
                        return type(dataframe)(map(convert, dataframe))
                    else:
                        return dataframe

                return convert(dataframe)

        else:
            print 'QUERY: {}'.format(query.filter)
            return dataframe


    def process(self, keyfile, project_id, metric_id, labels, align, reduce, days, hours, minutes,resource_filter, metric_filter, reduce_grouping, iloc00):
        _file = keyfile
        client = monitoring.Client.from_service_account_json(_file, project=project_id)

        return self.perform_query(client, metric_id, labels, align, reduce, days, hours, minutes, resource_filter, metric_filter, reduce_grouping, iloc00)

fetchmetrics = fetchmetrics()

# Class for labels, it can vary based on different api endpoint.
# Adding labels while querying GCP metrics only shows columns that is mentioned in label
class metricslabel():
    def kubecontainer(self):
        labels = ['cluster_name', 'pod_name']
        return labels

    def kubenodes(self):
        labels = ['cluster_name', 'node_name']
        return labels

metricslabel = metricslabel()

def error(message):
    sys.stderr.write('error: {}'.format(message))
    print
    print
    PARSER.print_help()
    sys.exit(1)

# function to check for NaN value in data. It looks for last entry without NaN value.
# ALIGN_MEAN or ALIGN_NEXT_OLDER is not available for every endpoint.
def validation(data):
    if data != 0:
        for key in data:
            for i, value in enumerate(reversed(data[key])):
                if str(value) == 'nan':
                    if i == (len(data[key])- 1):
                        data[key] = 'ZBX_NOTSUPPORTED'
                    else:
                        continue
                else:
                    data[key] = [value]
                    break

    return data

# function for dicovery of instance or items for gcp
def discovery(discovered_list, type, project, subdomain):
    if type in ('clusterkey', 'nodekey', 'podkey', 'nodedaemonkey'):
        print('{"data": [')
        for i in discovered_list:
            if i == discovered_list[-1]:
                print(json.dumps(i))
            else:
                print(json.dumps(i) + ',')
        print(']}')

    else:
        var = [{"Data": [{"{#INSTANCE}": i, "{#MTYPE}": type, "{#PROJECT}": project, "{#SUBDOMAIN}": subdomain} for i in discovered_list]}]

        print('{"data": [')
        for i in var[0]['Data']:
            if i == var[0]['Data'][-1]:
                print(json.dumps(i))
            else:
                print(json.dumps(i) + ',')
        print(']}')


# sending the metrices to zabbix
def send_to_zabbix(host, item_key_prefix, type, count):
    try:
        if count:
            cmd = '/usr/bin/zabbix_sender -v -z localhost -i ' + '/tmp/{0}_{1}_count.tmp'.format(host, item_key_prefix)
            subprocess.check_output(cmd, shell=True)

            os.remove('/tmp/{0}_{1}_count.tmp'.format(host, item_key_prefix))

        else:
            cmd = '/usr/bin/zabbix_sender -v -z localhost -i ' + '/tmp/{0}_{1}_{2}.tmp'.format(host,item_key_prefix, type)
            subprocess.check_output(cmd, shell=True)

            os.remove('/tmp/{0}_{1}_{2}.tmp'.format(host, item_key_prefix, type))

    except subprocess.CalledProcessError:
        print('GCP KEY ERROR!')
        sys.exit()

# querying the dictionary data and sending the metrices to zabbix
def querymetrics(data, metric_id, host, project_id, num):
    api = metric_id.split('/')
    item_key_prefix = api[2]
    if len(api) != 3:
        for i in range(3, len(api)):
            item_key_prefix = item_key_prefix + '_' + api[i]


    if data != 0:
        class gcpmetric():
            def container(self):
                if num:
                    with open('/tmp/{0}_{1}_count.tmp'.format(host, item_key_prefix), 'w') as f:
                        f.write('{} {} {}\n'.format(host, 'pod[count]', len(set(key[6] for key in data))))
                        f.write('{} {} {}\n'.format(host, 'namespace[count]', len(set(key[5] for key in data))))
                        f.write('{} {} {}\n'.format(host, 'container[count]', len(set(key[4] for key in data))))

                else:
                    with open('/tmp/{0}_{1}_{2}.tmp'.format(host,item_key_prefix, api[1]), 'w') as f:
                        for key, value in data.items():
                            item_key = 'gcp_metric_cluster' + '[' + api[1].upper() + ',' + key[1] + ',' + key[6] + ',' + \
                                       key[4] + ',' + '_'.join([key[-len(key) + count] for count in range(7, len(key)) if
                                                                len(key) > 7]) + ''.join(
                                [',' if len(key) > 7 else '']) + item_key_prefix + ']'
                            value = value[0]
                            f.write('{} {} {}\n'.format(host, item_key, value))

            def node_daemon(self):
                with open('/tmp/{0}_{1}_{2}.tmp'.format(host,item_key_prefix, api[1]), 'w') as f:
                    for key, value in data.items():
                        item_key = 'gcp_metric_cluster' + '[' + api[1].upper() + ',' + key[4] + ',' + '_'.join(
                            [key[-len(key) + count] for count in range(5, len(key)) if
                             len(key) > 5]) + ''.join(
                            [',' if len(key) > 5 else '']) + item_key_prefix + ']'
                        value = value[0]
                        f.write('{} {} {}\n'.format(host, item_key, value))

            def node(self):
                with open('/tmp/{0}_{1}_{2}.tmp'.format(host,item_key_prefix, api[1]), 'w') as f:
                    for key, value in data.items():
                        item_key = 'gcp_metric_cluster' + '[' + api[1].upper() + ',' + key[4] + ',' + '_'.join(
                            [key[-len(key) + count] for count in range(5, len(key)) if
                             len(key) > 5]) + ''.join(
                            [',' if len(key) > 5 else '']) + item_key_prefix + ']'
                        value = value[0]
                        f.write('{} {} {}\n'.format(host, item_key, value))

            def pod(self):
                with open('/tmp/{0}_{1}_{2}.tmp'.format(host,item_key_prefix, api[1]), 'w') as f:
                    for key, value in data.items():
                        item_key = 'gcp_metric_cluster' + '[' + api[1].upper() + ',' + key[5] + ',' + '_'.join([key[-len(key) + count] for count in range(6, len(key)) if
                                                 len(key) > 6]) + ''.join(
                            [',' if len(key) > 6 else '']) + item_key_prefix + ']'
                        value = value[0]
                        f.write('{} {} {}\n'.format(host, item_key, value))

            def compute(self):
                pass

            def agent(self):
                pass

        gcpmetric = gcpmetric()

        gcp_type = {'container': gcpmetric.container, 'node_daemon': gcpmetric.node_daemon, 'node': gcpmetric.node,
                    'pod': gcpmetric.pod, 'compute': gcpmetric.compute, 'agent': gcpmetric.agent}

        if metric_id.split('.')[0] not in ('compute', 'agent'):
            gcp_type[api[1]]()
        else:
            gcp_type[metric_id.split('.')[0]]()

        if 'kubernetes' in api[0]:
            send_to_zabbix(host, item_key_prefix, api[1], num)
        else:
            send_to_zabbix(project_id, item_key_prefix, api[1], num)


def main():
    args_dict = vars(PARSER.parse_args())

    metric_type = {'kubecontainer': metricslabel.kubecontainer, 'kubenodes': metricslabel.kubenodes}

    if args_dict['label']:
        labels = metric_type[args_dict['label']]()
    else:
        labels = ''

    if args_dict['service']:
        append = 'module_id:{}'.format(args_dict['service'])
        if args_dict['resource_filter'] is None:
            args_dict['resource_filter'] = append
        else:
            args_dict['resource_filter'] += append

    def process_filter(_filter):
        if not _filter:
            return None
        _filter = _filter.split(',')
        _ret = {}
        for res in _filter:
            key, value = res.split(':')
            _ret[key] = value
        return _ret

    # if the host is a cluster than add a resource filter.
    if args_dict['host']:
        if 'cluster' in args_dict['host']:
            args_dict['resource_filter'] = 'cluster_name:' + args_dict['host'].split('.cluster')[0]

    # data re-formatting for simpler use going forward
    resource_filter = process_filter(args_dict['resource_filter'])
    metric_filter = process_filter(args_dict['metric_filter'])

    if args_dict['reduce_grouping']:
        args_dict['reduce_grouping'] = args_dict['reduce_grouping'].split(',')

    data = fetchmetrics.process(
        '/opt/gcp/gcproject/{}/keyfile.json'.format(args_dict['project']),
        args_dict['project'],
        args_dict['metric'],
        labels,
        args_dict['align'],
        args_dict['reduce'],
        int(args_dict['days']),
        int(args_dict['hours']),
        int(args_dict['minutes']),
        resource_filter,
        metric_filter,
        args_dict['reduce_grouping'],
        args_dict['iloc00']
    )

    # check if the request is for dicovery
    if args_dict['discover'] and data !=0:
        class discovermetrices:
            def cluster(self):
                discovery(set(key[3] for key in data), 'K8CLUSTER', args_dict['project'], args_dict['subdomain'])

            def instance(self):
                discovery(set(key[3] for key in data), 'INSTANCE', args_dict['project'], args_dict['subdomain'])

            def clusterkey(self):
                discovery_list = [{"{#CONTAINER}": key[4], "{#NAMESPACE}": key[5], "{#POD}": key[6],
                                   "{#PROJECT}": args_dict['project'],
                                   "{#CLUSTER}": args_dict['host'].split('.cluster')[0], "{#EXTRA}": '_'.join(
                        [key[-len(key) + count] for count in range(7, len(key)) if len(key) > 7])} for key in data]

                discovery(discovery_list, 'clusterkey', args_dict['project'], args_dict['subdomain'])

            def nodekey(self):
                discovery_list = [
                    {"{#NODE}": key[4], "{#PROJECT}": args_dict['project'],
                     "{#CLUSTER}": args_dict['host'].split('.cluster')[0],
                     "{#EXTRA}": '_'.join([key[-len(key) + count] for count in range(5, len(key)) if len(key) > 5])} for
                    key in data]

                discovery(discovery_list, 'nodekey', args_dict['project'], args_dict['subdomain'])

            def podkey(self):
                discovery_list = [
                    {"{#POD}": key[5], "{#NAMESPACE}": key[4], "{#PROJECT}": args_dict['project'],
                     "{#CLUSTER}": args_dict['host'].split('.cluster')[0],
                     "{#EXTRA}": '_'.join([key[-len(key) + count] for count in range(6, len(key)) if len(key) > 6])} for
                    key in data]

                discovery(discovery_list, 'podkey', args_dict['project'], args_dict['subdomain'])

            def nodedaemonkey(self):
                discovery_list = [
                    {"{#CONTAINER}": key[4], "{#PROJECT}": args_dict['project'],
                     "{#CLUSTER}": args_dict['host'].split('.cluster')[0],
                     "{#EXTRA}": '_'.join([key[-len(key) + count] for count in range(5, len(key)) if len(key) > 5])} for
                    key in data]

                discovery(discovery_list, 'nodedaemonkey', args_dict['project'], args_dict['subdomain'])

            def agentkey(self):
                pass

        discovermetrices = discovermetrices()


        discover_type = {'cluster': discovermetrices.cluster, 'instance': discovermetrices.instance,
                         'clusterkey': discovermetrices.clusterkey, 'nodekey': discovermetrices.nodekey,
                         'podkey': discovermetrices.podkey, 'nodedaemonkey': discovermetrices.nodedaemonkey,
                         'agentkey': discovermetrices.agentkey}

        discover_type[args_dict['discover']]()

    # Send the data to zabbix if it is iloc00 false. Default is true
    elif args_dict['iloc00']:
        querymetrics(validation(data), args_dict['metric'], args_dict['host'], args_dict['project'], args_dict['count'])
        print('ok')

    # Print dataframe if iloc00 is added as an argument
    else:
        print(data)


if __name__ == '__main__':
    sys.exit(main())
