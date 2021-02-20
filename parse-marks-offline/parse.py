import requests as r
import re
import json
from decimal import *
from bs4 import BeautifulSoup
from config import response_url, answer_key_url

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

# TODO: Command line arguments.
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
        # TODO: Probably wrong, because response sheet is already jumbled, so order needs to be decided with long_id
        if j <= 5:
            current_question['short_id'] = f'g{j}'
            current_question['marks'] = 1.0
        elif j <= 10:
            current_question['short_id'] = f'g{j}'
            current_question['marks'] = 2.0
        elif j <= 35:
            current_question['short_id'] = f'c{j-10}'
            current_question['marks'] = 1.0
        else:
            current_question['short_id'] = f'c{j-10}'
            current_question['marks'] = 2.0
        data = row.find_all('td')
        question_type = data[1].text
        question_id = data[3].text
        status = str(data[5].text)

        # in case of NAT questions, the answer's position is changed, so we have to ADAPT as well.
        if question_type == 'NAT':
            response_given = question_tables[i].find_all('td')[-1].text
        else:
            response_given = data[7].text
        # TODO: Don't know how the representation is, when a question is marked for review but not answered.
        current_question['type'] = question_type
        current_question['long_id'] = question_id
        current_question['status'] = status
        current_question['response_given'] = response_given
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
ares = parse_answer_key()

# merge required properties into one list into cres, in this case
for i, ans_row in enumerate(ares):
    for key in ans_row:
        if key == 'answer_key' or key == 'subject_id':
            cres[i][key] = ans_row[key]
            # TODO: No way to detect question-type mismatch (i.e. question is MCQ, but answer is NAT, mostly happens when answer-key is not in proper order)


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
for i, q in enumerate(cres):
    if q['status'] == 'Not Answered':
        cres[i]['obtained_marks'] = 0
        continue
    if q['type'] == 'MCQ':
        converted = str((ord(q['answer_key']) - ord('A')) + 1)
        cres[i]['obtained_marks'] = q['marks'] if q['response_given'] == converted else (
            (-0.33)*q['marks'])
    elif q['type'] == 'MSQ':
        all_ans = [str((ord(a) - ord('A')) + 1)
                   for a in q['answer_key'].split(';')]
        all_chosen = [str(a) for a in q['response_given'].split(',')]
        correct = True
        for ee in all_ans:
            if ee not in all_chosen:
                correct = False
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
            cres[i]['obtained_marks'] = q['marks'] if correct else 0.0

# here, cres hopefully contains all the required parameters

# print json to stdout so we get json by
# python3 parse.py > res.json
# TODO: maybe use file instead of stdout?
print(json.dumps(cres, indent=4))
