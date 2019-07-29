# Getting Started Guide

Thematic API has been designed to analyse people's responses to open-ended questions in surveys. 
Thematic uses a combination of Natural Language Processing and Deep Learning algorithms 
to detect and group re-occurring themes and identify sentiment behind the responses.

## Definitions
-   Survey - A finite set of questions sent out to people.
-   Survey Instance - A finite set of responses to a Survey.
-   Analysis - Discovery of base and sub themes in a single Survey Instance and the application of those themes to each survey response.
-   Repeated Survey - Multiple Survey Instances for the same survey. The oposite of a repeated survey is a One-off Survey.
-   Continuous Survey - A Repeated Survey that is updated at least twice within two consecutive months.
-   Incremental Survey Update - A small number of responses added to a pre-existing Continuous Survey with a completed Analysis. Only application of the themes already identified in the completed Analysis to each survey response is performed (i.e. no new discovery for the added responses is performed).
-   Model - A collection of files created and used during the Analysis.

## Getting ready to start using the API

**First**, make sure you have access to the Thematic API endpoint [https://processor.us.getthematic.com/v1/](https://processor.us.getthematic.com/v1/).

**Second**, make sure you have a username and a password. Contact **support@entopix.com** if you don't have yours.

**Third**, make sure you can authenticate correctly. Almost all API endpoints use header based authentication and expect a header:

- X-API-Authentication : "{access key}"

To retrieve the access key, login to the API using your username and password: [/v1/login](http://themes-docs.entopix.com/#!/User/post_v1_login). The api key will be returned as a json response to this call

## Analysis of surveys

To analyse people’s responses to open-ended questions in a survey, the following three steps need to happen first:

#### 1. Create a Survey

If you have a One-off survey in a new area, or the first instance of a Repeated Survey, setup a new Survey Instance by calling [/v1/create_survey](http://themes-docs.entopix.com/#!/Surveys/post_v1_create_survey). You will need to specify:

- survey name, e.g. 'My survey', 
- the total number of columns in the survey,
- the columns that contain the responses to open-ended questions,
- whether or not the survey file contains a header. 

The returned object will contain a **survey id** assigned to this survey, as well as the id of the Model, called **modelset id**, which should be stored for the use in other calls. This will perform the Analysis without any information about its content and themes known in advance. 

If you have a new instance of a Repeated Survey, under your account you will have a Model from a previously run first instance of that survey.
The only difference in processing is that you will reference the corresponding **modelset id** during the setup.

**Only run this call once, otherwise duplicate surveys will be created.**

You can also retrieve all surveys created under your account by calling [/v1/surveys](http://themes-docs.entopix.com/#!/Surveys/get_v1_surveys).

#### 2. Run Analysis Job

The Analysis of a Survey Instance is called a 'job'. This is where you upload your dataset: a CSV file in UTF-8 encoding containing survey responses.
You will need to provide the survey id (the result of creating a survey), then wait for the job to be completed and finally retrieve the results.
 
To run the job, call [/v1/create_job](http://themes-docs.entopix.com/#!/Jobs/post_v1_create_job), which will return a job id. Store it for use in other calls.

All stages of the analysis will be run, i.e. **job_type** *full*. A job is considered complete when its **state** changes to *finished*. Supply your job id to [/v1/job/{job_uuid}/info](http://themes-docs.entopix.com/#!/Jobs/get_v1_job_job_uuid_info) to check if the job has been completed. If yes, 
the results of the analysis can be saved.

**Only run this call once for a dataset, otherwise duplicate jobs will be created.**

You can also retrieve all your jobs and their states run under your account by calling [/v1/jobs](http://themes-docs.entopix.com/#!/Jobs/get_v1_jobs).

#### 3. Download and Save Results

Once a job is completed, the results of the analysis can be downloaded. The main results of the Analysis consist of two files: a CSV file with themed responses, which can be retrieved using [/v1/job/{job_uuid}/csv](http://themes-docs.entopix.com/#!/Results/get_v1_job_job_uuid_csv) call, and a JSON file with the metadata about the themes, which can be retrieved using [/v1/job/{job_uuid}/themes](http://themes-docs.entopix.com/#!/Results/get_v1_job_job_uuid_themes) call.

- **output.csv** - The original input CSV with new columns attached to each non-empty respones. Each theme is represented by its unique id.
    - base themes - one or more generic themes, where *nothing* stands for a meaningless response and *other* is applied to all comments that don't match other themes 
    - sub themes - one or more themes which correspond to the more specific versions of the base themes (where possible)
    - sentiment score - a number indicating whether response contained a positive (+1) or a negative (-1) sentiment
- **themes.json** - The metadata file containing information about the extracted themes and the analysis:
    - **titles** - title automatically selected for each theme (unique id -> title)
    - **map** - phrases that were used to map to theme (phrase -> unique id)
    - **themes{N}** - information about themes extracted for each column grouping, where N is the id of that grouping:
        - whether or not a theme was merged into another theme (if *merged* is present)
        - which sub themes a theme contains (if *sub_themes* is present, empty or not, it indicates that this theme is a base theme)
        - number of comments with that theme (*freq*)

## Other types of jobs

Thematic API supports two further types of Analysis:

#### Incremental Survey Update

A small number of responses may be added to an existing Survey Instance, for example survey responses collected in a particular day.
In this case there is not enough data to discover new themes, but you may want to know which response contains which previously
discovered themes. Call the [/v1/create_job](http://themes-docs.entopix.com/#!/Jobs/post_v1_create_job) endpoint and specify the **job_type** *apply*.


#### Translation

Thematic also supports the analysis of surveys responses in languages other than English. This is useful in cases, when the same survey is
sent out to customers from different countries, but the person reviewing the results only speaks English.

Thematic integrates with the Google API and a language detection library to provide a translation feature. To translate the responses before running the analysis, call first the [/v1/create_job](http://themes-docs.entopix.com/#!/Jobs/post_v1_create_job) endpoint and specify the **job_type** *translate*.
