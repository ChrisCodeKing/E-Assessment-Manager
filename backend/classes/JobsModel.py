import os

class JobsModel:
    def __init__(self):
        self.jobs = []

    def load_jobs(self, folder_path):
        # Check if the directory exists
        if not os.path.exists(folder_path):
            # Create the directory if it does not exist
            os.makedirs(folder_path)
        
        # List the contents of the directory
        self.jobs = os.listdir(folder_path)

    def remove_job(self, file_name):
        try:
            os.remove(file_name)
            self.jobs.remove(os.path.basename(file_name))
            return True
        except OSError as e:
            print(f"Error: {e.strerror}")
            return False
