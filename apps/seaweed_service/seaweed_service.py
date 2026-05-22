import requests
from django.conf import settings
import logging

logger = logging.getLogger(__name__)


class SeaweedFSService:
    """ 
    File Storage class to save the documents
    """
    def __init__(self):
        self.master_url = settings.SEAWEEDFS_MASTER_URL
        self.volume_url = settings.SEAWEED_VOLUME_URL
    
    def upload_file(self, file_obj, filename):
        """ 
        Upload the file to the Seaweed service and return the file_id
        """
        try:
            # 1. Search a path to save the file inside of Seaweed master
            response = requests.post(f"{self.master_url}/dir/assign")
            assign_data = response.json()
            
            # 2. Obtain the file_id and the volume server
            file_id = assign_data.get('fid')
            volume_server = assign_data.get('url')
            
            # 3. Upload the file to the volumer server
            files = {'file': (filename, file_obj)}
            upload_url = f"http://{volume_server}/file_id"
            upload_response = requests.post(upload_url, files=files)
            
            if upload_response.status_code == 201:
                logger.info(f"File uploaded successfully: {file_id}")
                return file_id
            else:
                logger.info(f"Upload failed: {upload_response.text}")
                return None

        except Exception as e:
            logger.error(f"Error uploading to SeaweedFS: {str(e)}")
    
    def get_file(self, file_id):
        """ 
        Obtain the file and return its content and id
        """
        try:
            file_url = f"{self.volume_url}/{file_id}"
            response = requests.get(file_url)
            
            if response.status_code == 200:
                return response.content
            else:
                logger.error(f"Failed to get file: {file_id}")
                return None

        except Exception as e:
            logger.error(f"Error retrieving file from SeaweedFS: {str(e)}")
            return None
        
    def delete_file(self, file_id):
        """ 
        Remove the file from Seaweed
        """
        try:
            delete_url = f"{self.volume_url}/{file_id}"
            response = requests.delete(delete_url)
            return response.status_code == 204
        except Exception as e:
            logger.error(f"Error deleting file from SeaweedFS: {str(e)}")
            return False
    
    def update_file(self, file_id, new_file_obj, filename):
        """
        Update the file but keeping the same id
        """
        try:
            upload_url = f"{self.volume_url}/{file_id}"
            
            files = {'file': (filename, new_file_obj)}
            response = requests.post(upload_url, files=files)
            
            if response.status_code == 201:
                logger.info(f"File updated with same ID: {file_id}")
                return file_id
            else:
                logger.error(f"Update failed: {response.text}")
                return None
        
        except Exception as e:
            logger.error(f"Error updating file in SeaweedFS: {str(e)}")
            return None