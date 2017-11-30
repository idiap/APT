# -*- coding: UTF-8 -*-

#####################################################################
# APT.py
#
# This program calculates the accuracy of pronoun translation.
#
# Copyright (c) 20xx Idiap Research Institute, http://www.idiap.ch/
# Written by Lesly Miculich <Lesly.Miculich@idiap.ch>
#
# This file is part of APT.
#
# APT is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 3 as
# published by the Free Software Foundation.
#
# APT is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Foobar. If not, see <http://www.gnu.org/licenses/>.
#
####################################################################


import sys, os
import ConfigParser
import codecs
import numpy
import improve_alignment

sep_nl = "\n"
sep_tab = "\t"
sep_esp = " "
sep_lin = "-"
encoding = "utf-8"
case_2_probabilities = False
other_category = "OTHER"
none_category = "NONE"
full_match = False


def normalize_word(word, list_target_words, dict_equal):
	for i, group in enumerate(dict_equal):
		if word in group:
			return list_target_words.index(group[0])
	if word in list_target_words:
                return list_target_words.index(word)
        return None

    
def normalize_dict_similar(list_target_words, dict_equal, dict_similar):
        new_dict_similar = []
        if case_2_probabilities:
                for i, (s, r, t, p) in enumerate(dict_similar):
                        r = normalize_word(r, list_target_words, dict_equal)
                        t = normalize_word(t, list_target_words, dict_equal)     
                        if r and t:
                                new_dict_similar.append([s, r, t, float(p)])
        else:
                for i, d in enumerate(dict_similar):
                        d = [normalize_word(w, list_target_words, dict_equal) for w in d if w in list_target_words]
                        if len(d)>1: new_dict_similar.append(d)                        
        return new_dict_similar

def normalize_dict_equal(list_target_words, dict_equal):
        new_dict_equal = []
        for d in dict_equal:
                new_d = [w for w in d if w in list_target_words]
                if len(new_d)>1: new_dict_equal.append(new_d)
        return new_dict_equal
    
def similar(word_source, axis_ref, axis_target, dict_similar):
	
	if len(dict_similar):	
		if case_2_probabilities:
                        for s, r, t, p in dict_similar:
                                r, t = set([r]), set([t])
                                if word_source == s:
                                        if full_match:
                                                if r == axis_ref and t == axis_target:
                                                        return p, r, t
                                        else:
                                                if (r & axis_ref) and (t & axis_target):
                                                        return p, r, t
		else:
			for d in dict_similar:
				d = set(d)
				if full_match:
					if axis_ref <= d and axis_target <= d :
						return 1, axis_ref , axis_target 
				else: 
					if axis_ref & d and axis_target & d:
						return 1, axis_ref & d, axis_target & d
				
	return 0, None, None

def equal(axis_ref, axis_target, count_other, index_other):
	if full_match:
		if axis_ref == axis_target:
			if count_other or not index_other or (not index_other in axis_ref):
                        	return axis_ref
			else: return set([])
	else:
		if not count_other and index_other:
			return axis_ref & axis_target - index_other
		else:	
			return axis_ref & axis_target

def get_case(l_source, l_ref, l_target, list_target_words, dict_equal, dict_similar, count_other, index_other):

	word_source = l_source[2]
	prob = 1
	axis_ref = [-1]
	axis_target = [-1]

	if l_ref:
		axis_ref = set([normalize_word(w, list_target_words, dict_equal) for w in l_ref[2]])

	if l_target:
		axis_target = set([normalize_word(w, list_target_words, dict_equal) for w in l_target[2]])

	if not l_ref:
		case = 5 if l_target else 6
	elif not l_target:
		case = 4
	else:
                axis_equal = equal(axis_ref, axis_target, count_other, index_other)
		if axis_equal:
			case, axis_ref, axis_target = 1, axis_equal, axis_equal
		else:
			prob_2, axis_sim_1, axis_sim_2 = similar(word_source, axis_ref, axis_target, dict_similar)
			if prob_2:
                                case, prob, axis_ref, axis_target = 2, prob_2, axis_sim_1, axis_sim_2                                
			else: case = 3

	return case, prob, (axis_ref, axis_target)


def score_words(l_source_words, l_ref_words, l_target_words, l_cases, l_weights, list_target_words, dict_equal, dict_similar, count_multiword, count_other):
	
	cases = numpy.zeros(len(l_cases))
	weights = numpy.array(l_weights)
	matrix = numpy.zeros((len(list_target_words), len(list_target_words)), dtype=int)
	list_cases = [0]*len(l_source_words)
	
	dict_equal = normalize_dict_equal(list_target_words, dict_equal)
        dict_similar = normalize_dict_similar(list_target_words, dict_equal, dict_similar)

	index_other = set([list_target_words.index(other_category)]) if other_category in list_target_words else None
        
	for c, (l_source, l_ref, l_target) in enumerate(zip(l_source_words, l_ref_words, l_target_words)):
		case, prob, pos_matrix = get_case(l_source, l_ref, l_target, list_target_words, dict_equal, dict_similar, count_other, index_other)
		if case in l_cases:
			cases[l_cases.index(case)] += prob
			for i in pos_matrix[0]:
				for j in pos_matrix[1]:
					matrix[i,j] += 1
					if not count_multiword: break
				else: continue
				break
		list_cases[c] = case

	score = float(sum(cases * weights)/sum(cases))
	
	return score, cases, matrix, list_cases		


def get_words_from_position(sentences, l_sentences, l_positions, list_words, sep = None):
	
	with codecs.open(sentences, encoding=encoding) as f:
		l_words = [[]]*len(l_sentences)
		l_all_words = set()
	
		for s, line in enumerate(f):
			if s in l_sentences:	
				line = line.strip().lower().split(sep_esp)
				for i in numpy.where(l_sentences == s)[0]:
					pos = l_positions[i]
					if not pos: continue
					word = [line[p] for p in pos]
					l_words[i] = [pos, word, []]
					
					if list_words:
						
						for w in word:
							for sub_word in w.split(sep):
								if sub_word in list_words:
									l_words[i][2].append(sub_word)
									break
						if not l_words[i][2]: l_words[i][2] = [other_category]
					else:
						l_words[i][2] = word
						l_all_words.update(word)

	return l_words, l_all_words

def get_aligned_positions(l_sentences, l_words, alignment):

	with open(alignment) as f:
		l_positions = [[]]*len(l_sentences)
		
		for s, line in enumerate(f):
			if s in l_sentences:
				line = line.strip().split(sep_esp)
				for i in numpy.where(l_sentences == s)[0]:
					pos = [int(e.split(sep_lin)[1]) for e in line if e.startswith(str(l_words[i][0]) + sep_lin)]
					l_positions[i] = sorted(pos) 

	return l_positions

def get_words_from_list(sentences, list_words, sep_source = None, input_type = "word"):
	
	
	with codecs.open(sentences, encoding=encoding) as f:
		l_sentences = []
		l_words = []
		
		if input_type == "word":
			for i, sentence in enumerate(f):
				sentence = sentence.strip().lower().split(sep_esp)
				for pos, word in enumerate(sentence):
					sub_words = word.split(sep_source)
					for sub_word in sub_words:
						if sub_word in list_words:
							l_sentences.append(i)
							l_words.append([pos, word, sub_word]) 
							break

		elif input_type == "possition":
			with codecs.open(list_words, encoding=encoding) as f_w:
				for i, (sentence, possitions) in enumerate(zip(f, f_w)):
					sentence = sentence.strip().lower().split(sep_esp)
					if possitions.strip() != "":
						possitions = [int(x) for x in possitions.split(sep_esp)]
						for pos in possitions:
							l_sentences.append(i)
						
							l_words.append([pos, sentence[pos], sentence[pos]])
	
	return numpy.array(l_sentences), l_words
			

def get_list_from_file(file_name, sep = None):	
	with codecs.open(file_name, encoding=encoding) as f:
		list_words = [line.strip().lower() for line in f if line.strip() != ""]
	if sep:
		list_words = [w.replace(" ","").split(sep) for w in list_words]
	return list_words

def update_list_target(list_target_words, vocabulary_ref, vocabulary_target):

	if list_target_words:
		list_target_words.append(other_category)
	else:
		list_target_words = list(vocabulary_ref.union(vocabulary_target))

	list_target_words.append(none_category)

	return list_target_words

def print_output_detail(l_sentences, l_source_words, l_ref_words, l_target_words, list_cases, out):
	with codecs.open(out + ".detail", "w", encoding=encoding) as f:
		f.write(sep_tab.join(["SENT.", "POS. SOURCE", "SOURCE", "POS. REF.", "REF.", "POS. TARGET", "TARGET", "CASE"]) + sep_nl)
		for sentence, source, ref, target, case in zip(l_sentences, l_source_words, l_ref_words, l_target_words, list_cases):
			f.write(sep_tab.join([ \
				str(sentence), str(source[0]), source[2], \
				sep_esp.join([str(r) for r in ref[0]] if ref else sep_lin), sep_esp.join(ref[2]) if ref else sep_lin, \
				sep_esp.join([str(t) for t in target[0]] if target else sep_lin), sep_esp.join(target[2]) if target else sep_lin, \
				str(case) \
				]) + sep_nl)
		
def add(matrix, maxtix_row, matrix_col, matrix_dia, list_target_words, word, n = None):

	row_lefth = maxtix_row.sum(0)
	col_lefth = matrix_col.sum(1)

	if n: 
		row_lefth = row_lefth[:n] 
		col_lefth = col_lefth[:n]
		list_target_words = list_target_words[:n]

	col_lefth = numpy.hstack((col_lefth, matrix_dia.sum()))
	col_lefth = numpy.array(numpy.matrix(col_lefth).T)

	matrix = numpy.vstack((matrix, row_lefth))	
	matrix = numpy.hstack((matrix, col_lefth))

	list_target_words = numpy.append(list_target_words, word)
	
	return matrix, list_target_words


def print_output(score, cases, matrix, l_cases, weihgts, list_target_words, out_file, max_len_matrix):
	
	out = "Score: %0.4f\n" % score
	out += "Cases: " + ",".join([str(c) for c in l_cases]) + sep_nl
	out += "Weights: " + ",".join([str(w) for w in weihgts]) + sep_nl
	out += "Findings per case: " + ",".join(["%0.0f" % c for c in cases]) + sep_nl
	out += "Total findings: %0.0f\n" % sum(cases)
	
	order = numpy.argsort(matrix.diagonal()).tolist()
	order.reverse()
	matrix = (matrix[order])[:,order]
	
	list_target_words = numpy.array(list_target_words)[order]


	if len(list_target_words) > max_len_matrix:

		matrix, list_target_words = add(matrix[:max_len_matrix, :max_len_matrix], \
						matrix[max_len_matrix:], matrix[:,max_len_matrix:], \
						matrix[max_len_matrix:,max_len_matrix:], list_target_words, \
						"...", max_len_matrix)
		
	matrix, list_target_words = add(matrix, matrix, matrix, matrix, list_target_words, "-sum-")
	
	out += sep_tab + sep_tab.join(list_target_words) + sep_nl
	
	for label, row in zip(list_target_words, matrix):
		out += label + sep_tab + sep_tab.join([str(r) for r in row]) + sep_nl
	with codecs.open(out_file + ".score", "w", encoding=encoding) as f:
		f.write(out)
	

def aligment(sr_align, st_aling, s, r, t):
	if sr_align.strip() == "":
		sr_align = run_giza(s,r)
	if st_align.strip() == "":
		st_align = run_giza(s,t)
	return sr_align, st_aling
              
def main(argv):

	try:
		print "*** Reading input\n"

		config_file = argv[0]
		open(config_file, 'r')
		config = ConfigParser.RawConfigParser()
		config.read(config_file)

		lang_source = config.get("lang", "source")
		lang_target = config.get("lang", "target")

		sep_source = config.get("lang", "source_word_separator")
		if not sep_source or sep_source.strip() == "":
			sep_source = None
		sep_target = config.get("lang", "target_word_separator")
		if not sep_target or sep_target.strip() == "":
			sep_target = None

		source = config.get("files", "source")
		if not os.path.isfile(source):
			raise NameError("Source file does not exist")
		reference = config.get("files", "reference")
		if not os.path.isfile(reference):
			raise NameError("Reference file does not exist")
		target = config.get("files", "target")
		if not os.path.isfile(target):
			raise NameError("Target file does not exist")
		align_sr = config.get("files", "alignment_source_reference")
		if not os.path.isfile(align_sr):
			raise NameError("Source-reference alignment file does not exist")
		align_st = config.get("files", "alignment_source_target")
		if not os.path.isfile(align_st):
			raise NameError("Target-reference alignment file does not exist")
		input_type = config.get("files", "input_type")
		list_source_words = config.get("files", "list_source_pronouns")
		if not os.path.isfile(list_source_words):
			print "Not list of source pronouns"		
			list_source_words = []
		elif input_type == "word":
			list_source_words = get_list_from_file(list_source_words)
		list_target_words = config.get("files", "list_target_pronouns")
		if not os.path.isfile(list_target_words):
			print "Not list of target pronouns"		
			list_target_words = []
		else:
			list_target_words = get_list_from_file(list_target_words)

		dict_equal= config.get("dictionary", "equal")		
		if not os.path.isfile(dict_equal):
			print "Not dictionary of equal pronouns"
			dict_equal = []
		else:
			dict_equal = get_list_from_file(dict_equal, sep = ",")
		dict_similar= config.get("dictionary", "similar")
		if not os.path.isfile(dict_similar):
			print "Not dictionary of similar pronouns"		
			dict_similar = []
		else:
			dict_similar = get_list_from_file(dict_similar, sep = ",")
		dict_source_words = config.get("dictionary", "source_pronouns")
		if not os.path.isfile(dict_source_words):
			print "Not dictionary of source pronouns"
			dict_source_words = []
		else:
			dict_source_words = get_list_from_file(dict_source_words)
		dict_target_words = config.get("dictionary", "target_pronouns")
		if not os.path.isfile(dict_target_words):
			print "Not dictionary of target pronouns"
			dict_target_words = []
		else:
			dict_target_words = get_list_from_file(dict_target_words)
		l_cases = config.get("cases", "cases_to_use")
		if l_cases:
			l_cases = [int(c.strip()) for c in l_cases.split(",") if int(c.strip()) in range(1,7)]
		else:
			raise NameError("List of cases to use is empty")
		weights = config.get("cases", "weigths_per_case")
		if weights:
			weights = [float(c.strip()) for c in weights.split(",")]
		else:
			raise NameError("List of weights is empty")
		count_other = config.getboolean("cases", "count_OTHER_as_equal")

		out = config.get("output", "output_file")
		count_multiword = config.getboolean("output", "counting_multiword_in_matrix")
		max_len_matrix = config.getint("output", "max_length_matrix")
                
		print "*** End Reading input\n"

	except IndexError:
        	print 'Missing argument. Use:\n\t python APT.py <configuration file>' 
        	sys.exit(2)
	except IOError:
		print 'File does not exits. Use:\n\t python APT.py <configuration file>' 
        	sys.exit(2)
	except 	NameError as e:
		print "Input error: " + e.message
		sys.exit(2)
	except:
    		print("Unexpected error:", sys.exc_info()[0])
    		raise
	

	

	l_sentences, l_source_words = get_words_from_list(source, list_source_words, sep_source, input_type)
	l_ref_pos = get_aligned_positions(l_sentences, l_source_words, align_sr)
	l_ref_words, l_ref_vocabulary = get_words_from_position(reference, l_sentences, l_ref_pos, list_target_words, sep_target )
	l_target_pos = get_aligned_positions(l_sentences, l_source_words, align_st)
	l_target_words, l_target_vocabulary  = get_words_from_position(target, l_sentences, l_target_pos, list_target_words, sep_target )

	print "*** Improving alignment\n"
	print "For reference:"
	improve_alignment.improve_alignment(l_sentences, l_source_words, l_ref_words, source, reference, align_sr, dict_source_words, dict_target_words)
	print "For target:"
	improve_alignment.improve_alignment(l_sentences, l_source_words, l_target_words, source, target, align_st, dict_source_words, dict_target_words)
	print "*** End improving alignment\n"

	print "*** Calculating score\n"

	list_target_words = update_list_target(list_target_words, l_ref_vocabulary, l_target_vocabulary)

	score, cases, matrix, list_cases = score_words(l_source_words, l_ref_words, l_target_words, l_cases, weights, list_target_words, dict_equal, dict_similar, count_multiword, count_other)
	
	print_output_detail(l_sentences, l_source_words, l_ref_words, l_target_words, list_cases, out)
	print_output(score, cases, matrix, l_cases, weights, list_target_words, out, max_len_matrix)
	
	
	print "Score: %0.2f" % score
	print "More details in output files"
	print "*** End calculating score\n"


if __name__ == "__main__":
    main(sys.argv[1:])
