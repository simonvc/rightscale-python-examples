from lxml import objectify
import myrightscalepassword
import requests

headers = {'X-API-VERSION': "1.5", 'Content-Type': 'application/x-www-form-urlencoded', 'Accept': 'application/xml'}
baseurl="https://us-3.rightscale.com"

def lookup(s, k='', v='', cloud=2, fail_if_not_found=False):
  def short_return(something):
    if not something and fail_if_not_found:
      raise NameError("%s not found" % v)
    if type([]) == type(something):
      if len(something) == 1:
        return something[0]
      else:
        return something
    else:
      return something
  data={}
  if k=="deployments":
    r=s.get(baseurl+"/api/deployments", headers=headers, data=data).text.encode('ascii', 'ignore')
    return short_return(objectify.fromstring(r).xpath("//deployments/deployment[name = '%s']/links/link[@rel = 'self']/@href" % v))
  elif k=="ssh_keys":
    r=s.get(baseurl+"/api/clouds/%s/ssh_keys" % cloud, headers=headers, data=data).text.encode('ascii', 'ignore')
    return short_return( objectify.fromstring(r).xpath("//ssh_keys/ssh_key[resource_uid = '%s']/links/link[@rel = 'self']/@href" % v))
  elif k=='clouds':
   r=s.get(baseurl+"/api/clouds", headers=headers, data=data).text.encode('ascii', 'ignore')
   return short_return( objectify.fromstring(r).xpath("//clouds/cloud[name = '%s']/links/link[@rel = 'self']/@href" % v))
  elif k=='server_templates':
    r=s.get(baseurl+"/api/server_templates", headers=headers).text.encode('ascii', 'ignore')
    return short_return( objectify.fromstring(r).xpath("//server_templates/server_template[name = '%s']/links/link[@rel = 'self']/@href" % v))
  elif k=='security_groups':
    r=s.get(baseurl+"/api/clouds/%s/security_groups" % cloud, headers=headers).text.encode('ascii', 'ignore')
    return short_return( objectify.fromstring(r).xpath("//security_groups/security_group[name = '%s']/links/link[@rel = 'self']/@href" % v))
  elif k=='instance_types':
    r=s.get(baseurl+"/api/clouds/%s/instance_types" % cloud, headers=headers).text.encode('ascii', 'ignore')
    return short_return( objectify.fromstring(r).xpath("//instance_types/instance_type[name = '%s']/links/link[@rel = 'self']/@href" % v))
  elif k=='volumes':
    r=s.get(baseurl+"/api/clouds/%s/volumes" % cloud, headers=headers).text.encode('ascii', 'ignore')
    return short_return( objectify.fromstring(r).xpath("//volumes/volume[name = '%s']/links/link[@rel = 'self']/@href" % v))
  elif k=='servers':
    r=s.get(baseurl+"/api/servers/", headers=headers).text.encode('ascii', 'ignore')
    return short_return( objectify.fromstring(r).xpath("//servers/server[name = '%s']/links/link[@rel = 'self']/@href" % v))
  elif k=='next_instance':
    r=s.get(baseurl+"/api/servers/", headers=headers).text.encode('ascii', 'ignore')
    return short_return( objectify.fromstring(r).xpath("//servers/server[name = '%s']/links/link[@rel = 'next_instance']/@href" % v))
  else:
    return None


def login(s):
  data={}
  data['email']=user
  data['password']=myrightscalepassword.password
  data['account_href']="/api/accounts/%s" %acct
  url=baseurl+"/api/session"
  print s.post(url, data=data, headers=headers).text



#### tests


if __name__=='__main__':
  user="simon@example.com"
  acct="12345"
  baseurl="https://us-3.rightscale.com"
  password=myrightscalepassword.password
  s = requests.Session()

  login(s)

  print lookup(s, "servers", "launchtest01.example.net")
  print lookup(s, "next_instance", "launchtest01.example.net")
  print lookup(s, "ssh_keys", "my-keypair")
  print lookup(s, "deployments", "mydeployment")
  print lookup(s, "clouds", "EC2 eu-west-1")
  print lookup(s, "server_templates", "Base ServerTemplate for Linux (v12.11.0-LTS) - Non-orchestrated - PI LTG, 20130723")
  print lookup(s, "security_groups", "ALL")
  print lookup(s, "security_groups", "APP")
  print lookup(s, "instance_types", "m1.small")
  print lookup(s, "volumes", "launchtest01.example.net/opt/")
  import code
  code.InteractiveConsole(locals()).interact()


