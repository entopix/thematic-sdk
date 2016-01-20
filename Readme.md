# Getting Started 
Thematic API has been designed to analyse people's responses to open-ended questions in surveys. 
Thematic uses a combination of Natural Language Processing and Deep Learning algorithms 
to detect and group re-occurring themes and identify sentiment behind the comments.


## Definitions
-	Survey - A finite set of questions sent out to people.
-	Survey Instance - A finite set of responses to a Survey.
-	Analysis - Discovery of base and sub themes in a single Survey Instance and the application of those themes to each survey response.
-	Repeated Survey - Multiple Survey Instances for the same survey. The oposite of a repeated survey is a One-off Survey.
-	Continuous Survey - A Repeated Survey that is updated at least twice within two consecutive months.
-	Incremental Survey Update - A small number of responses added to a pre-existing Continuous Survey with a completed Analysis. Only application of the themes already identified in the completed Analysis to each survey response is performed (i.e. no new discovery for the added responses is performed).
-	Model - A collection of files created and used during the Analysis.


In this guide you will learn how to authenticate, how to process different types of surveys, how to tweak the Model, 
and finally how to perform incremental updates.

## Authentication

Almost all API endpoints use header based authentication and expect a header:
- X-API-Authentication : "{access key}"

To retrieve the access key, username and password can be used instead, by calling [/v1/login](#!/User/post_v1_login)

You can also just retrieve the key without logging in by calling [/v1/retrieve_key](#!/User/get_v1_retrieve_key).

## Analysis of surveys

Assuming you have a One-off survey in a new area, or you have the first instance of a survey that may be repeated, 
our goal is to perform the Analysis without any information about its content and themes known in advance. 

If you have a new instance of a Repeated Survey, this means that under your account you have a Model from a previously run first instance of that survey.
The only difference in processing is that you will reference that Model during the setup.

#### 1. Setting up a Survey Instance

To set up a Survey Instance, call [/v1/create_survey](#!/Surveys/post_v1_create_survey). 

You will need to provide information such as survey name, e.g. 'My survey', the total number of columns in the survey, 
the columns containing text, and whether or not the survey file contains a header.

For new instances of a Repeated Survey, in addition you will need to provide the id of the model set from the first instance of that Repeated survey.

The returned object from the call will contain a survey id assigned to this survey, as well as the id of the Model, called model set.

Note the modelset_id value, if you plan to process other new instances of this survey, or surveys that are in a similar area, but don't have enough data of their own. 


#### 2. Running Analysis of a Survey Instance

The Analysis of a Survey Instance is called a 'job'. To run the analysis, you can upload a CSV file containing the Survey Instance data,
 along providing the survey id (the result of setting up the survey), then wait for the job to be completed and finally retrieve the results.
 
To run the job, call [/v1/create_job](#!/Jobs/post_v1_create_job), which will return a job id.

By using that job id as a parameter, you can call the API again to check if the job has been completed:
After that, run [/v1/job/{job_uuid}/info](#!/Jobs/get_v1_job_job_uuid_info), and when the return object under **state** is **finished**, 
the results of the analysis can be saved.

You can also retrieve all your jobs and their states run under your account by calling [/v1/jobs](#!/Jobs/get_v1_jobs).

#### 3. Saving the results of the Analysis

The results of the Analysis consist of two types of files:

- **output.csv** - The original input Survey Instances with new columns attached with themes and sentiment scores;
- **themes.json** - The metadata file containing information about the extracted themes and the analysis.

You can retrieve them individually by using [/v1/job/{job_uuid}/csv](#!/Results/get_v1_job_job_uuid_csv) and [/v1/job/{job_uuid}/themes](#!/Results/get_v1_job_job_uuid_themes) calls.

### Tweaking the Analysis

There are different ways of tweaking the results of the Analysis:

- Reviewing and correcting some of the Model files;
- Changing the default parameters for different stages, such as thresholds.

Alternatively, one could also reference a Model created from a different Survey Instance, for example from one that was created using significantly more responses than the current Survey Instance. This has been explained above.

Thematic API has been designed in a way that whenever a Model file is updated and re-uploaded, the Analysis is immediately re-run to generate new results based on these updates.


#### 1. Reviewing and correcting Concepts

Concepts is one of the files in the automatically-generated Model, which can be retrieved for review and then re-used in the Analysis. 
It contains equivalent relations between words and phrases that are used by the algorithm to deduce phrases that mean equivalent themes. 
When performing the Analysis, Thematic API automatically generates a Concepts file. 
It can be retrieved using the get call [/v1/job/{job_uuid}/concepts](#!/Results/get_v1_job_job_uuid_concepts).

After reviewing and modifying this file, a new Analysis using that file can be run using the post call
[/v1/job/{job_uuid}/concepts](#!/Configuration/post_v1_job_job_uuid_concepts).


#### 1. Reviewing and correcting Themes

Themes generated during the Analysis can be modified in the following ways:

- You can remove a theme completely.
- You can change a title of an existing theme. Thematic automatically chooses the most frequent way a theme is referred to in text.
- You can change the automatically determined mappings of text phrases to themes by removing existing ones or adding new ones.
- You can modify the hierarchy of the themes tree:
  - if a theme has been merged into a base theme or a sub theme, you can unmerge and track this theme in your survey;
  - you can make a sub theme of a particular base theme into a base theme in its own right;
  - you can make a base theme into a sub theme of another base theme.

To do this in Thematic, simply retrieve the themes.json using the get call [/v1/job/{job_uuid}/themes](#!/Results/get_v1_job_job_uuid_themes), 
then modify it, and finally re-upload it using the post call [/v1/job/{job_uuid}/themes](#!/Configuration/post_v1_job_job_uuid_themes).


#### 3. Changing the default parameters of the Analysis

There is a number of default Analysis parameters that can be modified:

- COLUMNS specifies which columns contain responses that need to be Analysed and whether they need to be treated individually, or in groupings.
 For example, to analyse the responses from the first column in a CSV spreadsheet, simply use [[0]].
 Groupings are useful when you need extract separate sets of base themes from different columns. 
 For example, [[0], [1]] base themes from the first and the second columns individually, whereas [[0,1]] will extract a single set of base themes combining the responses in both of these columns.

- WORDS_TO_CONCEPTS_PARAMS specify similarity thresholds above which words of different grammatical categories can be considered to be equivalent. 
Select a value between 0.6 and 1.0 depending on the strength of your language model. These parameters will be used for the job type *concepts*.

- EXTRACT_THEMES_PARAMS - Parameters for the job type *extract*
  - MAX_NUM_BASE_THEMES specifies the number of base themes to generate during the Analysis. 
Select a value between 10 and 100, depending on how much variation you expect in responses.
Keep in mind that the most frequent base themes will cover the majority of respones.
  - MERGE_SIMILARITY specifies similarity threshold above which two themes can be merged into one.
Select a value between 0.7 and 0.9 depending on the strength of your language model.  
  - SUBTHEME_SIMILARITY specifies similarity threshold above which a less frequent theme becomes a sub theme of a more frequent base theme.
Select a value between 0.6 and 0.9 depending on the strength of your language model. Please note that this value should be higher than the MERGE_SIMILARITY

- APPLY_THEMES_PARAMS - Parameters for the job type *apply*
These parameters are useful for situation when none of the extracted themes can be found in a response. We use approximate matching to the most similar theme by using the language model.
  - ALLOW_ONE_THRESHOLD specifies the minimum similarity of the most similar base theme. Select a value between 0.7 and 0.95 depending on the strength of the model.
  - ALLOW_MULTIPLE_THRESHOLD specifies the minimum similarity of two or more similar base themes, if such can be found. Select a value between 0.75 and 0.95 depending on the strength of the model. 
 Please note that this value should be higher than the ALLOW_ONE_THRESHOLD.


To modify the default values of these parameters in Thematic, first retrieve the parameters using a get call
[/v1/job/{job_uuid}/params](#!/Configuration/get_v1_job_job_uuid_params), then modify them, and finally start a new Analysis by using a post call
[/v1/job/{job_uuid}/params](#!/Configuration/post_v1_job_job_uuid_params).


### Incremental Survey Update

A small number of responses may be added to an existing Survey Instance, for example survey responses collected in a particular day.
In this case there is not enough data to discover new themes, but you may want to which response contains which themes among the previously
discovered ones. This means, you need to run the job command [/v1/create_job](#!/Jobs/post_v1_create_job) 
and specify the job_type *apply*.


### Translation

Thematic also supports the analysis of surveys responses in languages other than English. This is useful in cases, when the same survey is
sent out to customers from different countries, but the person reviewing the results only speaks English.

Thematic integrates with Google API and a language detection library to provide a translation feature. This is designed as a job of type *translation*,
which you specify when running the job command [/v1/create_job](#!/Jobs/post_v1_create_job).
