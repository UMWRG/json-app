import click
from hydra_json import ImportJSON, ExportJSON

from hydra_client.connection import JSONConnection, RemoteJSONConnection

global APP_NAME
APP_NAME='hydra-json'

def hydra_app(category='import'):
    def hydra_app_decorator(func):
        func.hydra_app_category = category
        return func
    return hydra_app_decorator

def get_client(hostname, session_id=None, **kwargs):
    """
        Get the client connection to Hydra. If a hostname is passed,
        and the host name starts with 'http', then connect to hydra server
        using a remote connection. Otherwise connect with a local connection
        to hydra_base
    """
    if hostname is not None and hostname.startswith('http'):
        return RemoteJSONConnection(app_name=APP_NAME,
                                    url=hostname,
                                    session_id=session_id)

    return JSONConnection(app_name=APP_NAME,
                          db_url=hostname,
                          **kwargs)

def get_logged_in_client(context, user_id=None):
    session = context['session']
    client = get_client(context['hostname'], session_id=session, user_id=user_id)
    if client.user_id is None:
        client.login(username=context['username'], password=context['password'])
    return client


@click.group()
@click.pass_obj
@click.option('-u', '--username', type=str, default=None)
@click.option('-p', '--password', type=str, default=None)
@click.option('-h', '--hostname', type=str, default=None)
@click.option('-s', '--session', type=str, default=None)
def cli(obj, username, password, hostname, session):
    """ CLI for the Hydra JSON application. """

    obj['hostname'] = hostname
    obj['username'] = username
    obj['password'] = password
    obj['session']  = session

def start_cli():
    cli(obj={}, auto_envvar_prefix='HYDRA_JSON')

@hydra_app(category='export')
@cli.command(name='export')
@click.pass_obj
@click.option('-n', '--network-id',  required=True, type=int, help='''ID of the network that will be exported.''')
@click.option('-s', '--scenario-id', required=True, type=int, help='''ID of the scenario that will be exported.''')
@click.option('-d', '--data-dir',  required=True, type=str, help='''Target Directory''')
@click.option('--user-id', type=int, default=None)
def export(obj, network_id, scenario_id, data_dir, user_id):


    client = get_logged_in_client(obj, user_id=user_id)

    json_exporter = ExportJSON(client)

    json_exporter.export_network(network_id, scenario_id, data_dir)

@hydra_app(category='import')
@cli.command(name='import')
@click.pass_obj
@click.option('-f', '--network-file', required=True, help='''Path to the network file''')
@click.option('-t', '--template-id', required=True, type=int, help='''ID of the template that matches the network''')
@click.option('-p', '--project-id', required=True, type=int, help='''ID of the project to place the network''')
@click.option('--network-name', required=False, type=str, help='''Optional network name, rather than using the one in the file''')
@click.option('--user-id', type=int, default=None)
def import_network(obj, network_file, template_id, project_id, network_name=None, user_id=None):

    client = get_logged_in_client(obj, user_id=user_id)

    json_importer = ImportJSON(client)

    json_importer.import_network(network_file, template_id, project_id, network_name=network_name)

@hydra_app(category='import_template')
@cli.command(name='import-template')
@click.pass_obj
@click.option('-f', '--template-file', required=True, help='''Path to the templlate file''')
@click.option('--user-id', type=int, default=None)
def import_template(obj, template_file, user_id):
    """
        Import a template JSON file
    """

    client = get_logged_in_client(obj, user_id=user_id)

    json_importer = ImportJSON(client)

    json_importer.import_template(template_file)

#TODO: Implement the register function in the import & export app
#@click.pass_obj
#@click.option('--all', is_flag=True, help='By default only the Export, Run, Import is registered. This flag registers the import, export and auto apps')
#def register(obj, all=False):
#
#    auto.register()
#
#    if all is True:
#        importer.register()
#        exporter.register()
