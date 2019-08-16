#!/usr/bin/env python
# reportgen.py
# simple script to generate cis scan report based on the ouptut from custom plugins
# output all controls, grouped together with PASS, FAIL, VERIFY
# default output format is html
# Abdul Karim <akarim786@gmail.com>

from __future__ import print_function
from __future__ import unicode_literals
from __future__ import absolute_import

try:
    import json
except ImportError:
    import simplejson as json

import sys
import os
import csv
from optparse import OptionParser

raw_log_path='reports/raw'
report_path = 'reports/html'

def getRuns(reports_path):
    """
    Get number of run from log locations
    """
    dates =  [f for f in os.listdir(reports_path) if os.path.isdir(os.path.join(raw_log_path, f))]
    return sorted(dates, reverse=True)

def getHosts (hostfile):
    """
    return all hosts in inventory file
    """
   #dates =  [f for f in os.listdir(report_path) if os.path.isdir(os.path.join(raw_log_path, f))]
    with open(hostfile, 'r') as f:
        host_list = f.readlines()
        hosts=[]
        for line in host_list:
            h = line[1]
            if not line.startswith ('#'):
                hosts.append(line.strip())
    return hosts


def getHostStatus(datestamp,hostname):
    """
    get overall status of a host
    """
    try:
        with open(raw_log_path+'/'+datestamp+'/summary_report_'+datestamp+'.csv', 'rb') as f:
            reader = csv.reader(f)
            thelist = list(reader)
    except:
        thelist={}
    hoststatus=''
    for line in thelist:
        if line != []:
            status=line[2].strip()
            h = line[1].strip()
            if h.startswith(hostname) and status.startswith('FAIL'):
                return 'FAIL'
                break
            hoststatus=status
    return hoststatus

def generate_report(report_path,inventoryfile):
    """
    Process reports output in html
    """
    htmlfile = open(report_path+'/cis_report.html','w') 

    htmlfile.write("<html>")
    htmlfile.write( "<head>")
    htmlfile.write( '  <meta name="viewport" content="width=device-width, initial-scale=1">')
    htmlfile.write( '  <link rel="stylesheet" href="https://maxcdn.bootstrapcdn.com/bootstrap/3.3.7/css/bootstrap.min.css">')
    htmlfile.write( '  <script src="https://ajax.googleapis.com/ajax/libs/jquery/3.2.1/jquery.min.js"></script>')
    htmlfile.write( '  <script src="https://maxcdn.bootstrapcdn.com/bootstrap/3.3.7/js/bootstrap.min.js"></script>')
    htmlfile.write( '</head>')
    htmlfile.write( '<body>')
    htmlfile.write( '<center><h3> cis scan report</h3></center>' )

    run_list=getRuns(raw_log_path)
    host_list=getHosts(inventoryfile)
    count=1
    for host in host_list:
        hostname=host.strip()
        reportcount=1
        reportstatus=''
        htmlfile.write( '<div class="container">')
        htmlfile.write( '<button type="button" class="btn btn-info" data-toggle="collapse" data-target="#host'+str(count)+'">'+hostname+''+reportstatus+'</button>')
        htmlfile.write( '<div id="host'+str(count)+'" class="collapse">')
        for rundate in run_list:
            runstatus = getHostStatus(rundate,hostname)
            btn_class = 'btn-info'
            try:
                if runstatus.startswith ('FAIL'):
                    btn_class='btn-danger'
                elif runstatus.startswith('VERIFY'):
                    btn_class='btn-warn'
                elif runstatus.startswith('PASS'):
                    btn_class='btn-success'
            except KeyError as err:
                btn_class='btn-disabled'
            htmlfile.write( '<div class="container">')
            htmlfile.write( '<button type="button" class="btn '+btn_class+'" data-toggle="collapse" data-target="#report_'+str(count)+''+str(reportcount)+'">'+rundate+'</button>')
            htmlfile.write( '<div id="report_'+str(count)+''+str(reportcount)+'" class="collapse">')
            htmlfile.write( '<div class="container">')
            htmlfile.write( '<button type="button" class="btn btn-danger" data-toggle="collapse" data-target="#reportfailed_'+str(count)+''+str(reportcount)+'">FAILED</button>')
            htmlfile.write( '<div id="reportfailed_'+str(count)+''+str(reportcount)+'" class="collapse">')
            htmlfile.write( '<div class="table-responsive">')
            htmlfile.write( "<table class='table'>")
            htmlfile.write( "<tr><td>Date of run: "+rundate+"</td>")
            htmlfile.write( "<tr bgcolor=grey><th> control</th> <th> status </th> <th>command</th> <th>output</th></tr>")
            try:
               with open(raw_log_path+'/'+rundate+'/'+hostname+'_'+rundate+'.json','r') as f:
                data = f.readlines()
                for line in data:
                    j = json.loads(line)
                    for control, result in j.iteritems():
                        colour='lightgreen'
                        if result['status'] == 'FAIL':
                            colour='red'
                            htmlfile.write( '<tr bgcolor="+colour+"><td>'+control+'</td> <td>'+result["status"]+'</td>')
                            htmlfile.write( "<td>"+result['cmd']+"</td>")
                            htmlfile.write( "<td>"+str(result['output'])+"</td></tr>")
            except IOError as err:
                htmlfile.write( "<tr><td>no run for this date</td> <td> %s </td> </tr>" % (err))
            htmlfile.write( "</table>")
            htmlfile.write( '</div>')
            htmlfile.write( '</div>')
            htmlfile.write( '</div>')

            htmlfile.write( '<div class="container">')
            htmlfile.write( '<button type="button" class="btn btn-success" data-toggle="collapse" data-target="#reportpass_'+str(count)+''+str(reportcount)+'">PASS</button>')
            htmlfile.write( '<div id="reportpass_'+str(count)+''+str(reportcount)+'" class="collapse">')
            htmlfile.write( '<div class="table-responsive">')
            htmlfile.write( "<table class='table'>")
            htmlfile.write( "<tr><td>Date of run: "+rundate+"</td>")
            htmlfile.write( "<tr bgcolor=grey><th> control</th> <th> status </th> <th>command</th> <th>output</th></tr>")
            try:
                with open(raw_log_path+'/'+rundate+'/'+hostname+'_'+rundate+'.json','r') as f:
                    data = f.readlines()
                    for line in data:
                        j = json.loads(line)
                        for control, result in j.iteritems():
                            colour='lightgreen'
                            if result['status'] == 'PASS':
                                colour='green'
                                htmlfile.write( "<tr bgcolor="+colour+"><td>"+control+"</td> <td>"+result['status']+"</td>")
                                htmlfile.write( "<td>"+result['cmd']+"</td>")
                                htmlfile.write( "<td>"+result['output']+"</td></tr>")
            except IOError as err:
                htmlfile.write( "<tr><td>no run for this date</td> <td> %s</td> </tr>" %(err))
            htmlfile.write( "</table>")
            htmlfile.write( '</div>')
            htmlfile.write( '</div>')
            htmlfile.write( '</div>')

            htmlfile.write( '<div class="container">')
            htmlfile.write( '<button type="button" class="btn btn-warning" data-toggle="collapse" data-target="#reportverify_'+str(count)+''+str(reportcount)+'">VERIFY</button>')
            htmlfile.write( '<div id="reportverify_'+str(count)+''+str(reportcount)+'" class="collapse">')
            htmlfile.write( '<div class="table-responsive">')
            htmlfile.write( "<table class='table'>")
            htmlfile.write( "<tr><td>Date of run: "+rundate+"</td>")
            htmlfile.write( "<tr bgcolor=grey><th> control</th> <th> status </th> <th>command</th> <th>output</th></tr>")
            try:
                with open(raw_log_path+'/'+rundate+'/'+hostname+'_'+rundate+'.json','r') as f:
                    data = f.readlines()
                    for line in data:
                        j = json.loads(line)
                        for control, result in j.iteritems():
                            colour='lightgreen'
                            if result['status'] == 'VERIFY' or result['status'] == 'UNKNOWN':
                                colour='orange'
                                htmlfile.write( "<tr bgcolor="+colour+"><td>"+control+"</td><td>"+result['status']+"</td>")
                                htmlfile.write( "<td>"+result['cmd']+"</td>")
                                htmlfile.write( "<td>"+result['output']+"</td></tr>")
            except IOError as err:
                htmlfile.write( "<tr><td>no run for this date</td> <td>%s</td> </tr>" % (err))

            htmlfile.write( "</table>")
            htmlfile.write( '</div>')
            htmlfile.write( '</div>')

            htmlfile.write( '</div>')
            htmlfile.write( '</div>')
            htmlfile.write( '</div>')
            reportcount =  reportcount + 1
        htmlfile.write( '</div>')
        htmlfile.write( '</div>')
        count =  count + 1
    htmlfile.write( "</body>")
    htmlfile.write( "</html>")

    print ('Output generated in '+report_path)

def parse_cmdline():
    """
    Process commandline arguments etc
    """
    parser = OptionParser()
    parser.add_option("-i", "--inventory", dest="inventoryfile",
                  help="inventory list of hostnames (required)")

    (options, args) = parser.parse_args()
    if not options.inventoryfile:
	    parser.print_help()
	    sys.exit(1)
    return options,args

def main():
    options,args = parse_cmdline()
    
    if not os.path.exists(report_path):
        os.mkdir(report_path)

    generate_report(report_path,options.inventoryfile)


if __name__ == "__main__":
    main()
