import requests
from urllib import urlencode
from time import sleep
import myrightscalepassword
from lxml import objectify
# There should be a myrightscalepassword.py in this directory containing password="yourPassword"

from RightScaleHelper import lookup 

user="simon@example.com"
acct="12345"
cloudid=2
baseurl="https://my.rightscale.com" # wont work because of the 302 that python turns into a GET 
baseurl="https://us-3.rightscale.com"
password=myrightscalepassword.password

s = requests.Session()
data = {}
data['email'] = user
data['password'] = password
data['account_href'] = "/api/accounts/%s" % acct

headers = {'X-API-VERSION': "1.5", 'Content-Type': 'application/x-www-form-urlencoded', 'Accept': 'application/xml'}
sessionurl=baseurl+"/api/session"
print "login"
r=s.post(sessionurl, headers=headers, data=data) # login
print r.text

server_name='launchtest01.example.com'

print "create volume"
volumename='%s_opt' % server_name
volume_href=lookup(s, "volumes", volumename)

if not volume_href:
  data={}
  data['volume[name]']=volumename
  data['volume[description]']='The /opt for %s' % server_name
  data['volume[size]']='100' #gigabytes
  data['volume[iops]']='500' #iops
  data['volume[datacenter_href]']='/api/clouds/2/datacenters/342887S8S5SU6'
  r=s.post(baseurl+'/api/clouds/2/volumes', headers=headers, data=data)
  print r.text
else:
  print "Volume already exists (or more than one). Refusing to create another with the same name."
  print volume_href 

volume_href=lookup(s, "volumes", volumename)

if not volume_href:
  print "Failed to create or find the volume"
  exit(1)


print "create server"

servers_with_this_name=lookup(s, "servers", server_name)

if not servers_with_this_name:
  data={}
  data['server[name]']                              =server_name
  data['server[description]']                       ='test server'
  data['server[deployment_href']                    =lookup(s, "deployments", "appservers")
  data['server[instance][cloud_href]']              =lookup(s, "clouds", "EC2 eu-west-1")
  data['server[instance][server_template_href]']    =lookup(s, "server_templates", "Base ServerTemplate for Linux (v13.4) - Non-Orchestrated - PI LTG,20130816")[0]
  data['server[instance][ssh_key_href]']            =lookup(s, "ssh_keys", "my-keypair")
  data['server[instance][instance_type_href]']      =lookup(s, "instance_types", "m1.small") 
  data['server[instance][security_group_hrefs][]']  = [ 
      lookup(s, "security_groups", "APP"),
      lookup(s, "security_groups", "ALL")]

  r=s.post(baseurl+'/api/servers', headers=headers, data=data)
  print r.content
  print r.text
  print "Sleeping 10 seconds for rightscale to commit config"
  sleep(10)
  servers_with_this_name=lookup(s, "servers", server_name)
else:
  print "A server with the name %s already exists. Cowardly refusing to create another" % server_name
  print servers_with_this_name


if False:
  print "There must be no ambiguity about which volume i'm going to attach to which server"
  print servers_with_this_name, volume_href
  raise SystemExit
else:
  print "Attaching %s to %s" % (volume_href, servers_with_this_name)
  data={}
  data['recurring_volume_attachment[device]']='/dev/xvdj'
  data['recurring_volume_attachment[storage_href]']=volume_href
  data['recurring_volume_attachment[runnable_href]']=servers_with_this_name
  r=s.post(baseurl+'/api/clouds/%s/recurring_volume_attachments' % cloudid, headers=headers, data=data)
  print r.text 


print "Setting inputs"
data={}
data['inputs[][name]']     ='BLOCK_DEVICE'
data['inputs[][value]']    ='text:/dev/xvdj'
next_instance_id=lookup(s, 'next_instance', server_name).split('/')[-1] #get the first next instance
r=s.put(baseurl+'/api/clouds/%s/instances/%s/inputs/multi_update' % (cloudid, next_instance_id), headers=headers, data=data)
print r.text

