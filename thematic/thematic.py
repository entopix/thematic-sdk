
import json
import time
#pip
import requests

class Thematic:
    def __init__(self, base_url, username, password):
        self.base_url = base_url
        self.retrieve_apikey( username, password )

    def retrieve_apikey( self, username, password):
        payload = {'username' : username, 
                    'password' : password
                  }
        r = requests.post(self.base_url+"/login",
                        data=payload)
        response = json.loads(r.text)
        if response["status"] != "success":
            raise Exception("retrieve_apikey: Failed to login ("+response["error"]["message"]+")")
        self.api_key = response["data"]["api_key"]



    def create_survey( self, name, total_columns, columns, has_header,modelset_id=None,output_format=None):
        payload = {'name' : name, 
                    'total_columns' : total_columns, 
                    'columns' : json.dumps(columns), 
                    'has_header' : has_header}
        # optional modelsetid
        if modelset_id:
            payload['modelset_id'] = modelset_id
        if output_format:
            payload['output_format'] = output_format
        r = requests.post(self.base_url+"/create_survey",
                        headers = {'X-API-Authentication' : self.api_key},
                        data=payload)
        response = json.loads(r.text)
        if response["status"] != "success":
            raise Exception("create_survey: Failed to create survey ("+response["error"]["message"]+")")
        if "survey_id" not in response["data"]:
            raise Exception("create_survey: Bad Response")
        return response["data"]


    def run_job( self, survey_id, csv_filename, previous_job_id=None ):
        files = {'csv_file': open(csv_filename, 'rb')}
        payload = { 'survey_id' : survey_id }
        if previous_job_id:
            payload["previous_job_id"] = previous_job_id
        r = requests.post(self.base_url+"/create_job",
                        headers = {'X-API-Authentication' : self.api_key},
                        files=files,
                        data=payload)
        response = json.loads(r.text)
        if response["status"] != "success":
            raise Exception("run_job: Failed to create job ("+response["error"]["message"]+")")
        if "jobid" not in response["data"]:
            raise Exception("run_job: Bad Response")
        return response["data"]["jobid"]

    def cancel_job( self, job_id ):
        r = requests.post(self.base_url+"/job/"+job_id+"/cancel",
                    headers = {'X-API-Authentication' : self.api_key}
                    )
        response = r.text
        print r.text
        return response

    def run_incremental_update( self, survey_id, csv_filename, previous_job_id=None ):
        files = {'csv_file': open(csv_filename, 'rb')}
        payload = { 'survey_id' : survey_id, 'job_type' : 'apply' }
        if previous_job_id:
            payload["previous_job_id"] = previous_job_id
        r = requests.post(self.base_url+"/create_job",
                        headers = {'X-API-Authentication' : self.api_key},
                        files=files,
                        data=payload)
        response = json.loads(r.text)
        if response["status"] != "success":
            raise Exception("run_incremental_update: Failed to create job ("+response["error"]["message"]+")")
        if "jobid" not in response["data"]:
            raise Exception("run_incremental_update: Bad Response")
        return response["data"]["jobid"]

    def run_translations( self, survey_id, csv_filename ):
        files = {'csv_file': open(csv_filename, 'rb')}
        payload = { 'survey_id' : survey_id, 'job_type' : 'translate' }
        r = requests.post(self.base_url+"/create_job",
                        headers = {'X-API-Authentication' : self.api_key},
                        files=files,
                        data=payload)
        response = json.loads(r.text)
        if response["status"] != "success":
            raise Exception("run_translations: Failed to create job ("+response["error"]["message"]+")")
        if "jobid" not in response["data"]:
            raise Exception("run_translations: Bad Response")
        return response["data"]["jobid"]

    def configure_concepts( self, concepts_filename, previous_job_id ):
        files = {'concepts_file': open(concepts_filename, 'rb')}
        payload = { }

        r = requests.post(self.base_url+"/job/"+previous_job_id+"/concepts",
                        headers = {'X-API-Authentication' : self.api_key},
                        files=files,
                        data=payload)
        response = json.loads(r.text)
        if response["status"] != "success":
            raise Exception("configure_concepts: Failed to create configuration job ("+response["error"]["message"]+")")
        if "jobid" not in response["data"]:
            raise Exception("configure_concepts: Bad Response")
        return response["data"]["jobid"]

    def configure_themes( self, themes_filename, previous_job_id ):
        files = {'themes_file': open(themes_filename, 'rb')}
        payload = { }

        r = requests.post(self.base_url+"/job/"+previous_job_id+"/themes",
                        headers = {'X-API-Authentication' : self.api_key},
                        files=files,
                        data=payload)
        response = json.loads(r.text)
        if response["status"] != "success":
            raise Exception("configure_themes: Failed to create configuration job ("+response["error"]["message"]+")")
        if "jobid" not in response["data"]:
            raise Exception("configure_themes: Bad Response")
        return response["data"]["jobid"]

    def configure_language_model( self, language_model_filename, previous_job_id ):
        files = {'model_file': open(language_model_filename, 'rb')}
        payload = { }

        r = requests.post(self.base_url+"/job/"+previous_job_id+"/language_model",
                        headers = {'X-API-Authentication' : self.api_key},
                        files=files,
                        data=payload)
        response = json.loads(r.text)
        if response["status"] != "success":
            raise Exception("configure_language_model: Failed to create configuration job ("+response["error"]["message"]+")")
        if "jobid" not in response["data"]:
            raise Exception("configure_language_model: Bad Response")
        return response["data"]["jobid"]

    def configure_parameters( self, parameters, previous_job_id ):
        payload = parameters

        r = requests.post(self.base_url+"/job/"+previous_job_id+"/params",
                        headers = {'X-API-Authentication' : self.api_key},
                        data=payload)
        response = json.loads(r.text)
        if response["status"] != "success":
            raise Exception("configure_parameters: Failed to create configuration job ("+response["error"]["message"]+")")
        if "jobid" not in response["data"]:
            raise Exception("configure_parameters: Bad Response")
        return response["data"]["jobid"]

    def get_job_details( self, job_id ):
        r = requests.get(self.base_url+"/job/"+job_id+"/info",
                    headers = {'X-API-Authentication' : self.api_key}
                    )
        response = json.loads(r.text)
        if response["status"] != "success":
            raise Exception("get_job_status: Failed to get job status ("+response["error"]["message"]+")")
        if "state" not in response["data"]:
            raise Exception("get_job_status: Bad Response")
        return response["data"]


    def get_job_logs( self, job_id ):
        r = requests.get(self.base_url+"/job/"+job_id+"/log",
                    headers = {'X-API-Authentication' : self.api_key}
                    )
        response = r.text
        return response


    def get_charts( self, job_id, columns, format="json", compare_job_id=None, top_n=None, include_ignored=False):
        payload = { 'columns' :json.dumps(columns), "format" : format, "compare_job_id" : compare_job_id, "top_n" : top_n, "include_ignored" : include_ignored }
        r = requests.get(self.base_url+"/job/"+job_id+"/charts/",
                    headers = {'X-API-Authentication' : self.api_key},
                    params=payload
                    )
        response = json.loads(r.text)
        if response["status"] != "success":
            raise Exception("get_charts: Failed to get charts ("+response["error"]["message"]+")")
        return response["data"]

    def wait_for_job_completion( self, job_id ):
        ready = False
        print("Waiting for results...")
        while not ready:
            job_details = self.get_job_details( job_id )
            status = job_details['state']
            if status == "finished":
                ready = True
                break
            elif status == "errored":
                raise Exception("wait_for_job_completion: Job errored and did not complete")
            elif status == "canceled":
                raise Exception("wait_for_job_completion: Job was canceled")

            time.sleep(2)

    def list_jobs( self, survey_id=None, job_type=None ):
        payload = { }
        if survey_id:
            payload['survey_id'] = survey_id
        if job_type:
            payload['job_type'] = job_type
        
        r = requests.get(self.base_url+"/jobs/",
                    headers = {'X-API-Authentication' : self.api_key},
                    params=payload
                    )
        if r.status_code != 200:
            return None
        response = json.loads(r.text)
        return response["data"]["jobs"]


    def retrieve_csv( self, job_id ):
        r = requests.get(self.base_url+"/job/"+job_id+"/csv/",
                    headers = {'X-API-Authentication' : self.api_key}
                    )
        if r.status_code != 200:
            return None
        return r.text.encode('utf-8')

    def retrieve_themes( self, job_id ):
        r = requests.get(self.base_url+"/job/"+job_id+"/themes/",
                    headers = {'X-API-Authentication' : self.api_key}
                    )
        if r.status_code != 200:
            return None
        return r.text.encode('utf-8')


    def retrieve_concepts( self, job_id ):
        r = requests.get(self.base_url+"/job/"+job_id+"/concepts/",
                    headers = {'X-API-Authentication' : self.api_key}
                    )
        if r.status_code != 200:
            return None
        return r.text.encode('utf-8')


    def retrieve_excel( self, job_id, column, nps_column ):
        r = requests.get(self.base_url+"/job/"+job_id+"/excel/"+str(column),
                  headers = {'X-API-Authentication' : self.api_key},
                       params={'nps_column' : nps_column}
                  )
        if r.status_code != 200:
            return None
        return r.content

    def retrieve_language_model( self, job_id ):
        r = requests.get(self.base_url+"/job/"+job_id+"/language_model/",
                  headers = {'X-API-Authentication' : self.api_key}
                  )
        if r.status_code != 200:
            return None
        return r.content
    

    def retrieve_parameters( self, job_id ):
        r = requests.get(self.base_url+"/job/"+job_id+"/params",
                    headers = {'X-API-Authentication' : self.api_key}
                    )
        response = json.loads(r.text)
        if response["status"] != "success":
            raise Exception("get_job_status: Failed to get job status ("+response["error"]["message"]+")")
        return response["data"]



