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

import codecs

n_neighbors= 2
max_neighbors = 1
sep_esp = " "
encoding = "utf-8"
other_category = "OTHER"


def get_align(pw, align, get="target"):
	r_pw = []
	
	for e in align:
		pws, pwt = e.split("-")
		pws = int(pws)
		pwt = int(pwt)

		if get == "target":
			if (pws == pw):
				r_pw.append(pwt)
		
		elif get == "source":
			if (pwt == pw):
				r_pw.append(pws)
	return r_pw

def search_target(n_sent, pos_source, word_source, pos_target, word_target, sent_source, sent_target, align, source_valid_words, target_valid_words):    
	
	for w in word_target:
		if w in target_valid_words:
			return pos_target, word_target
	pos_range = []    
	if pos_target == []:  
		pos_left = pos_right = []  	
		for i in range(1 , max_neighbors):
			pos_left = get_align( max(pos_source - i , 0), align)
			if (pos_left != [] and pos_left != pos_target) or pos_source - i < 0: break 

		for i in range(1 , max_neighbors):
			pos_right = get_align( min(pos_source + i, len(sent_source) - 1), align)
			if (pos_right != [] and pos_right != pos_target) or pos_source + i >= len(sent_source): break 
		pos_range = sorted(list((set(pos_left + pos_right))))
	else:
		pos_range = sorted([int(x) for x in pos_target])

	
	if pos_range != []:

                imin = max(pos_range[0] - n_neighbors, 0)
                imax = min(pos_range[-1] + n_neighbors, len(sent_target) - 1)
		 
		n_cand = imax - imin + 1
		cand_weight = range(n_cand/2, 0,-1) + [1]*(n_cand % 2) + range(1, n_cand/2 + 1, 1) # Depend on the closeness to the center of the range

		l_cand = []
		l_cand_weight = []

		for pos_cand, we_cand in zip(range(imin, imax + 1), cand_weight):                            
			
			word_cand = sent_target[pos_cand].split("-")[-1] # In case of composed words                             

			if word_cand in target_valid_words and word_cand not in word_target:
				target_cand = get_align(pos_cand, align, get="source")
				found = False
 				for pos_tc in target_cand:
					if sent_source[pos_tc] in source_valid_words:
						found = True
						break
				
				if not found:
                        		l_cand.append(pos_cand)
					l_cand_weight.append(we_cand)
                                                             
		if len(l_cand)>0:
			# Select the first min weight candidate 
			pos_cand = l_cand_weight.index(min(l_cand_weight))
			pos_target.append(l_cand[pos_cand])
			if len(word_target) == 1 and word_target[0] == other_category:
				word_target.remove(other_category)	
			word_target.append(sent_target[l_cand[pos_cand]])
			print n_sent, pos_source, word_source, l_cand[pos_cand], sent_target[l_cand[pos_cand]]

	return  pos_target, word_target

def improve_alignment(l_sentences, l_source_words, l_target_words, source_sentences, target_sentences, alignment, source_valid_words, target_valid_words):
	with codecs.open(source_sentences, encoding=encoding) as f:
		source_sentences = [l.strip().split(sep_esp) for l in f]	

	with codecs.open(target_sentences, encoding=encoding) as f:
		target_sentences = [l.strip().split(sep_esp) for l in f]

	with codecs.open(alignment, encoding=encoding) as f:
		alignment = [l.strip().split(sep_esp) for l in f]

	for n_sent, source, target in zip(l_sentences, l_source_words, l_target_words):
		if target != []:
			target[0], target[2] = search_target(n_sent, source[0], source[2], target[0], target[2], source_sentences[n_sent], target_sentences[n_sent], alignment[n_sent], source_valid_words, target_valid_words)
		else:
			pos_t = []
			word_t = []
			pos_t, word_t = search_target(n_sent, source[0], source[2], pos_t, word_t, source_sentences[n_sent], target_sentences[n_sent], alignment[n_sent], source_valid_words, target_valid_words)
			if pos_t != []:
				target = [pos_t, word_t, word_t]
