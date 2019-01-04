import sys

# Make sure we are able to load the local modules
sys.path.append('./modules')

import json
import base64
import spacy
import PyPDF2
import base64
import io
from pymongo import MongoClient
import os
import re
from collections import defaultdict
from dateutil.parser import parse
from datetime import datetime

def lambda_handler(event, context):
    """Lambda handler processing the requests comming from API Gateway

    Arguments:
        event {dict} -- Event triggering the Lambda function
        context {dict} -- Context of the event

    Returns:
        dict -- JSON serializable respone for the frontend
    """

    client = MongoClient('mongodb://ec2-18-206-172-103.compute-1.amazonaws.com:27017', username='mongo', password='crippledmonkey', authSource='admin', connect=False)

    db = client.cse6242

    if event['context']['resource-path'] == '/stats':

        skill = event['params']['querystring']['skill'].lower()

        # Lemmatize the skill in order to be able to comapare it with the already lemmatized skills in the db
        nlp_lem = spacy.load(os.path.dirname(os.path.abspath(__file__)) + '/models/en_core_web_sm')
        skill =  " ".join(word.lemma_ for word in nlp_lem(skill))

        # Top companies

        pipeline = [
            {"$match": { "$expr": { "$in": [ skill, "$entities.SKILL" ] }}},
            {"$group": {"_id": "$employer_name", "value": {"$sum": 1}}},
            {"$project": { "name": "$_id", "value": 1, "_id": 0}},
            {"$sort": {"value": -1}},
            {"$limit": 10}
        ]

        companies = list(db.jobs.aggregate(pipeline))


        # Top Industries

        pipeline = [
            {"$match": { "$expr": { "$in": [ skill, "$entities.SKILL" ] }}},
            {"$group": {"_id": "$sector", "value": {"$sum": 1}}},
            {"$project": { "name": "$_id", "value": 1, "_id": 0}},
            {"$sort": {"value": -1}},
            {"$limit": 10}
        ]

        sectors = list(db.jobs.aggregate(pipeline))

        # States

        pipeline = [
            {"$match": { "$expr": { "$in": [ skill, "$entities.SKILL" ] }}},
            {"$group": {"_id": {"state_abrev": "$state_abrev", "state": "$state"}, "count": {"$sum": 1}}},
            {"$project": { "_id": 0, "state_abrev": "$_id.state_abrev", "state": "$_id.state", "count": 1}},
            {"$sort": {"count": -1}}
        ]

        states = list(db.jobs.aggregate(pipeline))

        # Bubbles

        pipeline = [
            {"$match": { "$expr": { "$in": [ skill, "$entities.SKILL" ] }}},
            { "$group": { "_id" : {"sector" : "$sector", "employer_name" : "$employer_name"}, "total" : { "$sum" : 1}}},
            { "$match" : {"total" : { "$gt" : 10 }}}
        ]

        bubbles = list(db.jobs.aggregate(pipeline))

        sector_index = defaultdict(list)
        max_count = 0
        min_count = 0

        for bubble in bubbles:
            sector_index[bubble['_id']['sector']].append({
                "name": bubble['_id']['employer_name'],
                "size": bubble['total']
            })

            if bubble['total'] > max_count:
                max_count = bubble['total']

            if bubble['total'] < min_count:
                min_count = bubble['total']

        bubbles = [{"name": sector_name, "children": sector}  for sector_name, sector in sector_index.items()]

        return {
            "companies": companies,
            "sectors": sectors,
            "states": states,
            "bubbles": {"name": "Job Market", "min": min_count, "max": max_count, "children": bubbles}
        }


    elif event['context']['resource-path'] == '/submit-resume':
        # Handle the resume upload and return the data necessary to display the initial two graphs.
        # This includes aggregated data for the two graphs shown on the second page.

        boundary = re.search(r'boundary=([^\s]+)', event['params']['header']['content-type'], re.IGNORECASE).group(1)

        # Split by the provied boundary in the content-type header
        # This removes the boundary from the binary multipart/form-data payload
        binary_base= base64.b64decode(event['body'])
        end_result = find_between(binary_base, boundary.encode('utf-8'), (boundary + '--').encode('utf-8'))
        end_result = b'\r\n'.join(end_result.split(b'\r\n')[4:])

        # Convert to io Byte Stream in order to feed it to PyPDF
        end_result_iostream = io.BytesIO(end_result)

        # Extract the test from the pdf and clean it up
        pdf_text = pdf_to_text(end_result_iostream)

        # Load the spacy model and extract the entities from the pdf
        nlp = spacy.load(os.path.dirname(os.path.abspath(__file__)) + '/models/model')
        nlp_degree = spacy.load(os.path.dirname(os.path.abspath(__file__)) + '/models/degree_model')
        nlp_lem = spacy.load(os.path.dirname(os.path.abspath(__file__)) + '/models/en_core_web_sm')

        doc = nlp(pdf_text)

        ######################################
        # Extract Skills
        ######################################

        skills = []

        for ent in doc.ents:
            if ent.label_ == "SKILL":
                doc_lem = nlp_lem(ent.text)
                words_lematization = []

                for ent_lem in doc_lem:
                    words_lematization.append(ent_lem.lemma_)

                words_lematization = " ".join(words_lematization)

                skills.append(words_lematization)

        skills = list(set(skills))

        ######################################
        # Extract Degree
        ######################################

        degree_options = {'b': 1, 'm': 2, 'p': 3}
        degree_doc = nlp_degree(pdf_text)

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
        degree = max(degrees)

        ######################################
        # Extract Experience
        ######################################

        experiences = []
        for ent in doc.ents:
            if ent.label_ != 'EXPERIENCE':
                # Skip the label if it is one of the pretrained
                continue

            experiences.append(spacy_datetime(ent.text))

        if len(experiences) == 0:
            # Append 0 to the experiences if there are no experiences
            experiences.append(0)

        experience = sum(experiences)

        fallback = 0.2
        weights = [0.5,0.3,0.2]
        pipeline = [
            { "$project": { "job_id": 1, "job_title": 1, "employer_name": 1, "location": 1, "apply_url": 1, "state_abrev": 1, "state": 1, "skill_union": { "$setUnion": [skills, "$entities.SKILL"] }, "skill_inter": { "$setIntersection": [skills, "$entities.SKILL"] }, "_id": 0 } },
            { "$project": { "job_id": 1, "job_title": 1, "employer_name": 1, "location": 1, "apply_url": 1, "state_abrev": 1, "state": 1, "skill_union": 1, "skill_inter": 1, "skill_union_size": { "$size": "$skill_union" }, "skill_inter_size": { "$size": "$skill_inter" }, "_id": 0 } },
            { "$match" : { "skill_inter_size" : { "$gt": 0 }}},
            { "$project": { "job_id": 1, "job_title": 1, "employer_name": 1, "location": 1, "apply_url": 1, "state_abrev": 1, "state": 1, "jaccard": { "$divide": ["$skill_inter_size", "$skill_union_size"] }, "degree_fraction": { "$abs": { "$subtract": [ degree, "$entities.DEGREE" ] } }, "_id": 0 } },
            { "$project": { "job_id": 1, "job_title": 1, "employer_name": 1, "location": 1, "apply_url": 1, "state_abrev": 1, "state": 1, "jaccard": 1, "degree_dist_divide": { "$divide": ["$degree_fraction", 3] }, "_id": 0 }},
            { "$project": { "job_id": 1, "job_title": 1, "employer_name": 1, "location": 1, "apply_url": 1, "state_abrev": 1, "state": 1, "jaccard": 1, "degree_dist_flagged": { "$subtract": [1, "$degree_dist_divide"]}, "_id": 0 }},
            { "$project": { "job_id": 1, "job_title": 1, "employer_name": 1, "location": 1, "apply_url": 1, "state_abrev": 1, "state": 1, "jaccard": 1, "degree_dist_flagged_2": { "$cond": { "if": { "$gt": ["$entities.DEGREE" , 0 ] }, "then": "$degree_dist_flagged", "else": fallback }}, "_id": 0 }},
            { "$project": { "job_id": 1, "job_title": 1, "employer_name": 1, "location": 1, "apply_url": 1, "state_abrev": 1, "state": 1, "jaccard": 1, "degree_dist": { "$cond": { "if": { "$gt": [degree , 0 ] }, "then": "$degree_dist_flagged_2", "else": 0 }}, "_id": 0 }},
            { "$project": { "job_id": 1, "job_title": 1, "employer_name": 1, "location": 1, "apply_url": 1, "state_abrev": 1, "state": 1, "jaccard": 1, "degree_dist": 1, "experience_fraction": { "$abs": {"$subtract": [ experience, "$entities.EXPERIENCE" ] }} , "_id": 0  }},
            { "$project": { "job_id": 1, "job_title": 1, "employer_name": 1, "location": 1, "apply_url": 1, "state_abrev": 1, "state": 1, "jaccard": 1, "degree_dist": 1, "experience_fraction_max": { "$max": ["$experience_fraction",10] }, "_id": 0 }},
            { "$project": { "job_id": 1, "job_title": 1, "employer_name": 1, "location": 1, "apply_url": 1, "state_abrev": 1, "state": 1, "jaccard": 1, "degree_dist": 1, "experience_flagged_divide": { "$divide": ["$experience_fraction_max", 10] }, "_id": 0 }},
            { "$project": { "job_id": 1, "job_title": 1, "employer_name": 1, "location": 1, "apply_url": 1, "state_abrev": 1, "state": 1, "jaccard": 1, "degree_dist": 1, "experience_flagged": { "$subtract": [1, "$experience_flagged_divide"]}, "_id": 0 }},
            { "$project": { "job_id": 1, "job_title": 1, "employer_name": 1, "location": 1, "apply_url": 1, "state_abrev": 1, "state": 1, "jaccard": 1, "degree_dist": 1, "experience_resume_check": { "$cond": { "if": { "$gt": [ experience, 0 ] }, "then": "experience_flagged", "else": fallback }}, "_id": 0 }},
            { "$project": { "job_id": 1, "job_title": 1, "employer_name": 1, "location": 1, "apply_url": 1, "state_abrev": 1, "state": 1, "jaccard": 1, "degree_dist": 1, "experience_dist": { "$cond": { "if": { "$gt": ["$entities.EXPERIENCE" , 0 ] }, "then": "experience_resume_check", "else": fallback }}, "_id": 0 }},
            { "$project": { "job_id": 1, "job_title": 1, "employer_name": 1, "location": 1, "apply_url": 1, "state_abrev": 1, "state": 1, "w_skill": { "$multiply": [weights[0], '$jaccard'] },  "w_degree": { "$multiply": [weights[1], '$degree_dist'] }, "w_experience": { "$multiply": [weights[2], '$experience_dist'] }  }},
            { "$project": { "job_id": 1, "job_title": 1, "employer_name": 1, "location": 1, "apply_url": 1, "state_abrev": 1, "state": 1, "score": { "$add": ["$w_skill", "$w_experience", "$w_degree"] } }},
            { "$sort" : { "score" : -1 }},
            { "$group": {"_id": {"state_abrev": "$state_abrev", "state": "$state"}, "count": {"$sum": 1}, 'jobs': { '$push': '$$ROOT' }, "state": { "$first": "$state" }}},
            { "$project": {"_id": 0, "state_abrev": "$_id.state_abrev", "state": "$_id.state", "count": 1, "job_id": 1, "job_title": 1, "apply_url": 1, "employer_name": 1, "location": 1, 'jobs': { '$slice': ['$jobs', 10]}}}
        ]

        states = list(db.jobs.aggregate(pipeline))

        return {
            "skills": skills,
            "experience": experience,
            "degree": degree,
            "states": states
        }

def find_between(s, first, last):
    """Find text between two strings

    Arguments:
        s {string} -- String to search in
        first {string} -- First string
        last {string} -- Last string

    Returns:
        string -- Result
    """

    try:
        start = s.index( first ) + len( first )
        end = s.index( last, start )
        return s[start:end]
    except ValueError:
        return ""

def pdf_to_text(pdfFileObj):
    """Extracts the text from a pdf file

    Arguments:
        pdfFileObj {file} -- PDF file

    Returns:
        string -- Extracted text
    """

    text= ''

    pdfReader= PyPDF2.PdfFileReader(pdfFileObj)

    for page in range(pdfReader.numPages):
        pageObj= pdfReader.getPage(page)
        text += pageObj.extractText()

    return ''.join([i if ord(i) < 128 else ' ' for i in text])

def spacy_datetime(input_from_spacy):
    """Splits the input string into two dates, parses them and calculates their difference in years

    Arguments:
        input_from_spacy {string} -- Extracted text

    Returns:
        float -- Years
    """

    input_from_spacy = re.sub("present",str(datetime.today().year),input_from_spacy,flags=re.IGNORECASE)
    input_from_spacy = re.sub("today",str(datetime.today().year),input_from_spacy,flags=re.IGNORECASE)
    dates_in_datetime = []

    if len(input_from_spacy.split("-")) == 2:
        separator = "-"
    elif len(input_from_spacy.split(" to")) == 2:
        separator = " to"
    else:
        return 0

    for index,items in enumerate(input_from_spacy.split(separator)):
        #Check if there is only Month and not year in the first split
        if((index==0) and (len(re.findall(r'\w+', items))))==1:
            #Year from second date in case first is missing
            try:
                try:
                    year = parse(input_from_spacy.split(separator)[1], fuzzy=True).year
                    dates_in_datetime.append(parse(str(items)+str(year), fuzzy=True))
                except ValueError:
                    dates_in_datetime.append(datetime.today())
            except OverflowError:
                dates_in_datetime.append(datetime.today())
        else:
            try:
                try:
                    dates_in_datetime.append(parse(items, fuzzy=True))
                except ValueError:
                    dates_in_datetime.append(datetime.today())
            except OverflowError:
                dates_in_datetime.append(datetime.today())

    return ((dates_in_datetime[1]-dates_in_datetime[0]).days)/365
