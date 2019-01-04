-- Create the jobs table from raw data

CREATE external TABLE raw_jobs (
    `extractedAttributes` struct<employmentType:string,experience:string,experienceLevel:array<string>>,
    `gaTrackerData` struct<industry:string,industryId:string,empSize:string,jobTitle:string,jobId:string,sector:string,sectorId:string, locationType:string, locationid:string>,
    `header` struct<applyUrl:string,employerName:string,employerId:string, posted:string, rating:string, salaryHigh:string, salaryLow:string, salarySource:string>,
    `job` struct<description:string,discoverDate:string,listingId:string>,
    `map` struct<country:string,employerName:string,lat:double,lng:double,location:string>,
    `rating` struct<ceoApproval:string,recommendToFriend:string,starRating:string>
)
ROW FORMAT SERDE 'org.openx.data.jsonserde.JsonSerDe'
LOCATION 's3://cse6242-t2-raw/v1/';

-- Create a flattened table in Parquet format

CREATE TABLE IF NOT EXISTS jobs
  WITH (format='PARQUET', external_location='s3://cse6242-t2-raw/preprocessed/') AS
SELECT
CAST(job.listingId AS BIGINT) as listing_id,
CAST(From_iso8601_timestamp(job.discoverDate) as timestamp) as discover_date,
header.posted as posted,
header.applyUrl as apply_url,
CAST(gaTrackerData.jobId AS BIGINT) as job_id,
gaTrackerData.jobTitle as job_title,
job.description as job_description,
extractedAttributes.employmentType as employment_type,
extractedAttributes.experience as experience,
extractedAttributes.experienceLevel as experience_level,
gaTrackerData.sector as sector,
CAST(gaTrackerData.sectorId AS integer) as sector_id,
gaTrackerData.industry as industry,
CAST(gaTrackerData.industryId AS integer) as industry_id,
CAST(header.employerId as integer) as employer_id,
header.employerName as employer_name,
gaTrackerData.locationType as location_type,
map.location as location,
CAST(gaTrackerData.locationId AS integer) as location_id,
map.country as location_country,
CAST(map.lat AS Decimal(9,6)) as location_latitude,
CAST(map.lng AS Decimal(9,6)) as location_longitude,
CAST(rating.ceoApproval AS DECIMAL(3,2)) as ceo_approval,
CAST(rating.recommendToFriend AS DECIMAL(3,2)) as recommend_to_friend,
CAST(rating.starRating AS DECIMAL(2,1)) as star_rating,
CAST(header.salaryHigh AS integer) as salary_high,
CAST(header.salaryLow AS integer) as salary_low,
header.salarySource as salary_source
FROM raw_jobs ORDER BY listing_id

-- Get a reduced subset of tech jobs

SELECT *
FROM (SELECT job_id, sector, job_title, apply_url, employer_name,
         location,
         location_country,
         regexp_extract(lower(location),
         ',\s*([^\s]{2}|labama|alaska|arizona|arkansas|california|colorado|connecticut|delaware|florida|georgia|hawaii|idaho|illinois|indiana|iowa|kansas|kentucky|louisiana|maine|maryland|massachusetts|michigan|minnesota|mississippi|missouri|montana|nebraska|nevada|new hampshire|new jersey|new mexico|new york|north carolina|north dakota|ohio|oklahoma|oregon|pennsylvania|rhode island|south carolina|south dakota|tennessee|texas|utah|vermont|virginia|washington|west virginia|wisconsin|wyoming)$', 1) AS state, CAST(job_description AS JSON) AS job_description
    FROM
    (SELECT job_description, MAX(job_id) as job_id, MAX(apply_url) as apply_url, MAX(employer_name) as employer_name, MAX(sector) AS sector, MAX(job_title) AS job_title, MAX(location) AS location, MAX(location_country) AS location_country
    FROM jobs_v1
    WHERE  LOWER(job_title) LIKE '%data sci%'
            OR LOWER(job_title) LIKE '%data ana%'
            OR LOWER(job_title) LIKE '%data eng%'
            OR LOWER(job_title) LIKE '%softw%'
            OR LOWER(job_title) LIKE '%comp%'
            OR LOWER(job_title) LIKE '%databa %'
            OR LOWER(job_title) LIKE '%analy%'
    GROUP BY job_description) as techjobs
    WHERE (regexp_like(location, ',\s*[^\s]{2}$')
            OR regexp_like(lower(location), ',\s*(alabama|alaska|arizona|arkansas|california|colorado|connecticut|delaware|florida|georgia|hawaii|idaho|illinois|indiana|iowa|kansas|kentucky|louisiana|maine|maryland|massachusetts|michigan|minnesota|mississippi|missouri|montana|nebraska|nevada|new hampshire|new jersey|new mexico|new york|north carolina|north dakota|ohio|oklahoma|oregon|pennsylvania|rhode island|south carolina|south dakota|tennessee|texas|utah|vermont|virginia|washington|west virginia|wisconsin|wyoming)'))
            AND (lower(location_country) IN('united states of america', 'us', 'u.s', 'united states', 'usa')
            OR location_country IS NULL)) AS jobsstates;
