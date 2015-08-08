# A1 for COMPSCI340/SOFTENG370 2015
# Prepared by Robert Sheehan
# Modified by ...

# You are not allowed to use any sleep calls.

from threading import Lock, Event
from process import State
from process import Type

class Dispatcher():
    """The dispatcher."""

    MAX_PROCESSES = 8

    def __init__(self):
        """Construct the dispatcher."""
        self._running_process_stack = []
        self._waiting_process_stack = []


    def set_io_sys(self, io_sys):
        """Set the io subsystem."""
        self.io_sys = io_sys

    def add_process(self, process):
        """Add and start the process."""
        if self._running_process_stack:
            active_process = self._running_process_stack[len(self._running_process_stack)-1]
            active_process.state = State.waiting

        process.state = State.runnable
        self._running_process_stack.append(process)
        self.io_sys.allocate_window_to_process(process, len(self._running_process_stack)-1)
        self.dispatch_next_process()

    def dispatch_next_process(self):
        """Dispatch the process at the top of the stack."""
        if self._running_process_stack:
            active_process = self._running_process_stack[len(self._running_process_stack)-1]
            active_process.state = State.runnable
            if active_process.is_alive():
                active_process.block_event.set()
                active_process.block_event.clear()
            else:  # has not been started before
                active_process.start()

    def to_top(self, process):
        """Move the process to the top of the stack."""
        # ...


    def pause_system(self):
        """Pause the currently running process.
        As long as the dispatcher doesn't dispatch another process this
        effectively pauses the system.
        """
        # ...

    def resume_system(self):
        """Resume running the system."""
        # ...

    def wait_until_finished(self):
        """Hang around until all runnable processes are finished."""
        # ...

    def proc_finished(self, process):
        """Receive notification that "proc" has finished.
        Only called from running processes.
        """
        process.iosys.remove_window_from_process(process)
        self._running_process_stack.pop()
        self.dispatch_next_process()

    def proc_waiting(self, process):
        """Receive notification that process is waiting for input."""
        process.state = State.waiting
        self._running_process_stack.pop()
        self._waiting_process_stack.append(process)
        self.io_sys.move_process(process, len(self._waiting_process_stack)-1)
        process.block_event.wait()
        self.dispatch_next_process()

    def proc_resume(self, process):
        process.state = State.runnable
        self._waiting_process_stack.pop()
        self._running_process_stack.append(process)
        self.io_sys.move_process(process, len(self._running_process_stack)-1)
        self.dispatch_next_process()

    def process_with_id(self, id):
        """Return the process with the id."""
        for process in self._running_process_stack:
            if process.id == id:
                return process
        for process in self._waiting_process_stack:
                if process.id == id:
                    return process
        return None
