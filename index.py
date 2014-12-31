#!/usr/bin/python3
import cgi
import cgitb
import os
import subprocess
import time

cgitb.enable()

print("Content-type: text/html\n")

form = cgi.FieldStorage()
mode = int(form.getvalue("mode", 0))

if not mode:
    time_in_secs = os.path.getmtime('./safe_pyth.py')
    time_in_python = time.gmtime(time_in_secs)
    formatted_time = time.strftime("%d %b %Y", time_in_python)
    print(open('index.html').read().replace('formatted_time', str(formatted_time)))
elif mode==1:
    print(open('web-docs.txt').read())
elif mode==2:
    resp=""
    code_message = form.getvalue("code", "")
    input_message = form.getvalue("input", "")
    debug_on = int(form.getvalue("debug", 0))

    pyth_code = code_message.split("\r\n")[0]
    pyth_process = \
        subprocess.Popen(["/usr/bin/python3",
                          "safe_pyth.py",
                          "-cd" if debug_on else "-c",
                          pyth_code],
                         stdin=subprocess.PIPE,
                         stdout=subprocess.PIPE,
                         stderr=subprocess.STDOUT)
    output, errors = \
        pyth_process.communicate(input=bytearray(input_message, 'utf-8'))
    if code_message:
        resp+="Output: \n"
        resp+='<pre class="scroll">'+output.decode()+(errors if errors else '')+'</pre>'

    print(resp)
