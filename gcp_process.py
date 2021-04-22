#!/usr/bin/env python

##########################################################################################################################
#                                                                                                                        #
#Google Cloud Process Monitoring Script                                                                                  #
#Python version 2.7                                                                                                      #
#Created By - Pritish Debnath                                                                                            #
#Creation Date - 2/24/2020                                                                                               #
#Usage: gcp_process.py --project <project_name> --metric_filter 'stackdriver-col|acpid|agetty' --metadata_filter <host>  #                                                                                                                         #
#                                                                                                                        #
##########################################################################################################################

# Importing Module

from gcloud import monitoring
import argparse
import sys
from datetime import datetime

PARSER = argparse.ArgumentParser(
         description='Google Cloud Monitoring API Command Line\nWebsite: https://github.com/odin-public/gcpmetrics',
         formatter_class=argparse.RawDescriptionHelpFormatter)


PARSER.add_argument('--project', help='Project ID.', metavar='ID')
PARSER.add_argument('--minutes', default=5, help='Minutes from now to calculate the query start date.', metavar='INT')
PARSER.add_argument('--metric', default='agent.googleapis.com/processes/cpu_time', help='Metric ID as defined by Google Monitoring API.', metavar='ID')
PARSER.add_argument('--metric_filter', default=None, help='Filter of metrics in the var:val[,var:val] format.', metavar='S')
PARSER.add_argument('--metadata_filter', default=None, help='Filter of resources in the var:val[,var:val] format.', metavar='S')

def error(message):

    sys.stderr.write('error: {}'.format(message))
    print
    print
    PARSER.print_help()
    sys.exit(1)

def zabbix_send(output, host):

    starttime = datetime.now()
    
    for key,value in output.items():
        key = 'gcp.process[{}]'.format(key)
        cmd = 'zabbix_sender -z localhost -p 10051 -s {} -k {} -o {}'.format(host,key,value)
        subprocess.check_output(cmd, shell=True)
        
    endtime = datetime.now()
    delta = endtime - starttime
    delta_float = delta.seconds + delta.microseconds/1E6
    
    print delta_float

def perform_query(client, metric_id, minutes, metadata_filter, metric_filter):
    
    query = client.query(
            metric_type = metric_id,
            minutes=minutes
            )
    
    query = query.select_metrics(**metric_filter)
    query = query.select_meta(name=metadata_filter)
    output = dict.fromkeys(list(metric_filter.values()), 0)
    
    for timeseries in query.iter(headers_only=True, page_size=None):
        if timeseries[0][1]['command'] in output:
            count = output[timeseries[0][1]['command']]
            output[timeseries[0][1]['command']] = count + 1

    zabbix_send(output, metadata_filter)

def process(keyfile, project_id, metric_id, minutes, metadata_filter, metric_filter):

    if not project_id:
        error('--project not specified')

    _file = keyfile
    client = monitoring.Client.from_service_account_json(_file, project=project_id)

    perform_query(client, metric_id, minutes, metadata_filter, metric_filter)
    
    
def main():

    args_dict = vars(PARSER.parse_args())

    def processfilter(_filter):
        if not _filter:
            return None
        _filter = _filter.split('|')
        _ret = {}
        for i in range(len(_filter)):
            _ret['command' + str(i)] = _filter[i]
        return _ret
    
    metric_filter = processfilter(args_dict['metric_filter'])
    keyfile = '/opt/gcp/gcproject/{}/keyfile.json'.format(args_dict['project'])

    process(
            keyfile,
            args_dict['project'],
            args_dict['metric'],
            int(args_dict['minutes']),
            args_dict['metadata_filter'],
            metric_filter
            )

if __name__ == '__main__':
    main()
