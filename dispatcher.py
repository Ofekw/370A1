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
        self._active_process = None
        self._running_process_stack = []
        self._paused_process_stack = []

    def set_io_sys(self, io_sys):
        """Set the io subsystem."""
        self.io_sys = io_sys

    def add_process(self, process):
        """Add and start the process."""
        size_of_stack = len(self._running_process_stack) + len(self._paused_process_stack)
        if self._active_process:
            self._active_process.block_event.wait()
            self._running_process_stack.append(self._active_process)
            self._active_process.iosys.move_process(self._active_process, size_of_stack)
        #process.iosys.allocate_window_to_process(size_of_stack, process)
        self._running_process_stack.append(process)
        self.dispatch_next_process()

    def dispatch_next_process(self):
        """Dispatch the process at the top of the stack."""
        size_of_stack = len(self._running_process_stack) + len(self._paused_process_stack)

        if self._running_process_stack:
            self._active_process = self._running_process_stack.pop()
            self._active_process.iosys.allocate_window_to_process(size_of_stack, self._active_process)
            self._active_process.state = State.runnable
            if self._active_process.is_alive():
                self._active_process.block_event.set()
            else:  # has not been started before
                self._active_process.start()
        #    else: #waiting
        #        self.running_process.state = State.runnable
        #        self.running_process.block_event.set()


    def to_top(self, process):
        """Move the process to the top of the stack."""
        for stackedProcess in self.processStack:
            if process == stackedProcess:
               index = self.processStack.index(stackedProcess)
               poppedProcess = self.processStack.pop(self)
               self.processStack.append(poppedProcess)







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
        #process.iosys.remove_window_from_process(process)
        #process.block_event.join()
        process.iosys.remove_window_from_process(process)
        self._active_process = None
        self.dispatch_next_process()

    def proc_waiting(self, process):
        """Receive notification that process is waiting for input."""
        process.state = State.waiting
        process.block_event.wait()

    def process_with_id(self, id):
        """Return the process with the id."""
        # ...
        return None

