
import sys
import json
import ConfigParser

sys.path.append('..')
from thematic.thematic import Thematic



def main():
    cfg = ConfigParser.ConfigParser()
    cfg.read('config.ini')

    # Login to the thematic service
    server_url = cfg.get('server', 'base_url')
    username = cfg.get('server', 'username')
    password = cfg.get('server', 'password')
    thematic_instance = Thematic( server_url, username, password )

    # Create a survey
    survey_name = cfg.get('survey', 'name')
    total_columns = cfg.get('survey', 'total_columns')
    columns = json.loads(cfg.get('survey', 'columns')) 
    has_header = cfg.get('survey', 'has_header')

    survey_info = thematic_instance.create_survey(survey_name,
                                    total_columns,
                                    columns,
                                    has_header)

    survey_id = survey_info["survey_id"]
    modelset_id = survey_info["modelset_id"]

    # Begin the survey job running
    filename = cfg.get('input', 'filename')
    job_id = thematic_instance.run_job( survey_id, filename )

    # Wait for the survey to finish
    thematic_instance.wait_for_job_completion( job_id )

    # Download the results
    results = thematic_instance.retrieve_results( job_id )
    if not results:
        raise Exception ("Failed to retrieve results")

    # Save the results to disk
    base_filename, extension = os.path.splitext(os.path.basename(filename))
    csv_filename = os.path.join("data_out/",base_filename+"_output.csv")
    themes_filename = os.path.join("data_out/",base_filename+"_themes.json")
    with open( csv_filename, "w" ) as f:
        f.write( results['csv'] )
    with open( themes_filename, "w" ) as f:
        f.write( results['themes'] )

    # Please note, this example does not include the tweaking of parameters, concepts or themes
    # These are required to get the most of the service and are described in the SDK documentation


if __name__ == "__main__": main()
