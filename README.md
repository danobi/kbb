kbb
=====

`kbb` is a kanban board implementation for the terminal. It's core feature is that it syncs with Google Tasks via the developer API. 


Features:
----
- User defined stages
 
- Command line user interface

- GTasks integration


Quickstart:
----
1) `git clone https://github.com/danobi/kbb.git`

2) `cd kbb`

3) `python3 -m virtualenv venv`

4) `source venv/bin/activate`

5) `pip install -r requirements.txt`

6) `python -m gui.gui   # start kbb`


Commands:
---
- `/sync` 
  - Explicitly syncs local task database with cloud database

- `/new [....]`
  - Creates a new task with the task name as `[...]`
  - Example: `/new update README.md for kbb`

- `/move [task #] [destination stage]`
  - Moves the task ([task #]) to the destination stage, where the [task #] is the number in square brackets in the GUI
  - Example: `/move 3 to done`

- `/delete [task #]`
  - Delete the task ([task #]), where the [task #] is the number in square brackets in the GUI
  - Example: `/delete 4`

- `/quit` or `CTRL-C`
  - Quits kbb
  - `CTRL-C` means press the `c` key on the keyboard while holding the `Ctrl` key


TODO:
----
- [x] Implement core API

- [x] Implement UI

- [ ] Create testing framework
  - [ ] Use separate testing environment 

- [ ] Write more thorough user documentation
  - [ ] Config file documentation

- [ ] Package `kbb`
  - [ ] Put some nice screenshots into this README
  - [ ] Package GTasks API key

- [ ] Clean up API
  - [ ] Remove returning of `Task` object after inserting task, since task_id isn't consistent after online sync
