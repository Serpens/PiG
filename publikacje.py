#!/usr/bin/env python
import os,sys
import csv
import json
from random import choice

# TODO: parameters
TOOL_ATTRIBUTES=[] #keys from json file #poki co nie wiem czy w ogole to potrzebne
WORKFLOW_ATTRIBUTES=[] #keys from csv file #poki co nie wiem czy w ogole to potrzebne


def loadcsv(csv_filename, bib_filename):
    global TOOL_ATTRIBUTES
    csv_file = open(csv_filename)
    csv_reader = csv.reader(csv_file, delimiter=',', quotechar='"')
    rowlist = [row for row in csv_reader]
    headers = rowlist[0]
    headers[0]='tool_id' #zakladam identyfikacje toola po tool_id a nie name; podmieniam nazwe kolumny 'tool_name_galaxy'
    TOOL_ATTRIBUTES = headers #poki co nie wiem czy w ogole to potrzebne
    rowlist = rowlist[1:]
    
    output_lines = []
    output_dict = {}

    for row in rowlist:
        tool = dict(zip(headers, row))
        tool_lines = ['@article{' + tool['tool_id'] + ',\n']
        for key in tool.keys():
            tool_lines.append('        %s = {%s},\n' % (key, tool[key]))
        tool_lines[-1] = tool_lines[-1][:-2] + '\n' # remove comma
        tool_lines.append('}\n\n')
        output_lines.extend(tool_lines)
        output_dict[tool['tool_id']] = tool
    
    output_file = open(bib_filename, 'w')
    output_file.writelines(output_lines)
    output_file.close()
    csv_file.close()
    return output_dict


def parsuj(plik):
    f = open(plik, 'r')
    return(json.load(f)['steps'])


def build_line(template, step):
    output = []
    # {}
    segments = template.split('}')
    new_template = []
    for s in segments:
        try:
            const, rand = s.split('{')
        except:
            const, rand = s,''
        new_template.extend([const, choice(rand.split('|'))])
    new_template = ''.join(new_template)
    # %%
    segments = new_template.split('%')
    for s in xrange(len(segments)/2):
        output.extend([segments[s*2], step[segments[s*2+1]]])
    """for s in xrange(0,len(segments)-1,2):
        output.extend([segments[s], step[segments[s+1]]])"""
    output.append(segments[-1])
    return ''.join(output)


def build_paragraph(step, templates):
    output = ''

    step['version']=step['tool_version'] #trzeba bedzie albo wymagac aby w pliku csv w template wystepowaly klucze z json (np 'tool_version' a nie 'version') albo jakos elegancko podmienic nazwy kluczy

    if templates.has_key(step['tool_id']):
    	output += build_line(templates[step['tool_id']], step)

    return output


def main():

    reference_dict = loadcsv(sys.argv[1], sys.argv[2])

    output = []
    raw_steps = parsuj(sys.argv[3])
    steps = []

    WORKFLOW_ATTRIBUTES=raw_steps['0'].keys() #poki co nie wiem czy w ogole to potrzebne

    #print WORKFLOW_ATTRIBUTES; return 0

    templates = {}

    print reference_dict['biomart_test']

    for ref in reference_dict:
        if reference_dict[ref].has_key('template'): #poki co jak nie ma w csv 'template' do danego narzedzia to nawet to narzedzie nie ma klucza 'template'. trzeba albo ustawic jakis parametr w csv.readerze albo wczytywac linie i robic split po przecinku.
            templates[ref] = reference_dict[ref]['template']

    sorted_keys = sorted([int(i) for i in raw_steps.keys()])
    for sort in sorted_keys:
        s = str(sort)
        steps.append(raw_steps[s])

    # create text
    for i in xrange(len(steps)):
         output.append(build_paragraph(steps[i], templates))

    output_file=open(sys.argv[4], 'w')
    output_file.write(' '.join(output))
    output_file.close()
    print '\n'.join(output)


if __name__=='__main__':
    main()


