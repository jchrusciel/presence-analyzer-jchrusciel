import requests
from lxml import etree


url = "http://bolt/~sargo/users.xml"

remote_xml = etree.parse(url)

local_xml = etree.parse("runtime/data/users.xml")

if set(remote_xml.getroot().itertext()) != set(local_xml.getroot().itertext()):
    f = open('runtime/data/users.xml', 'w')
    f.write(etree.tostring(remote_xml))
    f.close()
    print "xml overwritten"
else:
    print "xml files do not differ. skipping."
