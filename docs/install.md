## Installation

This document describes how to install CFPQ_PyAlgo for regular use.

To compare the CFPQ_PyAlgo performance with that of third-party CFPQ solvers, 
you need a separate evaluation installation that includes third-party solvers and datasets 
(see [eval_install.md](eval_install.md)).

There are three ways to install CFPQ_PyAlgo. 
Choose one based on whether you need a stable or development version and whether you prefer to use Docker.

### Pre-Built Docker Images

This is the fastest way to install any stable CFPQ_PyAlgo version.

<details>
  <summary>Instructions</summary>
  
  1. Download the [image from DockerHub](https://hub.docker.com/r/cfpq/py_algo).
     If needed, replace the `latest` tag with a desired version.
     ```bash
     docker pull cfpq/py_algo:latest
     ```

  2. Run the container.
     ```bash
     docker run -it cfpq/py_algo:latest
     ```

  3. Refer to [cli.md](cli.md) for further usage instructions.
  
</details>

### Docker Image from Sources

This is the way to install CFPQ_PyAlgo from sources while still using Docker.

<details>
  <summary>Instructions</summary>
  
  1. Clone the repository with its submodules.
     ```bash
     git clone --recurse-submodules -b murav/optimize-matrix https://github.com/JetBrains-Research/CFPQ_PyAlgo.git
     cd CFPQ_PyAlgo/
     git submodule init
     git submodule update
     ```

  2. Build the Docker image.
     ```bash
     # Ensure we're in the project root directory
     cd $(git rev-parse --show-toplevel)
     
     docker build --tag cfpq/py_algo:from-source .
     ```

  3. Run the container.
     ```bash
     docker run -it cfpq/py_algo:from-source
     ```

  4. Refer to [cli.md](cli.md) for further usage instructions.
  
</details>

### Direct Installation from Sources

This is the way to install CFPQ_PyAlgo from sources without using Docker.

<details>
  <summary>Instructions</summary>

  1. Ensure that your OS is Linux-based. 
     If it's not, use one of the Docker-based installation methods.
  
  2. Clone the repository with its submodules.
     ```bash
     git clone --recurse-submodules -b murav/optimize-matrix https://github.com/JetBrains-Research/CFPQ_PyAlgo.git
     cd CFPQ_PyAlgo/
     git submodule init
     git submodule update
     ```
  3. Configure Python 3.9 virtual environment.

  4. Install legacy dependencies (if you skip this step tests for legacy algorithms won't pass).
     ```bash
     pip3 install pygraphblas==5.1.8.0
     cd $(git rev-parse --show-toplevel)/deps/CFPQ_Data
     pip3 install -r requirements.txt
     python3 setup.py install
     cd ../../
     ```

  5. Install production dependencies.
     ```bash
     # Ensure we're in the project root directory
     cd $(git rev-parse --show-toplevel)
     
     pip3 install -r requirements.txt
     ```

  6. Check if the installation was successful by running tests.
     ```bash
     # Ensure we're in the project root directory
     cd $(git rev-parse --show-toplevel)
     
     python3 -m pytest test -v -m "CI"
     ```

  7. Refer to [cli.md](cli.md) for further usage instructions.
  
</details>