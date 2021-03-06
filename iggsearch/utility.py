#!/usr/bin/env python

import io, os, stat, sys, resource, gzip, platform, bz2, time

def log_time(program_start, module_start):
	current_time = time.time()
	program_time = round(current_time - program_start, 2)
	module_time = round(current_time - module_start, 2)
	peak_ram = round(max_mem_usage(), 2)
	print("  module: %s seconds, program: %s seconds, peak RAM: %s GB" % (module_time, program_time, peak_ram))

def which(program):
	""" Mimics unix 'which' function """
	def is_exe(fpath):
		return os.path.isfile(fpath) and os.access(fpath, os.X_OK)
	for path in os.environ["PATH"].split(os.pathsep):
		path = path.strip('"')
		exe_file = os.path.join(path, program)
		if is_exe(exe_file):
			return True
	return False

def auto_detect_file_type(inpath):
	""" Detect file type [fasta or fastq] of <p_reads> """
	infile = iopen(inpath)
	for line in infile:
		if line[0] == '>': return 'fasta'
		elif line[0] == '@': return 'fastq'
		else: sys.exit("Error: Filetype [fasta, fastq] of %s could not be recognized\n" % inpath)
	infile.close()

def check_compression(inpath):
	""" Check that file extension matches expected compression """
	ext = inpath.split('.')[-1]
	file = iopen(inpath)
	try:
		next(file)
		file.close()
	except:
		sys.exit("\nError: File extension '%s' does not match expected compression\n" % ext)

def iopen(inpath, mode='r'):
	""" Open input file for reading regardless of compression [gzip, bzip] or python version """
	ext = inpath.split('.')[-1]
	# Python2
	if sys.version_info[0] == 2:
		if ext == 'gz': return gzip.open(inpath, mode)
		elif ext == 'bz2': return bz2.BZ2File(inpath, mode)
		else: return open(inpath, mode)
	# Python3
	elif sys.version_info[0] == 3:
		if ext == 'gz': return io.TextIOWrapper(gzip.open(inpath, mode))
		elif ext == 'bz2': return bz2.BZ2File(inpath, mode)
		else: return open(inpath, mode)

def parse_file(inpath):
	""" Yields records from tab-delimited file with header """
	infile = iopen(inpath)
	fields = next(infile).rstrip('\n').split('\t')
	for line in infile:
		values = line.rstrip('\n').split('\t')
		if len(fields) == len(values):
			yield dict([(i,j) for i,j in zip(fields, values)])
	infile.close()

def max_mem_usage():
	""" Return max mem usage (Gb) of self and child processes """
	max_mem_self = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
	max_mem_child = resource.getrusage(resource.RUSAGE_CHILDREN).ru_maxrss
	if platform.system() == 'Linux':
		return round((max_mem_self + max_mem_child)/float(1e6), 2)
	else:
		return round((max_mem_self + max_mem_child)/float(1e9), 2)

def check_bamfile(args, bampath):
	""" Use samtools to check bamfile integrity """
	import subprocess as sp
	command = '%s view %s > /dev/null' % (args['samtools'], bampath)
	process = sp.Popen(command, shell=True, stdout=sp.PIPE, stderr=sp.PIPE)
	out, err = process.communicate()
	if err.decode('ascii') != '': # need to use decode to convert to characters for python3
		err_message = "\nWarning, bamfile may be corrupt: %s\nSamtools reported this error: %s\n" % (bampath, err.rstrip())
		sys.exit(err_message)





