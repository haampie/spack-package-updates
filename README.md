# Spack Package Updates

This tool identifies important outdated packages in Spack by analyzing the dependency graph and ranking packages based on their "authority" according to the HITS algorithm.

## Installation

```bash
pip install git+https://github.com/haampie/spack-package-updates
```

## Usage

Run the script to see the most important outdated packages:

```bash
spack-package-updates
```

## Example Output

```
         ninja:       1.13.0 -> 1.13.2       
     gnuconfig:   2024-07-27 -> 20250710     
         mpich:        4.3.2 -> 5.0.0        
         msmpi:       10.1.1 -> 10.1.12498.52
        py-pip:       25.1.1 -> 26.0.1       
```

The output shows:
- Package name
- Current version in Spack
- Latest version available (from Repology)
