# Python SDK

The Python SDK to use the Thematic API is distributed with the following artifacts:

- thematic.py, an SDK for the API written in Python
- example, a simple example of how to use the api. This example uses a config file containing settings and parameters for the API

These files are helpful in understanding how to call the API and how to perform its different functions.
The following sections explain how to log in, how to process different types of surveys, how to tweak the Model, and finally how to perform incremental updates.

## Python version
The example and sdk are written for Python 3.

## Installing requirements
The thirdparty requirements are outlined in the file requirements.txt and can be installed using 
```
pip install -r requirements.txt
```

##  Initialising the SDK

Assuming that API base URL, username and password are stored in config.ini, use the following code to initialise the Thematic interface of the API:

```
thematic_instance = Thematic( server_url, username, password )
```

## Analysing Surveys

To analyse a Survey Instance, a new survey needs creating:

```
survey_name = "Customer Experience Survey"
total_columns = 5
columns = [[{"index": 2, "name": "NPS Comment"}]]
has_header = True

survey_info = thematic_instance.create_survey(survey_name,
                                total_columns,
                                columns,
                                has_header)
```

There is an optional parameter modelset_id. Use it to reference a Model Set from another survey instance, such as the first instance of a repeating survey.

The format that survey columns should be a list of lists of dictionaries. Details of each:
* outer list: this outer definition is just to contain all items
* each internal list: a group of columns that share common themes. Most surveys will only have one internal list
* each dictionary proper json format. The dictionaries should be of the form:
{ "index" : integer_column_index, "name" : "human readable name" }


The return object will contain survey id and modelset id. 

```
survey_id = survey_info["survey_id"]
modelset_id = survey_info["modelset_id"]
```

Once a survey id is known, the SDK allows to pass a path to a file containing survey results. While **run_job** method passes 
this file to the job creating stage, the next method, **wait_for_job_completion**, halts the program until the job is completed:

```
filename = 'input.csv'
job_id = thematic_instance.run_job( survey_id, filename )
thematic_instance.wait_for_job_completion( job_id )
```

The following snippet shows how to retrieve the results of a job, which completes the analysis and lets you save the content on disk for inspection: 

```
results = thematic_instance.retrieve_results( job_id )
if not results:
    raise Exception ("Failed to retrieve results")
base_filename, extension = os.path.splitext(os.path.basename(filename))
csv_filename = os.path.join("data_out/",base_filename+"_output.csv")
themes_filename = os.path.join("data_out/",base_filename+"_themes.json")
with open( csv_filename, "w" ) as f:
    f.write( results['csv'] )
with open( themes_filename, "w" ) as f:
    f.write( results['themes'] )
```

## Tweaking Analysis

To tweak the analysis by editing the concepts file, first retrieve the automatically generated concepts file, and save it on disk for inspection:

```
concepts = thematic_instance.retrieve_concepts( job_id )
concepts_out_filename = "data_out/concepts.json"
with open( concepts_out_filename, "w" ) as f:
    f.write( concepts )
```

After the concept file has been reviewed and, if necessary, updated, run a new job as follows:

```
concepts_out_filename = cfg.get('modelset', 'conceptsfile')
survey_id = cfg.get('modelset','survey_id')
previous_job = cfg.get('jobs','base_job')
job_id = thematic_instance.configure_concepts( survey_id, concepts_out_filename, previous_job )
thematic_instance.wait_for_job_completion( job_id )
```

Similarly, the SDK allows to retrieve the themes as follows: 

```
themes = thematic_instance.retrieve_themes( job_id ) )
if not themes:
    raise Exception ("Failed to retrieve themes")

themes_filename = os.path.join("data_out/",base_filename+"_themes.json")
with open( themes_filename, "w" ) as f:
    f.write( themes )
resulting_files.append( themes_filename )
```

After reviewing and modifying this file, a new Analysis using that file can be run as follows:

```
themes_out_filename = cfg.get('modelset', 'themesfile')
survey_id = cfg.get('modelset','survey_id')
previous_job = cfg.get('jobs','base_job')
job_id = thematic_instance.configure_themes( survey_id, themes_out_filename, previous_job )
thematic_instance.wait_for_job_completion( job_id )
```

Finally, as explained above, you can tweak the API Analysis parameters too. By using the SDK, first retrieve them as a dictionary.
 
```
# retrieve parameters
params = thematic_instance.retrieve_parameters( job_id ) )
if not params:
    raise Exception ("Failed to retrieve params")
```

After reviewing and modifying the values in the dictionary, a new Analysis using these values can be run as follows:

```
survey_id = cfg.get('modelset','survey_id')
previous_job = cfg.get('jobs','base_job')
job_id = thematic_instance.configure_parameters( survey_id, params, previous_job )
thematic_instance.wait_for_job_completion( job_id )
```

## Running incremental updates

Once you have created a survey, run the initial Analysis job and simply want to analyse an additional small number of responses, 
the SDK provides the **run_incremental_update** method:

```
filename = cfg.get('modelset', 'incremental_update_to_survey')
job_id = thematic_instance.run_incremental_update( survey_id, filename )
thematic_instance.wait_for_job_completion( job_id )

```
## Translating survey responses

In order to translate survey responses, simply use the **run_translation** method:

```
filename = cfg.get('modelset', 'foreign_survey')
job_id = thematic_instance.run_translations( survey_id, filename )
thematic_instance.wait_for_job_completion( job_id )
```

