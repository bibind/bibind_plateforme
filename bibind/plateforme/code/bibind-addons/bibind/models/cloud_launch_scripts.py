# -*- encoding: utf-8 -*-
##############################################################################
#
#    odoo, Open Source Management Solution
#    Copyright (C) 2012 ASPerience SARL (<http://www.asperience.fr>).
#    All Rights Reserved
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
import time, os, random, string


from odoo import models, fields, api, _

from odoo.tools.translate import _
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT, DATETIME_FORMATS_MAP, float_compare
import odoo.addons.decimal_precision as dp
import sys
import array
from odoo import netsvc
import logging
from lxml import etree
import paramiko
from paramiko import SSHClient
from paramiko import SFTPClient
import ovh
from ansible.parsing.dataloader import DataLoader
from ansible.vars.manager import VariableManager
from ansible.inventory.manager import InventoryManager
from ansible.playbook.play import Play
from ansible.executor.task_queue_manager import TaskQueueManager
from ansible.plugins.callback import CallbackBase
from jinja2 import Environment, FileSystemLoader
import json
import yaml
from collections import namedtuple
import argparse
import tarfile

from collections import defaultdict
import base64



_logger = logging.getLogger("auguria_cloudmanager")


class Options(object):
    """
    Options class to replace Ansible OptParser
    """
    def __init__(self, verbosity=None, inventory=None, listhosts=None, subset=None, module_paths=None, extra_vars=None,
                 forks=None, ask_vault_pass=None, vault_password_files=None, new_vault_password_file=None,
                 output_file=None, tags=None, skip_tags=None, one_line=None, tree=None, ask_sudo_pass=None, ask_su_pass=None,
                 sudo=None, sudo_user=None, become=None, become_method=None, become_user=None, become_ask_pass=None,
                 ask_pass=None, private_key_file=None, remote_user=None, connection=None, timeout=None, ssh_common_args=None,
                 sftp_extra_args=None, scp_extra_args=None, ssh_extra_args=None, poll_interval=None, seconds=None, check=None,
                 syntax=None, diff=None, force_handlers=None, flush_cache=None, listtasks=None, listtags=None, module_path=None):
        self.verbosity = verbosity
        self.inventory = inventory
        self.listhosts = listhosts
        self.subset = subset
        self.module_paths = module_paths
        self.extra_vars = extra_vars
        self.forks = forks
        self.ask_vault_pass = ask_vault_pass
        self.vault_password_files = vault_password_files
        self.new_vault_password_file = new_vault_password_file
        self.output_file = output_file
        self.tags = tags
        self.skip_tags = skip_tags
        self.one_line = one_line
        self.tree = tree
        self.ask_sudo_pass = ask_sudo_pass
        self.ask_su_pass = ask_su_pass
        self.sudo = sudo
        self.sudo_user = sudo_user
        self.become = become
        self.become_method = become_method
        self.become_user = become_user
        self.become_ask_pass = become_ask_pass
        self.ask_pass = ask_pass
        self.private_key_file = private_key_file
        self.remote_user = remote_user
        self.connection = connection
        self.timeout = timeout
        self.ssh_common_args = ssh_common_args
        self.sftp_extra_args = sftp_extra_args
        self.scp_extra_args = scp_extra_args
        self.ssh_extra_args = ssh_extra_args
        self.poll_interval = poll_interval
        self.seconds = seconds
        self.check = check
        self.syntax = syntax
        self.diff = diff
        self.force_handlers = force_handlers
        self.flush_cache = flush_cache
        self.listtasks = listtasks
        self.listtags = listtags
        self.module_path = module_path

class Runner(object):

    def __init__(self, hostnames, playbook, private_key_file, run_data, become_pass, verbosity=0):

        self.run_data = run_data

        self.options = Options()
        self.options.private_key_file = private_key_file
        self.options.verbosity = verbosity
        self.options.connection = 'ssh'  # Need a connection type "smart" or "ssh"
        self.options.become = True
        self.options.become_method = 'sudo'
        self.options.become_user = 'root'

        # Set global verbosity
        self.display = Display()
        self.display.verbosity = self.options.verbosity
        # Executor appears to have it's own 
        # verbosity object/setting as well
        playbook_executor.verbosity = self.options.verbosity

        # Become Pass Needed if not logging in as user root
        passwords = {'become_pass': become_pass}

        # Gets data from YAML/JSON files
        self.loader = DataLoader()
        self.loader.set_vault_password(os.environ['VAULT_PASS'])

        # All the variables from all the various places
        self.variable_manager = VariableManager()
        self.variable_manager.extra_vars = self.run_data

        # Parse hosts, I haven't found a good way to
        # pass hosts in without using a parsed template :(
        # (Maybe you know how?)
        self.hosts = NamedTemporaryFile(delete=False)
        self.hosts.write("""[run_hosts]
%s
""" % hostnames)
        self.hosts.close()

        # This was my attempt to pass in hosts directly.
        # 
        # Also Note: In py2.7, "isinstance(foo, str)" is valid for
        #            latin chars only. Luckily, hostnames are 
        #            ascii-only, which overlaps latin charset
        ## if isinstance(hostnames, str):
        ##     hostnames = {"customers": {"hosts": [hostnames]}}

        # Set inventory, using most of above objects
        self.inventory = Inventory(loader=self.loader, variable_manager=self.variable_manager, host_list=self.hosts.name)
        self.variable_manager.set_inventory(self.inventory)

        # Playbook to run. Assumes it is
        # local to this python file
        pb_dir = os.path.dirname(__file__)
        playbook = "%s/%s" % (pb_dir, playbook)

        # Setup playbook executor, but don't run until run() called
        self.pbex = playbook_executor.PlaybookExecutor(
            playbooks=[playbook], 
            inventory=self.inventory, 
            variable_manager=self.variable_manager,
            loader=self.loader, 
            options=self.options, 
            passwords=passwords)

    def run(self):
        # Results of PlaybookExecutor
        self.pbex.run()
        stats = self.pbex._tqm._stats

        # Test if success for record_logs
        run_success = True
        hosts = sorted(stats.processed.keys())
        for h in hosts:
            t = stats.summarize(h)
            if t['unreachable'] > 0 or t['failures'] > 0:
                run_success = False

        # Dirty hack to send callback to save logs with data we want
        # Note that function "record_logs" is one I created and put into
        # the playbook callback file
        self.pbex._tqm.send_callback(
            'record_logs', 
            user_id=self.run_data['user_id'], 
            success=run_success
        )
        
        
        
        
class ResultCallback(CallbackBase):
    """A sample callback plugin used for performing an action as results come in

    If you want to collect all results into a single object for processing at
    the end of the execution, look into utilizing the ``json`` callback plugin
    or writing your own custom callback plugin
    """
    def v2_runner_on_ok(self, result, **kwargs):
        """Print a json representation of the result

        This method could store the result in an instance attribute for retrieval later
        """
        host = result._host
        print(json.dumps({host.name: result._result}, indent=4))

class BibindInventory(object):

    def __init__(self):
        self.inventory = {}
       
        self.inventory = self.empty_inventory()

        print(json.dumps(self.inventory))

    # Example inventory for testing.
    def get_inventory(self, hosts):
        
        
        jinja_env = create_jinja_env()
        groups = {}
        
        
        adress_ips = {}
        adress_ips = {'149.202.162.146'}
        group = {'name':'server', 'adress_ips':adress_ips}
        
        groups['server']=group
        
         
        tmpl = 'inventory.jinj2'
        

        template = jinja_env.get_template(tmpl)
        result = template.render(
             
             groups=groups,
            
             
        )
        inventory = open('my_inventory.txt', 'w')
        inventory.write(result)
        inventory.close()

        return inventory

    # Empty inventory for testing.
    def empty_inventory(self):
        return {'_meta': {'hostvars': {}}}

   

# Get the inventory.
BibindInventory()

FILE_EXT = ['.tar.gz', '.bz2', '.zip']
TYPE_MODE = [('Ansible script','ansible_script'),('Bash script','bash_script')]

class cloud_service_launch_script(models.Model):
        _name = 'launch.script'
        _description = 'Scripts de deploiement'
        _order = 'sequence'
    
        
        name= fields.Char('nom du parametre')
        
        sequence = fields.Integer('sequence', help="Sequence for the handle.",default=10)
        file_script_directory = fields.Char('Directory')
        file_script =fields.Binary('Fichier de script a lancer sur le serveur')
        file_compresser= fields.Many2one(comodel_name="ir.attachment", string="File") 
        script_code =fields.Text('Code à executer sur le serveur')
        script_code_yml =fields.Text('Code yml pour docker compose')
        type_script = fields.Selection(TYPE_MODE, 'Type de script', default='ansible_script')
        is_file = fields.Boolean('Fichier')
        is_deployed = fields.Boolean(compute='_get_is_deployed', string='is_deployed')
        param_json_data = fields.Text('Data in json')
        
        
        
        def _filestore(self):
            
            return tools.config.filestore(self.env.cr.dbname)
        
        def _get_path_file(self, fname):
            base_path = self._filestore()
            id = self.id
            directory = base_path + '/launch_script/' + str(id) 
            if not os.path.exists(directory):
                return False
            filepath = directory + '/' + fname
            
            if not os.path.isfile(filepath):
                return False
            
            return filepath
            
        
        def _set_path_file(self, fname, data):
            base_path = self._filestore()
            id = self.id
            directory = base_path + '/launch_script/' + str(id) 
            
            if not os.path.exists(directory):
                os.makedirs(directory)
            
            filepath = directory + '/' + fname
            
            if not os.path.isfile(filepath):
                script_file = open(filepath, "wb")
                bin = 'test'
                bin_data = base64.b64decode(data)
                script_file.write(bin_data)
                script_file.close()
                
                return filepath
            else:
                return filepath
            
            return filepath
        
        
        def _get_file_extension(self, filename):
            
            for ext in FILE_EXT:
                if filename.endswith(ext):
                    return ext
                else:
                    return False          
            
        
        def script_extract_file(self, file):
            ext = self._get_file_extension(file)
            if ext and ext =='.tar.gz':
                tar = tarfile.open(file)
                for tarinfo in tar:
                    _logger.info('%s, is , %s , bytes in size and is ' % (tarinfo.name,tarinfo.size))
                    
                    if tarinfo.isreg():
                        _logger.info('a regular file. ')
                    elif tarinfo.isdir():
                        _logger.info('a directory.')
                    else:
                         _logger.info('"something else."')
                tar.close()
                return res
            
        

        def get_param_host(self):
            _logger.info('binary file %s' % (self.file_compresser))
            doc = self.file_compresser
            
            _logger.info('irattchement data %s' % (doc.datas))
            _logger.info('irattchement name %s' % (doc.store_fname))
            _logger.info('irattchement name %s' % (doc.type))
            _logger.info('irattchement name %s' % (doc.datas_fname))
            _logger.info('self filestore %s' % (self._filestore()))
            directy_file = self._get_path_file(doc.datas_fname)
            _logger.info(' first directory file %s' % (directy_file))
            if not directy_file:
                directy_file = self._set_path_file(doc.datas_fname, doc.datas)  
                _logger.info(' in directory file %s' % (directy_file))
            _logger.info(' out directory file %s' % (directy_file))
            ext = self._get_file_extension(directy_file)
            _logger.info(' ext file %s' % (ext))
            tarinfo = self.script_extract_file(directy_file)
            _logger.info(' ext file %s' % (tarinfo))
            return True
        
        def send_file(self, param):
            
            transport = paramiko.Transport((param['host'], param['port']))
            password = param['password']
            username = param['login']
            transport.connect(username = username, password = password)

            sftp = paramiko.SFTPClient.from_transport(transport)

            filepath = param['path']
            localpath = self.file_script
            sftp.put(localpath, filepath)
            
            # Close
            
            sftp.close()
            transport.close()
            
        def call_file(self, param):
           
            client = SSHClient()
            client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            client.connect(param['ip'],username=param['login'],password=param['password'])
            client.exec_command('./'+param['path'])
        
            
            self.write({'set_date': time.strftime("%Y-%m-%d %H:%M:%S")})
            return True
        
        def _execute_commande(self, param):
            cmd    = self.script_code
            host   = param['host']
            user   = param['login']
            passwd = ['password']
            ssh    = paramiko.SSHClient()
            
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            ssh.connect(host, username=user)
            stdin, stdout, stderr = ssh.exec_command(cmd)
            
            stdin.flush()
          
            ssh.close()
            
            return

        def get_script_id(self):
            
             host = self.env['bibind.host'].browse(self.env.context.get('host'))
             deploy = host.deployer_script_notinstalled(self)
             if deploy:
                deployed = {}
                for s in json.loads(host.scriptdeployed):
                    deployed[s] = s
                deployed[self.id] = self.id
                deployed = json.dumps(deployed)
                host.write({'scriptdeployed':deployed})
            

        def _get_is_deployed(self):
             _logger.info('context  in field is deploed script %s' % (self.env.context))
             host = self.env['bibind.host'].browse(self.env.context.get('host'))
             for script in self:
                script.is_deployed =  host.button_script_is_deployed(script)
        
        
        def get_template_paths(self):
       
            return [os.path.abspath(os.path.join(os.path.dirname(__file__)))]

        
        def create_jinja_env(self):
            
            return Environment(
                loader=FileSystemLoader(
                    self.get_template_paths()
                )
            )

        def get_template(self,hosts, file):
                
                jinja_env = self.create_jinja_env()
                groups = hosts
                tmpl = 'inventory.jinj2'
                template = jinja_env.get_template(tmpl)
                result = template.render(    
                     groups=groups,
                     )
                inventory = open(file, 'w')
                inventory.write(result)
                inventory.close()
        
                return result
        
        def get_group(self, hosts):
           
            dd = defaultdict(list)
            
            for d , v in hosts.iteritems():
                for key, value in v.iteritems():
                    dd[key].append(value)
            
            return dd
        

        def get_hosts(self, listhosts):
           
            _logger.info('hostlist %s' % (listhosts))
            host_ids = self.env['bibind.host'].browse(listhosts)
            hosts ={}
            mytab = []
            tab = []
            _logger.info('host_ids %s' % (host_ids))
            for id in listhosts:
                   host = self.env['bibind.host'].browse(id)
                   _logger.info('host id %s' % (host.id))
                   _logger.info('host nodeid id %s' % (host.host_ipv4))
                   _logger.info('item %s' % (host.host_ipv4))  
                   _logger.info('host group %s' % (host.group.name))
                   hosts[host.id] = { host.group.name:host.host_ipv4}
            
            _logger.info('host %s' % (hosts))
            return hosts
        
        

        def get_inventory(self, hosts):
            hosts = self.get_hosts(hosts)
            inventory_file = '/var/lib/odoo/filestore/my_inventory'
            list_group = self.get_group(hosts)
            _logger.info('list group  %s' % (list_group))
            inventory = self.get_template(list_group, inventory_file)
            return inventory
        
        
        def get_script_or_play_book(self):
            
            data = self.file_script
            _logger.info('data  %s' % (data))
            return False
        
         
                
            
            
        def run_script(self, inventory_file):
            
                    
            Options = namedtuple('Options', ['connection', 'module_path', 'forks', 'become', 'become_method', 'become_user', 'check', 'diff'])
            # initialize needed objects
            loader = DataLoader()
            options = Options(connection='ssh', module_path='/usr/local/lib/python2.7/dist-packages/ansible', forks=100, become=None, become_method=None, become_user=None, check=False,
                              diff=False)
            passwords = dict(vault_pass='secret')
            
            # Instantiate our ResultCallback for handling results as they come in
            results_callback = ResultCallback()
            
            # create inventory and pass to var manager
            inventory = InventoryManager(loader=loader, sources=inventory_file)
            variable_manager = VariableManager(loader=loader, inventory=inventory)
            
            # create play with tasks
            
            if(self.is_file):
                filename = self.get_script_or_play_book(self.file_script)
                play_source = loader.load_from_file(filename)[0]
                play = Play().load(play_source, variable_manager=variable_manager, loader=loader)
            else:
                # create play with tasks
                play_source =  dict(
                        name = "Ansible Play",
                        hosts = 'localhost',
                        gather_facts = 'no',
                        tasks = [
                            dict(action=dict(module='shell', args='ls'), register='shell_out'),
                            dict(action=dict(module='debug', args=dict(msg='{{shell_out.stdout}}')))
                         ]
                    )
                play = Play().load(play_source, variable_manager=variable_manager, loader=loader)
            # actually run it
            tqm = None
            try:
                tqm = TaskQueueManager(
                          inventory=inventory,
                          variable_manager=variable_manager,
                          loader=loader,
                          options=options,
                          passwords=passwords,
                          stdout_callback=results_callback,# Use our custom callback instead of the ``default`` callback plugin
                      )
                #print "test" 
                result = tqm.run(play)
                #print(json.dumps(result, indent=4))
                
            finally:
                if tqm is not None:
                    tqm.cleanup()
                    #print "finally"


        
        
        
        
        
        
        
        
        
        
        
        
        
        def _run_commande(self, param):
            #
            # Try to connect to the host.
            # Retry a few times if it fails.
            #
            i =1 
            while True:
                
            
                try:
                    ssh = paramiko.SSHClient()
                    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
                    ssh.connect(param['host'])
                   
                    break
                except paramiko.AuthenticationException:
                    #print "Authentication failed when connecting to %s" % host
                    #sys.exit(1)
                    res ='fail auth'
                    return res
                except:
                    print("Could not SSH to %s, waiting for it to start" % host)
                    i += 1
                    time.sleep(2)
            
                # If we could not connect within time limit
                if i == 30:
                    #print "Could not connect to %s. Giving up" % host
                    #sys.exit(1)
                    res = 'fail timeout'
                    return res
            
            # Send the command (non-blocking)
            #cmd = self.command+'--'
            stdin, stdout, stderr = ssh.exec_command("my_long_command --arg 1 --arg 2")
            
            # Wait for the command to terminate
            while not stdout.channel.exit_status_ready():
                # Only print data if there is data to read in the channel
                if stdout.channel.recv_ready():
                    rl, wl, xl = select.select([stdout.channel], [], [], 0.0)
                    if len(rl) > 0:
                        # Print data from stdout
                        #print stdout.channel.recv(1024),
                        res ='done'
                        
            #
            # Disconnect from the host
            #
            ssh.close()
            return res
        
        
    
cloud_service_launch_script()






