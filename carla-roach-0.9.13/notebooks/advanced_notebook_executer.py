import nbformat
from nbclient import NotebookClient

def run_notebook(notebook_path):
    with open(notebook_path) as f:
        notebook = nbformat.read(f, as_version=4)
    client = NotebookClient(notebook)
    client.execute()

# Example usage
run_notebook("/home/ubuntu/vihaan-devel/carla/sip-report-gen/carla-roach-0.9.13/notebooks/advanced_replay.ipynb")