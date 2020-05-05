# Logistics 
The exericises in this module are based on the Gerstner et al. `Neuronal Dynamics` book and use `brian2` and `neurodynex`.

## Brian2

We hope that you familiarized yourself with the basics of `brian2` in `module0` already. Just in case, here you find
links to the [brian2 tutorials](https://brian2.readthedocs.io/en/stable/resources/tutorials/index.html)
to make onself familiar with the main concepts:
- [neurons](https://brian2.readthedocs.io/en/stable/resources/tutorials/1-intro-to-brian-neurons.html),
- [synapses](https://brian2.readthedocs.io/en/stable/resources/tutorials/2-intro-to-brian-synapses.html),
- and [simulations](https://brian2.readthedocs.io/en/stable/resources/tutorials/3-intro-to-brian-simulations.html).

## Neurodynex

The exercises also make use of the package [neurodynex](https://github.com/EPFL-LCN/neuronaldynamics-exercises) which was developed for the coding exercises that come with the "Neuronal Dynamics" book. It is installed
as part of the `lsmlsda` `conda` environment. As part of the exercises you will be asked to inspect code that comes with the `neudynex` package. You can either do this online at [https://github.com/EPFL-LCN/neuronaldynamics-exercises/blob/master/neurodynex/competing_populations/decision_making.py](https://github.com/EPFL-LCN/neuronaldynamics-exercises/blob/master/neurodynex/competing_populations/decision_making.py), or locally on your machine. 

To find out where the `neurodynex` package has been installed locally, open a terminal and execute:
```
conda activate lsmlsda
python -c "import neurodynex; import os; print(os.path.dirname(neurodynex.__file__))
```

This will return the path to the package, for example, `~/anaconda3/envs/lsmlsda/lib/python3.5/site-packages/neurodynex/` -- the simulator for the decision making exercise will then be in `~/anaconda3/envs/lsmlsda/lib/python3.5/site-packages/neurodynex/competing_populations/decision_making.py`.
