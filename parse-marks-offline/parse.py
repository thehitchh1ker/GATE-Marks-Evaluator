import requests as r
import re
import json
import argparse
from decimal import *
from pprint import pprint
from bs4 import BeautifulSoup

# Command line arguments.
response_url = None
answer_key_url = None
cmd_parser = argparse.ArgumentParser(
    description="Parses candidate's response sheet, calculates marks, and stores results as JSON.")
cmd_parser.add_argument(
    '-r', '--response', help="Candidate's response key URL.", dest='response_url')
cmd_parser.add_argument(
    '-k', '--key', help="Answer key URL.", dest='answer_key_url')
cmd_parser.add_argument('-o', help="Print output to file.", dest="file_name")
args = cmd_parser.parse_args()

response_url = args.response_url
answer_key_url = args.answer_key_url
file_name = args.file_name
if(response_url == None):
    response_url = input('Enter Response Sheet URL: ')
if(answer_key_url == None):
    answer_key_url = input('Enter Answer Key URL: ')
# pprint(response_url)
# pprint(answer_key_url)

# Get the response sheet
candidate_response = BeautifulSoup(r.get(response_url).text, 'html.parser')
# Locate the data
candidate_response_rows = candidate_response.find_all(
    'table', {'class': 'menu-tbl'})
question_tables = candidate_response.find_all(
    'table', {'class': 'questionRowTbl'})

# section labels, which are not used so far
sections = candidate_response.find_all('div', {'class': 'section-lbl'})

# Get the answer key (Google sheet URL, as mentioned)
ans_key_response = BeautifulSoup(r.get(answer_key_url).text, 'html.parser')
ans_table = ans_key_response.find_all('td')


'''
Parses the candidate response page
On successful parsing, it returns a list(65),
with each element as,
{
    'short_id':'',
    'marks':'',
    'type':'',
    'long_id':'',
    'status':'',
    'response_given':''
}
'''


def parse_candidate_response():
    response_data = []
    for i, row in enumerate(candidate_response_rows):
        j = i+1
        current_question = {}
        question_imgs = question_tables[i].find_all('img')
        names = [a['src'] for a in question_imgs]
        # pprint(names)
        # names = [str(a.src) for a in question_imgs]
        # pprint(names)
        short_id = None
        options = []
        if(len(names) == 5):
            # then we have MCQ/MSQ
            for i, ee in enumerate(names):
                m1 = re.findall(r'.*_ga(\d*)q(\d*)([a-d]?)\.png', ee)
                m2 = re.findall(r'.*_cs(\d*)q(\d*)([a-d]?)\.png', ee)
                # set number is of no use?
                # set_no = m[0]
                m = m2 if len(m1) < len(m2) else m1
                pref = 'c' if m == m2 else 'g'
                m = m[0]
                if i == 0:
                    short_id = f'{pref}{m[1]}'
                    continue
                options.append(m[2].upper())
        elif(len(names) == 1):
            # then we have NAT
            m1 = re.findall(r'.*_ga(\d*)q(\d*)([a-d]?)\.png', names[0])
            m2 = re.findall(r'.*_cs(\d*)q(\d*)([a-d]?)\.png', names[0])
            # set number is of no use?
            # set_no = m[0]
            m = m2 if len(m1) < len(m2) else m1
            pref = 'c' if m == m2 else 'g'
            m = m[0]
            short_id = f'{pref}{m[1]}'
        # pprint(short_id)
        # pprint(options)
        j = int(short_id[1:])
        if short_id[0] == 'g':
            if j <= 5:
                current_question['marks'] = 1.0
            else:
                current_question['marks'] = 2.0
        else:
            if j <= 25:
                current_question['marks'] = 1.0
            else:
                current_question['marks'] = 2.0
        data = row.find_all('td')
        question_type = data[1].text
        question_id = data[3].text
        status = str(data[5].text)

        # in case of NAT questions, the answer's position is changed, so we have to ADAPT as well.
        if question_type == 'NAT':
            response_given = question_tables[i].find_all('td')[-1].text
        else:
            if status == 'Not Answered' or data[7].text == ' -- ':
                response_given = ' -- '
            else:
                response_given_raw = [
                    int(a)-1 for a in data[7].text.split(',')]
                response_given_raw = [options[a] for a in response_given_raw]
                response_given = ','.join(response_given_raw)
        # pprint(f'choice {response_given}')
        # pprint('-----')
        # TODO: Don't know how the representation is, when a question is marked for review but not answered, for now, assuming it will have ' -- ' as response
        current_question['short_id'] = short_id
        current_question['type'] = question_type
        current_question['long_id'] = question_id
        current_question['status'] = status
        current_question['response_given'] = response_given

        # temporary key for sorting as in answer key
        current_question['temp'] = 10000 if(short_id[0] == 'c') else 100
        current_question['temp'] += int(short_id[1:])
        response_data.append(current_question)
    return response_data


'''
Parses the google sheet of the answer key.
On successful parsing, it returns list(65),
with each element as,
{
    'short_id':'',
    'answer_key':'',
    'go_url':'',
    'subject_id':'',
}
'''


def parse_answer_key():
    ans_data = []
    current_ans = {}
    for i, each in enumerate(ans_table):
        if(i < 4):
            continue
        if i % 4 == 0:
            current_ans = {}
            current_ans['short_id'] = each.text
        elif i % 4 == 1:
            # this column has extra double quotes, which we ignore
            current_ans['answer_key'] = each.text[1:-1]
        elif i % 4 == 2:
            current_ans['go_url'] = each.text
        elif i % 4 == 3:
            current_ans['subject_id'] = each.text
            ans_data.append(current_ans)
    return ans_data


cres = parse_candidate_response()
cres = sorted(cres, key=lambda k: k['temp'])
# pprint(cres)

ares = parse_answer_key()

# merge required properties into one list into cres, in this case
for i, ans_row in enumerate(ares):
    for key in ans_row:
        if key == 'answer_key' or key == 'subject_id':
            cres[i][key] = ans_row[key]


# determines precision based on answerkey
def get_precision(s):
    i = 0
    ans = 0
    seen_dot = False
    while i < len(s):
        if(s[i] == '.'):
            seen_dot = True
            i += 1
            continue
        if(seen_dot):
            ans += 1
        i += 1
    return ans


# calculating obtained_marks for each individual question, and storing it as cres
def calculate_marks():
    for i, q in enumerate(cres):
        if q['status'] == 'Not Answered' or q['response_given'] == '--':
            cres[i]['obtained_marks'] = 0
            continue
        if q['type'] == 'MCQ':
            cres[i]['obtained_marks'] = q['marks'] if q['response_given'] == q['answer_key'] else (
                (-1.0/3.0)*q['marks'])
        elif q['type'] == 'MSQ':
            all_ans = q['answer_key'].split(';')
            all_chosen = [str(a) for a in q['response_given'].split(',')]
            correct = sorted(all_ans) == sorted(all_chosen)
            cres[i]['obtained_marks'] = float(q['marks']) if correct else 0.0
        elif q['type'] == 'NAT':
            ans_range = q['answer_key'].split(':')
            getcontext().prec = max(1, get_precision(ans_range[0]))
            ans_range = [Decimal(a) for a in q['answer_key'].split(':')]
            correct = True
            if(len(ans_range) == 1):
                correct = Decimal(q['response_given']) == ans_range[0]
            else:
                res_given = Decimal(q['response_given'])
                correct = res_given >= ans_range[0] and res_given <= ans_range[1]
            cres[i]['obtained_marks'] = float(
                q['marks']) if correct else 0.0


# here, cres hopefully contains all the required parameters
# print json to stdout so we get json by
# python3 parse.py > res.json
# TODO: maybe use file instead of stdout?
calculate_marks()
# removing the temp variable
for each in cres:
    del each['temp']

if file_name == None:
    print(json.dumps(cres, indent=4))
else:
    with open(file_name, 'w+') as f:
        print(json.dumps(cres, indent=4), file=f)


def total_marks():
    getcontext().prec = 10
    total_attempt = 0
    incorrect_attempt = 0
    negative_marks = 0
    total_marks = 0
    for e in cres:
        if e['status'] == 'Not Answered' or e['response_given'] == ' -- ':
            continue
        if e['obtained_marks'] <= 0:
            negative_marks += Decimal(e['obtained_marks'])
            incorrect_attempt += 1
        total_marks += Decimal(e['obtained_marks'])
        total_attempt += 1

    print(f'Attempts: ({total_attempt}/{65})')
    print(f'Incorrect Attempts: ({incorrect_attempt}/{65})')
    print(f'Total Marks: {(total_marks + Decimal(-1)*negative_marks):.2f}')
    print(f'Negative Marks: {negative_marks:.2f}')
    print(f'Final Marks: {total_marks:.2f}')


# print some info if -o is provided
if file_name is not None:
    total_marks()
