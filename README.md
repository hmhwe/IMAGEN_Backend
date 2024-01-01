# IMAGEN_Backend

**Project Structure**

- **.github/workflows:** GitHub Actions workflows for automating build and push of Singularity containers.

- **definition_files:** Contains the definition files (*.def) for Singularity container images. This is the recipe for the images.

- **docs:** Weekly slide presentations and project documentation.

- **picas_client:** PiCas_Client (Pilot-Jobs) and Batch scripts for jobs

- **requirement.txt:** Project dependencies.

- **sonar-project.properties:** Configuration for SonarQube analysis.
  
**Instructions**

- Clone the repository.
- Install dependencies using `pip install -r requirement.txt`.

**Usage**

Building and Pushing Singularity Containers

- Run the GitHub Actions workflow on push to main branch

- The workflow checks for changes in definition_files and builds/pushes Singularity containers

**Documentation**

- Check docs folder and wiki for weekly presentations and project documentation
