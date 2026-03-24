## Pre-requisites

The tool is built ontop of two main technologies:
- Python `v3.14`
- Poetry `v2.3.2`

These need to be installed on the host machine prior to initializing the project pulling in its dependencies.

## Dependencies

Once the pre-requisites are in place, and you have checked out the repository, you should run the following command from the root directory of the repository, in order to install all the dependencies:

```shell
poetry install
```

## Running the Application

Once the dependencies are installed you should run the following command from the root directory of the repository, in order to start the application:

```shell
f1p
```

> Note: if you get a warning about the command not being found it's likely because you are not within the activated virtual environment of the poetry installation. In that case use `poetry run f1p` instead.

## Windows Notes

The application was built on a Windows machine, and it definitely works, however there may be a few things that need configuring to make it a bit more straight forward.

First of these dependencies is to ensure that the Python version installed is indeed `3.14`. Whether that is the default Windows App store version or a direct installation it doesn't matter. What does matter is if you have both. They will step on each other's toes and crash poetry. In such cases disable the Windows App store version.

Second, is making sure you have the Windows Subsystem for Linux (WSL) installed. Without it you can still run the app you will just have to suffix most commands with `.exe`.