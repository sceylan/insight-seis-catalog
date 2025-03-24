# insight-seis-catalog

A lightweight Python module to read and utilize the InSight seismicity catalog for Mars, including the QuakeML BED + Mars extension.

Authors:
- Savas Ceylan, ETH Zurich
- Fabian Euchner, ETH Zurich

## Installation

We suggest that you work with virtual environments. If you already have one, activate it:

#### 1. Clone this repository
```bash
git clone https://github.com/your-username/insight-seis-catalog.git
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

