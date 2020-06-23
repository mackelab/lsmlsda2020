Welcome to the repo for module 3. The demos/labs will be done within Jupyter Lab. To avoid all issues with compatibility and versions we recommend you to create and use a new conda environment. Download the *environment.yml* file and then run:

conda env create -f {path to the enviroment.yml file}

conda activate imaginganalysis

jupyter labextension install @jupyter-widgets/jupyterlab-manager ipyevents ipycanvas

jupyter lab
