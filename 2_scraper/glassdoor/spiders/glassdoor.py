import scrapy
import json

class GlassdoorSpider(scrapy.Spider):
    name = 'glassdoor'
    allowed_domains = ['glassdoor.com']
    start_urls = ['http://www.glassdoor.com/']

    # Current file number
    file_number = 1

    # Number of responses in the current batch
    batch_count = 0

    # Newest job id manually fetched from Glassdoor
    last_job_id = 3007872968

    # Fetch two million jobs
    num_of_jobs = 2000000

    # Batch size
    batch_size = 5000

    def parse_detail(self, response):
        if response.status == 200:
            self.batch_count += 1

            if self.batch_count == self.batch_size:
                self.file_number += 1
                self.batch_count = 0

            with open('./output/output_%s.jsonl' % self.file_number, 'a') as f:
                f.write(response.text + '\n')

    def parse(self, response):
        # Loop trough the range of ids and fetch the document from the glassdoor site
        for id in range(self.num_of_jobs):
            yield response.follow('https://www.glassdoor.com/Job/json/details.htm?jobListingId=' + str(self.last_job_id - id), self.parse_detail)
