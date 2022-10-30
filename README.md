# Overview

This package provides a simple function dependency plotting functionality.

![This project's function dependency graph](./example_flow.svg)

## Quick start

To create the dependency flow chart any python project, simply run

```
python run.py -r {project_top_directory} -is {list} {of} {(sub)directories} {to} {ignore} -m {output_directory}
```

from the `graphit` directory. For example, to create the flow chart of functional dependencies

```
python run.py -r . -is output venv tests -m {output_directory}
```

## Outputs

A successful run will generate a timestamped subdirectory in the specified `{output_directory}`. It contains:
- meta data on the identified in scope python modules (i.e. `*/py` files)
  - see the `.csv` file
- meta data on the functions that were parsed from all relevant python modules 
  - see the `graphit_function_meta_data.csv` file
- meta data on the function dependencies based on identified function calls
  - see the `graphit_function_dependency_meta_data.csv` file
- meta data on the graph visualizing the functional dependency flow of the project
  - see the `graphit_{function_reference_id}_graph_meta_data.csv` file
- the depenency flow diagram, compatible with most browsers
  - see the `graphit_{function_reference_id}_graph_root_diagram.html`

Finally, it will try to open the `.html` file containing the flow chart in your default browser, too.
