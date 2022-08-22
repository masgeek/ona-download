# Ona-Download

## Deployment

This project requires `python3` to be installed, ensure you haveit available globally on your system.

## Development

### Setup virtual environment `venv`

To create your virtual environment within your code directory run the command below

```bash
    python -m venv venv
```

### Activate virtual environment

You’ll need to use different syntax for activating the virtual environment depending on which operating system and command shell you’re using.

On Unix or MacOS, using the bash shell: source `/path/to/venv/bin/activate`

On Windows using the Command Prompt: `path\to\venv\Scripts\activate.bat`

To deploy this project run

### Install requirements

Run the following command withing the venv session to install dependencies

```bash
pip install -r requirements.txt
```

Next rename the `.env.example` to `.env` then update with the correct database credentials