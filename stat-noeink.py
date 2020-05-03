import requests
import gzip
import io
import xml.etree.ElementTree as ET
import shutil
from clint.textui import progress
import subprocess as cmd

def main_func():
	#host_file_url = "https://ralph.bakerlab.org/stats/host.gz"
	host_file_url = "https://boinc.bakerlab.org/rosetta/stats/host.gz"

	print("Downloading")
	r = requests.get(host_file_url, stream = True)
	with open("/home/ric/download.gz", "wb") as data:
		total_length = int(r.headers.get('content-length'))
		for chunk in progress.bar(r.iter_content(chunk_size = 1024), expected_size=(total_length/1024) + 1):
			if chunk:
				data.write(chunk)

	print("Decompressing")
	with open('/home/ric/download.xml', 'wb') as f_out, gzip.open('/home/ric/download.gz', 'rb') as f_in:
		shutil.copyfileobj(f_in, f_out)

	print("Parsing")
	arm_count = 0
	credit = 0.0
	arm_flag = 0
	tree = ET.iterparse("/home/ric/download.xml", events=("start", "end"))
	is_first = True
	for event, elem in tree:
		if elem.tag == "total_credit" and event == "end":
			tcredit = float(elem.text)
			elem.clear()
		if elem.tag == "p_vendor" and event == "end" and elem.text == "ARM":
			arm_flag = 1
			elem.clear()
		elif elem.tag == "p_vendor" and event == "end" and elem.text != "ARM":
			arm_flag=0
			elem.clear()
		if arm_flag == 1 and elem.tag == "os_name" and event == "end" and elem.text != "Android":
			arm_count=arm_count+1
			credit = credit + tcredit
			print(elem.text)
			elem.clear()
		if elem.tag == "host" and event == "end":
			elem.clear()
		if elem.tag == "hosts" and event == "end":
			elem.clear()

	print("Non Android ARM machine count = %s" % arm_count)
	print("Combined Credit = %f" % credit)
	readme = open('README.md', 'w')
	print("# Non Android ARM machine count = %s \n" % arm_count, file = readme)
	print("# Combined Credit = %f" % credit, file = readme)
	readme.close()
	cp = cmd.run("rm -rf download*", check=True, shell=True)
	cp = cmd.run("git add .", check=True, shell=True)
	cp = cmd.run("git commit -m 'Update Stats'", check=True, shell=True)
	cp = cmd.run("git push", check=True, shell=True)

if __name__ == '__main__':
    main_func()
