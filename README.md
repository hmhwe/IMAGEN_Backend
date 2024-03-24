# IMAGEN_Backend

**Project Structure**

- **.github/workflows:** GitHub Actions workflows for automating build and push of Singularity containers.

- **definition_files:** Contains the definition files (*.def) for Singularity container images. This is the recipe for the images.

- **docs:** Weekly slide presentations and project documentation.

- **picas_client:** PiCas_Client (Pilot-Jobs) and Batch scripts for jobs

- **requirement.txt:** Project dependencies.

- **sonar-project.properties:** Configuration for SonarQube analysis.
  
**Instructions**

- Clone the repository:


        git clone git@github.com:hmhwe/IMAGEN_Backend.git
  
- cd IMAGEN_Backend
- Install dependencies using


      pip install -r requirement.txt
    
  
  **Steps to run Pilot-Jobs**
  - cd IMAGEN_Backend/picas_client
  - Create (install) views in CouchDB for tasks (by default):

         python  createViews.py
    
  - Create (install) Views in CouchDB for tasks with priority:

        python  createPriorityViews.py

  **Push tokens via CLI**
  

      python pushtoken.py  yoloToken.txt
  
    
  **Submit Pilot-Job to SLURM**


        sbatch submitPilotJob.sh
  

**Documentation**

- docs folder and wiki for weekly presentations and project documentation
