
import json
import time
import datetime
import logging
# pip
import requests

log = logging.getLogger(__name__)


class Thematic(object):
    num_retries = 5000

    @classmethod
    def FromLogin(self, base_url, username, password):
        self.base_url = base_url
        # create with unknown key
        thematic = Thematic(base_url, '')
        # login which will fill in key
        thematic.retrieve_apikey(username, password)
        return thematic

    def __init__(self, base_url, api_key):
        self.base_url = base_url
        self.api_key = api_key

    def retrieve_apikey(self, username, password):
        payload = {'username': username,
                   'password': password
                   }
        r = requests.post(self.base_url+"/login",
                          data=payload)
        response = json.loads(r.text)
        if response["status"] != "success":
            raise Exception(
                "retrieve_apikey: Failed to login ("+response["error"]["message"]+")")
        self.api_key = response["data"]["api_key"]
        self.login_cookie = r.headers['Set-cookie']

    def create_survey(self, name, total_columns, columns, has_header, modelset_id=None, output_format=None):
        payload = {'name': name,
                   'total_columns': total_columns,
                   'columns': json.dumps(columns),
                   'has_header': has_header}
        # optional modelsetid
        if modelset_id:
            payload['modelset_id'] = modelset_id
        if output_format:
            payload['output_format'] = output_format
        r = requests.post(self.base_url+"/create_survey",
                          headers={'X-API-Authentication': self.api_key},
                          data=payload)
        response = json.loads(r.text)
        if response["status"] != "success":
            raise Exception(
                "create_survey: Failed to create survey ("+response["error"]["message"]+")")
        if "survey_id" not in response["data"]:
            raise Exception("create_survey: Bad Response")
        return response["data"]

    def update_survey(self, survey_id, name=None, total_columns=None, columns=None, has_header=None, modelset_id=None, output_format=None):
        payload = {}
        if name:
            payload['columns'] = name
        if columns:
            payload['columns'] = columns
        if has_header:
            payload['has_header'] = has_header
        if total_columns:
            payload['total_columns'] = total_columns
        if modelset_id:
            payload['modelset_id'] = modelset_id
        if output_format:
            payload['output_format'] = output_format
        r = requests.put(self.base_url+"/survey/{}".format(survey_id),
                         headers={'X-API-Authentication': self.api_key},
                         data=payload)
        response = json.loads(r.text)
        if response["status"] != "success":
            raise Exception(
                "update_survey: Failed to create survey ("+response["error"]["message"]+")")
        return response["data"]

    def get_survey_details(self, survey_id):
        r = requests.get(self.base_url+"/survey/{}".format(survey_id),
                         headers={'X-API-Authentication': self.api_key})
        response = json.loads(r.text)
        if response["status"] != "success":
            raise Exception(
                "update_survey: Failed to create survey ("+response["error"]["message"]+")")
        return response["data"]

    def run_job_with_file_object(self, survey_id, files, previous_job_id=None, params=None):

        payload = {'survey_id': survey_id}
        if params:
            payload.update(params)
        if previous_job_id:
            payload["previous_job_id"] = previous_job_id
        r = requests.post(self.base_url+"/create_job",
                          headers={'X-API-Authentication': self.api_key},
                          files=files,
                          data=payload)
        response = json.loads(r.text)
        if response["status"] != "success":
            raise Exception("run_job: Failed to create job (" +
                            response["error"]["message"]+")")
        if "jobid" not in response["data"]:
            raise Exception("run_job: Bad Response")
        return response["data"]["jobid"]

    def run_job(self, survey_id, csv_filename, themes_file=None, previous_job_id=None, params=None):
        with open(csv_filename, 'rb') as csv_file_obj:
            files = {'csv_file': csv_file_obj}
            if themes_file:
                with open(themes_file, 'rb') as themes_file_obj:
                    files['themes_file'] = themes_file_obj
                    return self.run_job_with_file_object(survey_id, files, previous_job_id=previous_job_id, params=params)
            else:
                return self.run_job_with_file_object(survey_id, files, previous_job_id=previous_job_id, params=params)
        return None

    def create_job_from_artifacts(self, survey_id, artifacts_filename):
        with open(artifacts_filename, 'rb') as artifacts_file_obj:
            files = {'artifacts_file': artifacts_file_obj}
            return self.run_job_with_file_object(survey_id, files)

    def cancel_job(self, job_id):
        r = requests.post(self.base_url+"/job/"+job_id+"/cancel",
                          headers={'X-API-Authentication': self.api_key}
                          )
        response = r.text
        return response

    def delete_job(self, job_id):
        r = requests.get(self.base_url+"/job/"+job_id+"/delete",
                         headers={'X-API-Authentication': self.api_key}
                         )
        response = r.text
        return response

    def _run_post_request_with_json_response(self, url, files, data):
        r = requests.post(url,
                          headers={'X-API-Authentication': self.api_key},
                          files=files,
                          data=data)
        if r.status_code != 200:
            raise Exception('Failed with code {} and reason: {}'.format(
                r.status_code, r.text))
        response = json.loads(r.text)
        if response["status"] != "success":
            raise Exception(
                "run_incremental_update: Failed to create job ("+response["error"]["message"]+")")
        return response

    def run_incremental_update_with_file_object(self, survey_id, csv_file_obj, previous_job_id, disambiguation_columns=None):
        files = {'csv_file': csv_file_obj}
        payload = {'survey_id': survey_id, 'job_type': 'apply'}
        if disambiguation_columns is not None:
            payload['job_type'] = 'incremental_data'
            payload['updated_parameters'] = json.dumps({'disambiguation_columns': disambiguation_columns})
        if previous_job_id:
            payload["previous_job_id"] = previous_job_id
        response = self._run_post_request_with_json_response(
            self.base_url+"/create_job", files, payload)

        if "jobid" not in response["data"]:
            raise Exception("run_incremental_update: Bad Response")
        return response["data"]["jobid"]

    def run_incremental_update(self, survey_id, csv_filename, previous_job_id, disambiguation_columns=None):
        with open(csv_filename, 'rb') as csv_file_obj:
            return self.run_incremental_update_with_file_object(survey_id, csv_file_obj, previous_job_id, disambiguation_columns=disambiguation_columns)
        return None

    def run_translations(self, survey_id, csv_filename, columns=None):
        files = {'csv_file': open(csv_filename, 'rb')}
        payload = {'survey_id': survey_id, 'job_type': 'translate'}
        if columns:
            payload['job_options'] = json.dumps({'columns': columns})
        response = self._run_post_request_with_json_response(
            self.base_url+"/create_job", files, payload)

        if "jobid" not in response["data"]:
            raise Exception("run_translations: Bad Response")
        return response["data"]["jobid"]

    def configure_concepts(self, concepts_filename, previous_job_id):
        files = {'concepts_file': open(concepts_filename, 'rb')}
        response = self._run_post_request_with_json_response(
            self.base_url+"/job/"+previous_job_id+"/concepts", files, {})

        if "jobid" not in response["data"]:
            raise Exception("configure_concepts: Bad Response")
        return response["data"]["jobid"]

    def configure_word_frequencies(self, nouns_filename, verbs_filename, adjectives_filename, previous_job_id):
        files = {'nouns_file': open(nouns_filename, 'rb'),
                 'verbs_file': open(verbs_filename, 'rb'),
                 'adjectives_file': open(adjectives_filename, 'rb')}
        response = self._run_post_request_with_json_response(
            self.base_url+"/job/"+previous_job_id+"/word_frequencies", files, {})

        if "jobid" not in response["data"]:
            raise Exception("configure_word_frequencies: Bad Response")
        return response["data"]["jobid"]

    def configure_themes(self, themes_filename, previous_job_id):
        files = {'themes_file': open(themes_filename, 'rb')}
        response = self._run_post_request_with_json_response(
            self.base_url+"/job/"+previous_job_id+"/themes", files, {})

        if "jobid" not in response["data"]:
            raise Exception("configure_themes: Bad Response")
        return response["data"]["jobid"]

    def configure_language_model(self, language_model_filename, previous_job_id):
        files = {'model_file': open(language_model_filename, 'rb')}
        response = self._run_post_request_with_json_response(
            self.base_url+"/job/"+previous_job_id+"/language_model", files, {})

        if "jobid" not in response["data"]:
            raise Exception("configure_language_model: Bad Response")
        return response["data"]["jobid"]

    def configure_stopwords(self, stopwords_filename, previous_job_id):
        files = {'stopwords_file': open(stopwords_filename, 'rb')}
        response = self._run_post_request_with_json_response(
            self.base_url+"/job/"+previous_job_id+"/stopwords", files, {})

        if "jobid" not in response["data"]:
            raise Exception("configure_stopwords: Bad Response")
        return response["data"]["jobid"]

    def configure_parameters(self, parameters, previous_job_id):
        response = self._run_post_request_with_json_response(
            self.base_url+"/job/"+previous_job_id+"/params", None, parameters)

        if "jobid" not in response["data"]:
            raise Exception("configure_parameters: Bad Response")
        return response["data"]["jobid"]

    def get_job_details(self, job_id):
        r = requests.get(self.base_url+"/job/"+job_id+"/info",
                         headers={'X-API-Authentication': self.api_key}
                         )
        if r.status_code != 200:
            raise Exception("get_job_status: Bad Response: {} {}".format(
                r.status_code, r.text))
        response = json.loads(r.text)
        if response["status"] != "success":
            raise Exception(
                "get_job_status: Failed to get job status ("+response["error"]["message"]+")")
        if "state" not in response["data"]:
            raise Exception("get_job_status: Bad Response")
        return response["data"]

    def get_job_logs(self, job_id):
        r = requests.get(self.base_url+"/job/"+job_id+"/log",
                         headers={'X-API-Authentication': self.api_key}
                         )
        response = r.text
        return response

    def wait_for_job_completion(self, job_id, check_continue=None):
        ready = False
        log.info("Waiting for results of job "+job_id+" ...")
        current_status = "unknown"
        num_exceptions = 0
        start_time = time.time()
        process_start_time = 0
        end_time = 0
        log.info("\tStarted at {}".format(datetime.datetime.now()))
        while not ready:
            # protect the endpoint to get job details against transmission errors (because we call it so much)
            try:
                job_details = self.get_job_details(job_id)
                num_exceptions = 0
            except Exception as e:
                if num_exceptions >= self.num_retries:
                    num_exceptions += 1
                else:
                    raise Exception('Failure waiting for job completion after {} tries: {}'.format(
                        num_exceptions, e))

            status = job_details['state']
            if status == "finished":
                ready = True
                log.info("\tFinished at {}".format(datetime.datetime.now()))
                end_time = time.time()
                break
            elif status == "in_progress":
                process_start_time = time.time()
            elif status == "errored":
                log.error("\tErrored at {}".format(datetime.datetime.now()))
                raise Exception(
                    "wait_for_job_completion: Job errored and did not complete")
            elif status == "canceled":
                log.info("\tCancelled at {}".format(datetime.datetime.now()))
                raise Exception("wait_for_job_completion: Job was canceled")
            if status != current_status:
                current_status = status
                log.info("\tStatus is "+current_status)

            # check if we should still be waiting for this job
            if check_continue and not check_continue():
                raise Exception('wait_for_job_completion: Interrupted')

            time.sleep(2)
        log.info("\tStatus is finished")
        if process_start_time:
            # only prints if we spent time processing
            log.info("\tWaited {}s in queue and spent {}s processing".format(
                datetime.timedelta(seconds=(process_start_time-start_time)),
                datetime.timedelta(seconds=(end_time-process_start_time)))
            )

    def list_jobs(self, survey_id=None, job_type=None):
        payload = {}
        if survey_id:
            payload['survey_id'] = survey_id
        if job_type:
            payload['job_type'] = job_type

        r = requests.get(self.base_url+"/jobs/",
                         headers={'X-API-Authentication': self.api_key},
                         params=payload
                         )
        if r.status_code != 200:
            return None
        response = json.loads(r.text)
        return response["data"]["jobs"]

    def _internal_request_to_text_or_file(self, url, file_obj):
        log.info('getting {}'.format(url))
        if file_obj:
            r = requests.get(
                url, headers={'X-API-Authentication': self.api_key}, stream=True)
            if r.status_code != 200:
                return False
            for chunk in r.iter_content(chunk_size=512):
                if chunk:  # filter out keep-alive new chunks
                    file_obj.write(chunk)
            return True

        else:
            r = requests.get(
                url, headers={'X-API-Authentication': self.api_key})
            if r.status_code != 200:
                log.error('Failed to retrieve. Code {} message {}'.format(
                    r.status_code, r.text))
                return None
            return r.text.encode('utf-8')

    def retrieve_csv(self, job_id, file_obj=None):
        url = self.base_url+"/job/"+job_id+"/csv/"
        return self._internal_request_to_text_or_file(url, file_obj)

    def retrieve_incremental_csv(self, job_id, file_obj=None):
        url = self.base_url+"/job/"+job_id+"/incremental_csv/"
        return self._internal_request_to_text_or_file(url, file_obj)

    def retrieve_themes(self, job_id, file_obj=None):
        url = self.base_url+"/job/"+job_id+"/themes/"
        return self._internal_request_to_text_or_file(url, file_obj)

    def retrieve_stopwords(self, job_id, file_obj=None):
        url = self.base_url+"/job/"+job_id+"/stopwords/"
        return self._internal_request_to_text_or_file(url, file_obj)

    def retrieve_concepts(self, job_id, file_obj=None):
        url = self.base_url+"/job/"+job_id+"/concepts/"
        return self._internal_request_to_text_or_file(url, file_obj)

    def retrieve_nouns(self, job_id, file_obj=None):
        url = self.base_url+"/job/"+job_id+"/nouns/"
        return self._internal_request_to_text_or_file(url, file_obj)

    def retrieve_verbs(self, job_id, file_obj=None):
        url = self.base_url+"/job/"+job_id+"/verbs/"
        return self._internal_request_to_text_or_file(url, file_obj)

    def retrieve_adjectives(self, job_id, file_obj=None):
        url = self.base_url+"/job/"+job_id+"/adjectives/"
        return self._internal_request_to_text_or_file(url, file_obj)

    def retrieve_artifacts(self, job_id, file_obj=None):
        if file_obj is None:
            raise Exception("Artifacts must be retrieved into a file object")
        url = self.base_url+"/job/"+job_id+"/artifacts/"
        return self._internal_request_to_text_or_file(url, file_obj)

    def retrieve_language_model(self, job_id):
        r = requests.get(self.base_url+"/job/"+job_id+"/language_model/",
                         headers={'X-API-Authentication': self.api_key}
                         )
        if r.status_code != 200:
            return None
        return r.content

    def retrieve_parameters(self, job_id):
        r = requests.get(self.base_url+"/job/"+job_id+"/params",
                         headers={'X-API-Authentication': self.api_key}
                         )
        response = json.loads(r.text)
        if response["status"] != "success":
            raise Exception(
                "get_job_status: Failed to get job status ("+response["error"]["message"]+")")
        return response["data"]
