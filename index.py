#!/usr/bin/python3
import cgi
import cgitb
import os
import subprocess
import time

cgitb.enable()

print("Content-type: text/html\n")

print("""
<html>

<head>
    <title>Pyth Compiler/Executor</title>
    <link rel="shortcut icon" href="/pyth/favicon2.ico" />
</head>

<body>

  <h3> <a href="https://github.com/isaacg1/pyth">Pyth</a>
  Compiler/Executor </h3>""")

form = cgi.FieldStorage()
code_message = form.getvalue("code", "")
input_message = form.getvalue("input", "")
debug_message = form.getvalue("debug", "off")

if debug_message == "on":
    debug_on = True
else:
    debug_on = False

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
    print("<p>Output:</p>")

print("<pre>")
for line in output.decode().split('\n'):
    print(cgi.escape(line))

if errors:
    for line in errors.split('\n'):
        print(cgi.escape(line))

time_in_secs = os.path.getmtime('./safe_pyth.py')
time_in_python = time.gmtime(time_in_secs)
formatted_time = time.strftime("%d %b %Y", time_in_python)


print("""</pre>

  <form id="code_input" method="post" action="index.py">
   <p><input type="submit" value="Run!" style="background-color: #00FFFF"/></p>
   <p>Debug on?: <input type="checkbox" name="debug" {4}/></p>
  </form>

  <p>Code:</p>
  <textarea name="code" form="code_input" cols="80" rows="10">{0}</textarea>

  <p>Input:</p>
  <textarea name="input" form="code_input" cols="80" rows="10">{2}</textarea>

  <p>Code length: {1}</p>

  <p>Compiler last updated: {3} GMT</p>

</body>

</html>
""".format(cgi.escape(code_message),
           len(code_message),
           cgi.escape(input_message),
           formatted_time,
           'checked="checked"' if debug_on else ''))
