from __future__ import unicode_literals
import itertools
from collections import defaultdict,Counter

neighboring = [(-1,0),(0,-1),(1,0),(0,1),(-1,-1),(-1,1),(1,-1),(1,1)]

def eSort(alignment):
	return sorted(alignment, key=lambda x:100*x[1]+x[0])

def fSort(alignment):
	return sorted(alignment, key=lambda x:100*x[0]+x[1])

def getEs(alignment):
	return [a[1] for a in alignment]

def getFs(alignment):
	return [a[0] for a in alignment]

#first
def growDiagFinal(word_e2f, word_f2e, char_e2f,char_f2e):
	
	# word_alignment = intersect(word_e2f,word_f2e)
	word_alignment = intersect(word_e2f,char_f2e)

	# char_alignment = intersect(char_e2f,char_f2e)
	char_alignment = intersect(word_e2f,char_f2e)

	e2f = list(set(word_e2f).intersection(char_e2f))
	f2e = list(set(word_f2e).intersection(char_f2e))

	alignment = list(set(word_alignment).intersection(char_alignment))
	if len(alignment) != 0:
		growDiag(alignment, e2f, f2e)
	
	finalAnd(e2f, alignment)
	finalAnd(word_e2f, alignment)#delete

	finalAnd([a[::-1] for a in f2e ], alignment);
	finalAnd([a[::-1] for a in char_f2e ], alignment);#delete

	return alignment

def intersect(e2f, f2e):
	return [(f,e) for f,e in e2f if (e,f) in f2e]

def growDiag(alignment, e2f, f2e):
	edit = True
	while edit:
		edit = False
		for e, f in itertools.product(range(max(getEs(alignment))+1), range(max(getFs(alignment))+1)):
			if (f, e) not in alignment:	continue
			for x,y in  neighboring:
				enew, fnew = e+x, f+y
				if (enew not in getEs(alignment) or fnew not in getFs(alignment)) and (((fnew, enew) in e2f) or ((enew, fnew) in f2e)):
					alignment.append((fnew, enew))
					edit = True
		if not edit:	break

def final(a, alignment):
	for fnew, enew in a:
		if (enew not in getEs(alignment) or fnew not in getFs(alignment)) and ((fnew, enew) in a):
			alignment.append((fnew, enew))

def finalAnd(a, alignment):
	for fnew, enew in a:
		if (enew not in getEs(alignment) and fnew not in getFs(alignment)) and ((fnew, enew) in a):
			alignment.append((fnew, enew))

def readAlign(s):
	return [tuple(map(int, i.split('-'))) for i in s.split(' ')]

def change_char_to_word(char_e2f, char_f2e, sent):
	char_f2e = sorted(char_f2e,key=lambda x:x[1])
	char_e2f = sorted(char_e2f,key=lambda x:x[1])
	word_lens = map(len, sent.split())
	word_lens_sums = reduce(lambda  s, l: s + [s[-1]+l], word_lens, [0])
	
	new_char_f2e = []
	for i,(start,end) in enumerate(zip(word_lens_sums,word_lens_sums[1:])):
		x = [ e for e,f in char_f2e if f in range(start,end)]
		if len(x) == 0:
			pass
		elif x.count(x[0]) == len(x) == len(range(start,end)):
			new_char_f2e.append((x[0],i))
		else:
			# method 1
			# new_char_f2e.append( (Counter(x).most_common(1)[0][0],i) )
			# mothod 2
			# new_char_f2e.append( (x[0],i) )
			# method 3
			for e,f in char_f2e:
				if f in range(start,end):
					new_char_f2e.append((e,i))
				
	new_char_e2f = []
	mapping = { r:i for i,(start,end) in enumerate(zip(word_lens_sums,word_lens_sums[1:])) for r in range(start,end)}
	for f,e in char_e2f:
		new_char_e2f.append((mapping[f],e))

	return new_char_e2f,new_char_f2e

def change_word_to_char(word_e2f, word_f2e, sent):
	word_e2f = sorted(word_e2f,key=lambda x:x[1])
	word_f2e = sorted(word_f2e,key=lambda x:x[1])
	word_lens = map(len, sent.split())
	word_lens_sums = reduce(lambda  s, l: s + [s[-1]+l], word_lens, [0])	

	mapping = defaultdict(lambda:[])
	for i,(start,end) in enumerate(zip(word_lens_sums,word_lens_sums[1:])):
		for r in range(start,end):
			mapping[i].append(r)
	
	new_word_f2e = []
	for e,f in word_f2e:
		for item in mapping[f]:
			new_word_f2e.append((e,item))

	new_word_e2f = []
	for f,e in word_e2f:
		for item in mapping[f]:
			new_word_e2f.append((item,e))

	return new_word_e2f,new_word_f2e
	
def main():
	fp = open("../t74/t74.gdfa.txt",'w')
	word_set = list(itertools.imap(lambda x:map(readAlign,x), itertools.izip(*map(open, ['../t74/t74.en-ch.txt', '../t74/t74.ch-en.txt']))))
	char_set = list(itertools.imap(lambda x:map(readAlign,x), itertools.izip(*map(open, ['../t74/t74.char.en-ch.txt', '../t74/t74.char.ch-en.txt']))))
	ch_sents = open("../t74/t74.clean.ch.txt").read().decode("utf-8").split("\n")
	ans_buffer = []
	for word, char ,ch_sent in zip(word_set,char_set,ch_sents):
		word_e2f, word_f2e, char_e2f, char_f2e = word[0],word[1],char[0],char[1]
		#method1
		char_e2f, char_f2e = change_char_to_word(char_e2f, char_f2e,ch_sent)
		alignment = growDiagFinal(word_e2f, word_f2e, char_e2f,char_f2e)
		# # ../t74/t74.gdfa.txt - ../t74/t74.ans.txt
		# precision: 0.700
		# recall: 0.705
		# f-measure: 0.702


		# method2
		# word_e2f, word_f2e = change_word_to_char(word_e2f, word_f2e,ch_sent)
		# alignment = growDiagFinal(word_e2f, word_f2e, char_e2f,char_f2e)
		# alignment,_ = change_char_to_word(alignment,[],ch_sent)
		# alignment = list(set(alignment))
		# ../t74/t74.gdfa.txt - ../t74/t74.ans.txt
		# precision: 0.682
		# recall: 0.709
		# f-measure: 0.695
		
		ans_buffer.append(' '.join(['%d-%d'%a for a in eSort(alignment)]))
	fp.write("\n".join(ans_buffer))
	fp.close()


main()
