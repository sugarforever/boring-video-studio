# Full-screen terminal applications

Use this reference when a terminal session enters Vim, `less`, `man`, a database client, or another application that owns the terminal content area.

## State branch

Extend the core `child_app` state only with states the real application needs, such as:

- `tui_view`: the application owns the complete terminal content area;
- `tui_navigation`: its buffer or viewport has moved through a real keystroke or planned navigation event;
- `tui_command`: its command line or input mode is active;
- `tui_exit`: its real exit action is visible before control returns to the shell.

The outer terminal window remains stable while the child application controls the content area. Reconstruct its real buffer, cursor, viewport, status region, and command area from source and manifest events.

## Inspect-then-run branch

When an existing script is inspected and then executed, preserve this causal structure with the actual application and command:

1. type and submit the real command that opens the file;
2. let the full-screen application take over the terminal;
3. navigate or scroll to the relevant real source;
4. perform the application's real exit action;
5. show the returned shell prompt;
6. type and submit the real execution command;
7. reveal its evidenced output and returned prompt.

For Vim, this may be `vi <real-path>`, navigation or scrolling, `:q`, then the real execution command. Vim is an example of the branch, not the universal editor or runtime.

Code, the later shell command, and its output occupy successive application states. They are not simultaneous panels. Seek directly into entry, navigation, exit, shell return, and execution to verify each state independently.
