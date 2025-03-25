# insight-seis-catalog

A lightweight Python module to read and utilize the InSight seismicity catalog for Mars, including the QuakeML BED + Mars extension.

Authors:
- Savas Ceylan, ETH Zurich
- Fabian Euchner, ETH Zurich

## Installation

We suggest that you work with virtual environments. If you already have one, activate it:

#### 1. Clone this repository
```bash
git clone https://github.com/sceylan/insight-seis-catalog.git
cd insight-seis-catalog
```

#### 2. If you do not have a virtual environment, create a new one
In the example below, we use ```.venv``` under the current working directory. Change this to a path where you most favor.
```bash
python -m venv .venv
```

#### 3. Activate your environment
```bash
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

#### 4. Install the module
```bash
pip install -e .
```


## Citation

We plan to distribute this repository as a supplement to an upcoming paper. Until then, please consider citing these studies where relevant if you use this package:

The last official release of InSight catalog itself:
- InSight Marsquake Service (2023). Mars Seismic Catalogue, InSight Mission; V14 2023-04-01. ETHZ, IPGP, JPL, ICL, Univ. Bristol. https://doi.org/10.12686/a21

Related papers:

- Ceylan, S., Clinton, J.F., Giardini, D., Stähler, S.C., Horleston, A., Kawamura, T., Böse, M., et al., 2022, The marsquake catalogue from InSight, sols 0–1011. Physics of the Earth and Planetary Interiors, Elsevier BV. doi:10.1016/j.pepi.2022.106943

- Clinton, J.F., Ceylan, S., Driel, M. van, Giardini, D., Stähler, S.C., Böse, M., Charalambous, C., et al., 2021, The Marsquake catalogue from InSight, sols 0–478. Physics of the Earth and Planetary Interiors, Elsevier BV. doi:10.1016/j.pepi.2020.106595
