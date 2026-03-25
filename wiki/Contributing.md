## Architecture

The system follows industry standard best practices for building performant, testable, and maintainable code. The underlying technologies used for the code are:

- [FastF1 API](https://github.com/theOehrly/Fast-F1) - A python package for extracting Formula 1 data
- [Panda3D](https://www.panda3d.org) - Framework for 3D rendering and Games

On top of these there is a good amount of Data Processing with vectorized operations in `pandas` DataFrame and Series objects. (The data coming back from the FastF1 api has been cleaned up, but leaves lots ot be desired when it comes to usable structures for a complete session timeline)

## CI

There is a CI workflow [ci.yml](/MrSir/f1-player/blob/main/.github/workflows/ci.yml) which builds the dependencies and then performs 3 main checks:
- lint check with `ruff`
- format check with `ruff`
- unit tests execution with `pytest`

## Merge Requests Requirements

The merge request MUST comply with these rules:

1. The MR Title MUST summarize the change being introduced in a concise way.
2. The MR Description MUST NOT be blank.
3. The MR Description MUST contain a `### WHY?` heading with a clear and concise explanation on why the change is being introduced.
4. The MR Description MUST contain a `### WHAT?` heading with a clear and concise description of the major areas being changed/introduced. (bullets are fine)
5. Commit conventions are up to the author, they WILL be squashed post merge.
6. The MR MUST NOT contain hundreds of lines of changes or more. (Small incremental changes are what we are looking for.)
7. THE MR MUST be reviewed and approved by the F1P Author [MrSir](https://github.com/MrSir), or any authorized contributor, before it can be merged.
8. The CI checks MUST succeed for the MR to be merged.
 

## Unit Tests

The application aims to be as stable and maintainable as possible, for this reason it is released with nearly 100% code coverage with unit tests. Tests which must pass as part of the CI checks.

The tests are written and executed via `pytest`

## WIKI

DO NOT EDIT the WIKI directly in the GitHub UI. The WIKI contents are managed within the repo itself (`wiki` directory), and are subject to the same MR process as code changes. Upon merging to master the [wiki.yml](/MrSir/f1-player/blob/main/.github/workflows/wiki.yml) workflow will run and synchronize the changes with the actual WIKI pages.

## Contributing with AI

Using AI to make contributions to the repository is largely discouraged because of the non-deterministic nature of AI systems making it impossible to guarantee compliance with the coding standards. That being said if you want to utilize AI to help speed up some of your code contributions then try to following to reduce the likelihood of rejection.

As far as models go `Claude` has been the most consistent, I recommend anything above `4.5`.

When formulating your prompt prefix it with the following. 
```
Analyze and follow the instructions in the `./ai/patterns.md` file first. Then ...
```

Make sure to also include the [ai/patterns.md](/MrSir/f1-player/blob/main/ai/patterns.md) file into the context for more deterministic results.

AI Slop will not be tolerated.