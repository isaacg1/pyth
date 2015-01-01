#!venv/bin/python
from flask import Flask, render_template, request, Response
import os
import time
import subprocess

app = Flask(__name__, template_folder='.', static_folder='.')

@app.route('/')
def root():
	time_in_secs = os.path.getmtime('safe_pyth.py')
	time_in_python = time.gmtime(time_in_secs)
	formatted_time = time.strftime("%d %b %Y", time_in_python)
	return render_template('index.html', formatted_time=formatted_time)

@app.route('/submit', methods=['POST'])
def submit():
	resp = ''

	code_message = request.form.get('code', '')
	input_message = request.form.get('input', '')
	debug_on = int(request.form.get('debug'), 0)

	pyth_code = code_message.split("\r\n")[0]
	pyth_process = \
		subprocess.Popen(['/usr/bin/env',
						  'python3',
						  'safe_pyth.py',
						  '-cd' if debug_on else '-c',
						  pyth_code],
						 stdin=subprocess.PIPE,
						 stdout=subprocess.PIPE,
						 stderr=subprocess.STDOUT)

	output, errors = \
		pyth_process.communicate(input=bytearray(input_message, 'utf-8'))

	if code_message:
		resp += 'Output: \n'
		resp += '<pre class="scroll">' + output.decode() + (errors if errors else '') + '</pre>'

	return Response(resp)

@app.route('/<path>')
def other(path):
	return app.send_static_file(path)

if __name__ == '__main__':
	app.run(debug=True)
