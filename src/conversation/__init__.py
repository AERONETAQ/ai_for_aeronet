"""One conversation = one folder, one docker container, one set of rows in SQLite.

current.py        which conversation this process works on
store.py          section 1: the SQLite table of turns
sandbox_state.py  section 2: the sandbox, its variables, restarts, kernel cleanup
context.py        section 3: history + state block = what the model sees
manage.py         new / load / delete / list conversations, running-container limit
"""
