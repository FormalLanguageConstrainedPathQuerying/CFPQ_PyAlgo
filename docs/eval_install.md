## Evaluator Installation

This document describes how to install the CFPQ_PyAlgo evaluator, 
a tool for evaluating the performance of various CFPQ solvers.

There are two ways to install the CFPQ_PyAlgo evaluator. 
Choose one based on whether you need a stable or development version.

**NOTE**: Some third-party tools are only available for x64 CPU architecture,
so you can only use the evaluator on that architecture. 
For other CPU architectures, you can still use CFPQ_PyAlgo without the performance evaluator 
(see [install.md](install.md)).

### Pre-Built Docker Image

This is the fastest way to install any stable CFPQ_PyAlgo evaluator version.

<details>
  <summary>Instructions</summary>
  
  1. Download the [image from DockerHub](https://hub.docker.com/r/cfpq/py_algo_eval).
     If needed, replace the `latest` tag with a desired version.
     ```bash
     docker pull cfpq/py_algo_eval:latest
     ```

  2. Run the container.
     ```bash
     docker run -it cfpq/py_algo_eval:latest
     ```

  3. Refer to [eval.md](eval.md) for further usage instructions.
  
</details>

### Docker Image from Sources

This is the way to install the CFPQ_PyAlgo evaluator from sources.

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
     
     # Load base image
     wget -O pearl.tar.gz https://figshare.com/ndownloader/files/42214812
     docker load --input pearl.tar.gz
     rm pearl.tar.gz
     
     # Build the eval image
     docker build -f Dockerfile-all-tools -t cfpq/py_algo_eval:from-source .
     ```

  3. Run the container.
     ```bash
     docker run -it cfpq/py_algo_eval:from-source
     ```

  4. Refer to [eval.md](eval.md) for further usage instructions.
  
</details>
