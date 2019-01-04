from pyspark import SparkConf, SparkContext
from html.parser import HTMLParser
import sys
import boto3
import json
import os
import json
import spacy
from collections import defaultdict
from spacy.lemmatizer import Lemmatizer
from spacy.lang.en import LEMMA_INDEX, LEMMA_EXC, LEMMA_RULES
import re

BUCKET_NAME = 'cse6242-t2-raw'
OBJECT_PREFIX = 'v2'

STATES_BY_ABREV = {'AK': 'Alaska', 'AL': 'Alabama', 'AR': 'Arkansas', 'AS': 'American Samoa', 'AZ': 'Arizona', 'CA': 'California', 'CO': 'Colorado', 'CT': 'Connecticut', 'DC': 'District of Columbia', 'DE': 'Delaware', 'FL': 'Florida', 'GA': 'Georgia', 'GU': 'Guam', 'HI': 'Hawaii', 'IA': 'Iowa', 'ID': 'Idaho', 'IL': 'Illinois', 'IN': 'Indiana', 'KS': 'Kansas', 'KY': 'Kentucky', 'LA': 'Louisiana', 'MA': 'Massachusetts', 'MD': 'Maryland', 'ME': 'Maine', 'MI': 'Michigan', 'MN': 'Minnesota', 'MO': 'Missouri', 'MP': 'Northern Mariana Islands',
                   'MS': 'Mississippi', 'MT': 'Montana', 'NA': 'National', 'NC': 'North Carolina', 'ND': 'North Dakota', 'NE': 'Nebraska', 'NH': 'New Hampshire', 'NJ': 'New Jersey', 'NM': 'New Mexico', 'NV': 'Nevada', 'NY': 'New York', 'OH': 'Ohio', 'OK': 'Oklahoma', 'OR': 'Oregon', 'PA': 'Pennsylvania', 'PR': 'Puerto Rico', 'RI': 'Rhode Island', 'SC': 'South Carolina', 'SD': 'South Dakota', 'TN': 'Tennessee', 'TX': 'Texas', 'UT': 'Utah', 'VA': 'Virginia', 'VI': 'Virgin Islands', 'VT': 'Vermont', 'WA': 'Washington', 'WI': 'Wisconsin', 'WV': 'West Virginia', 'WY': 'Wyoming'}
STATES_BY_NAME = {v.lower(): k for k, v in STATES_BY_ABREV.items()}

nlp_lem = spacy.load('en_core_web_sm')


def lemmatize(entity_text):
    doc_lem = nlp_lem(entity_text)

    return ' '.join([ent_lem.lemma_ for ent_lem in doc_lem])


def get_entities(text):
    text = preprocess_text(text)

    entities = defaultdict(list)

    nlp_skill = spacy.load('/tmp/job_skill')
    nlp_experience = spacy.load('/tmp/job_experience')
    nlp_degree = spacy.load('/tmp/job_degree')

    ######################################
    # Extract Skills
    ######################################

    skill_doc = nlp_skill(text)

    entities['SKILL'] = list(set([lemmatize(ent.text)
                                  for ent in skill_doc.ents if ent.label_ == "SKILL"]))

    ######################################
    # Extract Degree
    ######################################

    degree_options = {'b': 1, 'm': 2, 'p': 3}
    degree_doc = nlp_degree(text)

    degrees = []

    for ent in degree_doc.ents:
        if ent.label_ != 'DEGREE':
            # Skip the label if it is one of the pretrained
            continue

        # Take the indicies for the first letters of masters, bachelors, phd.
        # Bachelors and masters of different types usually start with an m or b no matter what follows.
        bachelor = ent.text.lower().find('b')
        master = ent.text.lower().find('m')
        phd = ent.text.lower().find('p')

        # Make sure to only use the ones that were found (without -1)
        indexes = [index for index in [bachelor, master, phd] if index >= 0]

        if len(indexes) == 0:
            continue

        # Append the type of degree for the smallest index/first occurence
        degrees.append(degree_options[ent.text.lower()[min(indexes)]])

    if len(degrees) == 0:
        # Append 0 to the degrees if there are no degrees
        degrees.append(0)

    # Get the minimum degree required out of all the degrees mentioned in the job posting
    entities['DEGREE'] = min(degrees)

    ######################################
    # Extract Experience
    ######################################

    degree_doc = nlp_experience(text)

    experiences = []
    for ent in degree_doc.ents:
        if ent.label_ != 'EXPERIENCE':
            # Skip the label if it is one of the pretrained
            continue

        experiences.append(extract_years(ent.text))

    if len(experiences) == 0:
        # Append 0 to the experiences if there are no experiences
        experiences.append(0)

    entities['EXPERIENCE'] = min(experiences)

    return dict(entities)


class MLStripper(HTMLParser):
    def __init__(self):
        self.reset()
        self.strict = False
        self.convert_charrefs = True
        self.fed = []

    def handle_data(self, d):
        self.fed.append(d)

    def get_data(self):
        return ''.join(self.fed)


def strip_tags(html):
    s = MLStripper()
    s.feed(html)
    return s.get_data()


def preprocess_text(text):
    # Strip all HTML tags
    text = strip_tags(text)

    # Drop all non-ascii characters
    return ''.join([i if ord(i) < 128 else ' ' for i in text]).replace("\n", " ")


def text2int(textnum):
    textnum = textnum.lower()

    numwords = [
        "zero", "one", "two", "three", "four", "five", "six", "seven", "eight",
        "nine", "ten", "eleven", "twelve", "thirteen", "fourteen", "fifteen",
        "sixteen", "seventeen", "eighteen", "nineteen",
    ]
    # Partial matching in the dictionary of words
    indices = [i for i, s in enumerate(numwords) if s in textnum]
    if indices:
        # Find the index of the word in the dictionary
        result = indices[0]
        result = int(result)
    else:
        # Return str if not found in the dictionary of words
        result = "not found"
    return result


def extract_years(text_string):
    experience = 0

    try:
        # Call function to extract number
        number_from_text = text2int(text_string)
        number_from_text = int(number_from_text)
        #number_from_text = int(number_from_text)
        flag = 1
    except:
        # In case no number could be extracted
        flag = 0
    # If number exists in pattern as digit
    if re.search(r'\d+', text_string):
        match = re.findall(r'\d+', text_string)
        match = float(min(match))
        # If number exists in pattern as word and digit
        if flag == 1:
            experience = min(match, number_from_text)
        # If number exists in pattern as word digit only
        else:
            experience = match
    # If digit does not exist in NER
    else:
        if flag == 1:
            experience = number_from_text
        else:
            experience = 0

    if text_string.lower().find('month') != -1:
        # Divide the years by twelve if the number is supposed to be a month
        # If we don't do this we will treat months as years which would be a fail
        return experience / 12
    else:
        return experience


def fetch_data(s3key):
    """
    Fetch data with the given s3 key and pass along the contents as a dictionary.

    :param s3key: An s3 key path string.
    :return: A list of dictionaries with jobs per jsonl file
    """
    s3 = boto3.resource('s3')
    obj = s3.Object(BUCKET_NAME, s3key)
    contents = obj.get()['Body'].read().decode('utf-8')

    return [json.loads(line) for line in contents.split('\n') if line != '']


def process_data(record):
    if 'job_description' not in record.keys():
        return None

    entities = get_entities(record['job_description'])

    # Remove job description because we don't need it in our final dataset
    del record['job_description']

    # Instead, add the extracted entities
    record['entities'] = entities

    # Add id for mongodb
    record['__id'] = record['job_id']

    # Remove ambiguous job id
    del record['job_id']

    # Handle the state abreviations and names
    if len(str(record['state'])) > 2:
        # Full name of state
        if str(record['state']).upper() in STATES_BY_NAME.keys():
            record['state_abrev'] = STATES_BY_NAME[record['state']].upper()
            record['state'] = record['state'].title()
        else:
            record['state'] = None
            record['state_abrev'] = None
    else:
        # Abreviation
        if str(record['state']).upper() in STATES_BY_ABREV.keys():
            record['state_abrev'] = record['state'].upper()
            record['state'] = STATES_BY_ABREV[record['state'].upper()].title()
        else:
            record['state'] = None
            record['state_abrev'] = None

    return json.dumps(record)


def main():
    s3 = boto3.resource('s3')
    b = s3.Bucket(BUCKET_NAME)

    # Remove the directory in case the task fails the first time.
    # This is important since it turns out that tasks fail regularly.
    # The temporary files created by the failed task will then cause the
    # next task to fail. Therefore we just remove the whole folder each time
    b.objects.filter(Prefix="spark-processed").delete()

    objs = b.objects.filter(Prefix=OBJECT_PREFIX)
    key_list = [obj.key for obj in objs]

    sc = SparkContext.getOrCreate()

    lines = [item for sublist in map(fetch_data, key_list) for item in sublist]

    # Create an RDD from the list of s3 key names to process stored in key_list
    lineRDD = sc.parallelize(lines)
    result = lineRDD.map(process_data)

    # Store a single file in the output bucket that can be imported with mongoimport later.
    result.repartition(1).saveAsTextFile(
        "s3a://{0}/spark-processed".format(BUCKET_NAME))
    sc.stop()


if __name__ == '__main__':
    main()
