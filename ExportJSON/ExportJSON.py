#!/usr/bin/env python
# -*- coding: utf-8 -*-
# (c) Copyright 2015 University of Manchester\
#\
# ExportJSON is free software: you can redistribute it and/or modify\
# it under the terms of the GNU General Public License as published by\
# the Free Software Foundation, either version 3 of the License, or\
# (at your option) any later version.\
#\
# ExportJSON is distributed in the hope that it will be useful,\
# but WITHOUT ANY WARRANTY; without even the implied warranty of\
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the\
# GNU General Public License for more details.\
# \
# You should have received a copy of the GNU General Public License\
# along with ExportJSON.  If not, see <http://www.gnu.org/licenses/>\
#

"""A Hydra plug-in for exporting a hydra network to a JSON file.

Basics
~~~~~~

The plug-in for exporting a network to a JSON file.
Basic usage::

       ExportJSON.py [-h] [-n network_id] [-s scenario_id] [-d target_dir]

Options
~~~~~~~

====================== ====== ============ =======================================
Option                 Short  Parameter    Description
====================== ====== ============ =======================================
``--help``             ``-h``              Show help message and exit.
``--network-id         ``-n`` NETWORK      The ID of the network to be exported.
``--scenario-id        ``-s`` SCENARIO     The ID of the scenario to be exported.
                                           (optional)
``--target-dir``       ``-d`` TARGET_DIR   Target directory 
``--server-url``       ``-u`` SERVER-URL   Url of the server the plugin will
                                           connect to.
                                           Defaults to localhost.
``--session-id``       ``-c`` SESSION-ID   Session ID used by the calling software.
                                           If left empty, the plugin will attempt
                                           to log in itself.
====================== ====== ============ =======================================


API docs
~~~~~~~~
"""


import argparse as ap
import logging

from HydraLib import PluginLib
from HydraLib.PluginLib import JsonConnection
from HydraLib.HydraException import HydraPluginError
from HydraLib.PluginLib import write_progress, write_output, validate_plugin_xml
import time
import json
import os, sys

if "../" not in sys.path:
    sys.path.append("../")

from utils.xml2json import json2xml
log = logging.getLogger(__name__)

global __location__
__location__ = os.path.split(sys.argv[0])[0]

class ExportJSON(object):
    """
    """

    Network = None
    Scenario = None

    def __init__(self, url=None, session_id=None):

        self.warnings = []

        #Record the names of the files created by the plugin so we can
        #display them to the user.
        self.files    = []

        self.connection = JsonConnection(url)
        if session_id is not None:
            log.info("Using existing session %s", session_id)
            self.connection.session_id=session_id
        else:
            self.connection.login()

        self.num_steps = 6

    def export(self, network_id, scenario_id, target_dir):
        write_output("Retrieving Network") 
        write_progress(2, self.num_steps) 
        if network_id is not None:
            #The network ID can be specified to get the network...
            try:
                network_id = int(network_id)
                x = time.time()
                if scenario_id is None:
                    network = self.connection.call('get_network', {'network_id':network_id})
                else:
                    network = self.connection.call('get_network', {'network_id':network_id,
                                                        'scenario_ids':[scenario_id]})

                log.info("Network retrieved in %s", time.time()-x)
            except:
                raise HydraPluginError("Network %s not found."%network_id)

        else:
            raise HydraPluginError("A network ID must be specified!")

        if target_dir is None:
            target_dir = os.path.join(os.path.expanduser('~'), 'Desktop')

        if not os.path.exists(target_dir):
            os.mkdir(target_dir)

        self.write_network(network, target_dir)

    def write_network(self, network, target_dir):
        write_output("Exporting network")
        write_progress(3, self.num_steps) 

        if self.as_xml is False:
            file_name = "network_%s.json"%(network['name'])
            self.files.append(os.path.join(target_dir, file_name))

            network_file = open(os.path.join(target_dir, file_name), 'w')
            network_file.write(json.dumps(network, sort_keys=True, indent=4, separators=(',', ': ')))
        else:
            file_name = "network_%s.xml"%(network['name'])
            self.files.append(os.path.join(target_dir, file_name))

            network_file = open(os.path.join(target_dir, file_name), 'w')
            json_network = {'network': network}
            network_file.write(json2xml(json_network))

        write_output("Network Exported")

def commandline_parser():
    parser = ap.ArgumentParser(
        description="""Export a network in to a file in JSON format.
                    Written by Stephen Knox <stephen.knox@manchester.ac.uk>
                    (c) Copyright 2015, University of Manchester.
        """, epilog="For more information visit www.hydraplatform.org",
        formatter_class=ap.RawDescriptionHelpFormatter)
    parser.add_argument('-n', '--network-id',
                        help='''Specify the network_id of the network to be exported.
                        If the network_id is not known, specify the network name. In
                        this case, a project ID must also be provided''')
    parser.add_argument('-s', '--scenario-id',
                        help='''Specify the ID of the scenario to be exported. If no
                        scenario is specified, all scenarios in the network will be
                        exported.
                        ''')
    parser.add_argument('-d', '--target-dir',
                        help='''Target directory''')
    parser.add_argument('-x', '--as_xml', action='store_true',
                        help='''Export as XML instead of JSON''')
    parser.add_argument('-u', '--server-url',
                        help='''Specify the URL of the server to which this
                        plug-in connects.''')
    parser.add_argument('-c', '--session-id',
                        help='''Session ID. If this does not exist, a login will be
                        attempted based on details in config.''')
    return parser


if __name__ == '__main__':
    parser = commandline_parser()
    args = parser.parse_args()
    json_exporter = ExportJSON(url=args.server_url, session_id=args.session_id)
    errors = []
    try:
        write_output("Starting App")
        write_progress(1, json_exporter.num_steps) 

        validate_plugin_xml(os.path.join(__location__, 'plugin.xml'))
        
        json_exporter.as_xml = args.as_xml

        json_exporter.export(args.network_id, args.scenario_id, args.target_dir)
        message = "Export complete"
    except HydraPluginError as e:
        message="An error has occurred"
        errors = [e.message]
        log.exception(e)
    except Exception, e:
        message="An error has occurred"
        log.exception(e)
        errors = [e]

    xml_response = PluginLib.create_xml_response('ExportJSON',
                                                 args.network_id,
                                                 [],
                                                 errors,
                                                 json_exporter.warnings,
                                                 message,
                                                 json_exporter.files)
    print xml_response