# Virtual Environment (.venv)

This project contains a Python virtual environment named `.venv` at the repository root.

## Activate (macOS / zsh)

```bash
# create (if you haven't already)
python3 -m venv .venv

# activate
source .venv/bin/activate

# upgrade pip and install requirements
python -m pip install --upgrade pip setuptools wheel
python -m pip install -r requirements.txt

# deactivate when done
deactivate
```

## Notes
- The venv was created at: `.venv`
- The venv Python executable: `.venv/bin/python`
- To remove the venv entirely, delete the `.venv` directory.
