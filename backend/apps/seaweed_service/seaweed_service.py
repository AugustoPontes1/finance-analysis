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
        self.volume_url = settings.SEAWEEDFS_VOLUME_URL
    
    def upload_file(self, file_obj, filename):
        """
        Upload the file to the Seaweed service and return the file_id
        """
        try:
            logger.debug(f"Requesting file assignment from master: {self.master_url}")
            response = requests.post(f"{self.master_url}/dir/assign")
            response.raise_for_status()
            assign_data = response.json()
            logger.debug(f"Master assign response: {assign_data}")

            file_id = assign_data.get('fid')
            volume_server = assign_data.get('url')

            if not file_id or not volume_server:
                logger.error(f"Invalid assign response — fid={file_id}, url={volume_server}")
                return None

            upload_url = f"http://{volume_server}/{file_id}"
            logger.debug(f"Uploading '{filename}' to volume server: {upload_url}")
            files = {'file': (filename, file_obj)}
            upload_response = requests.post(upload_url, files=files)

            if upload_response.status_code in (200, 201):
                logger.info(f"File uploaded successfully: fid={file_id}, filename={filename}")
                return file_id
            else:
                logger.error(f"Volume upload failed [{upload_response.status_code}]: {upload_response.text}")
                return None

        except Exception as e:
            logger.error(f"Error uploading to SeaweedFS: {str(e)}", exc_info=True)
            return None
    
    def get_file(self, file_id):
        """
        Obtain the file and return its content and id
        """
        try:
            file_url = f"{self.volume_url}/{file_id}"
            logger.debug(f"Fetching file fid={file_id} from: {file_url}")
            response = requests.get(file_url)

            if response.status_code == 200:
                logger.info(f"File retrieved successfully: fid={file_id}, size={len(response.content)} bytes")
                return response.content
            else:
                logger.error(f"Failed to get file fid={file_id} [{response.status_code}]: {response.text}")
                return None

        except Exception as e:
            logger.error(f"Error retrieving file from SeaweedFS: {str(e)}", exc_info=True)
            return None

    def delete_file(self, file_id):
        """
        Remove the file from Seaweed
        """
        try:
            delete_url = f"{self.volume_url}/{file_id}"
            logger.debug(f"Deleting file fid={file_id} at: {delete_url}")
            response = requests.delete(delete_url)

            if response.status_code == 204:
                logger.info(f"File deleted successfully: fid={file_id}")
                return True
            else:
                logger.error(f"Delete failed fid={file_id} [{response.status_code}]: {response.text}")
                return False
        except Exception as e:
            logger.error(f"Error deleting file from SeaweedFS: {str(e)}", exc_info=True)
            return False

    def update_file(self, file_id, new_file_obj, filename):
        """
        Update the file but keeping the same id
        """
        try:
            upload_url = f"{self.volume_url}/{file_id}"
            logger.debug(f"Updating file fid={file_id}, new filename='{filename}' at: {upload_url}")
            files = {'file': (filename, new_file_obj)}
            response = requests.post(upload_url, files=files)

            if response.status_code == 201:
                logger.info(f"File updated successfully: fid={file_id}, filename={filename}")
                return file_id
            else:
                logger.error(f"Update failed fid={file_id} [{response.status_code}]: {response.text}")
                return None

        except Exception as e:
            logger.error(f"Error updating file in SeaweedFS: {str(e)}", exc_info=True)
            return None