# A1 for COMPSCI340/SOFTENG370 2015
# Prepared by Robert Sheehan
# Modified by Ofek Wittenberg

# You are not allowed to use any sleep calls.

from threading import Lock, Event
from process import State
from process import Type
from threading  import RLock

class Dispatcher():
    """The dispatcher."""

    MAX_PROCESSES = 8

    def __init__(self):
        """Construct the dispatcher."""
        self._running_process_stack = []
        self._waiting_process_stack = []
        self._location_list = [False]*8
        self.lock = RLock()


    def set_io_sys(self, io_sys):
        """Set the io subsystem."""
        self.io_sys = io_sys

    def add_process(self, process):
        """Add and start the process."""
        if self._running_process_stack and process.type == Type.background: #(and stack size not less then 3)
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

        if len(self._running_process_stack) > 1:
            proc_two = self._running_process_stack[len(self._running_process_stack)-2]
            proc_two.state = State.runnable
            if proc_two.is_alive():
                proc_two.block_event.set()
                proc_two.block_event.clear()

        if len(self._running_process_stack) > 2:
            proc_three = self._running_process_stack[len(self._running_process_stack)-3]
            proc_three.state = State.waiting

    def to_top(self, process):
        """Move the process to the top of the stack."""
        # for i in range(len(self._running_process_stack)-1):
        #     if self._running_process_stack[i] == process:
        self._running_process_stack.remove(process)
        self.io_sys.remove_window_from_process(process)
        self.update_running_stack()
        self._running_process_stack.append(process)
        process.state = State.runnable
        self.io_sys.allocate_window_to_process(process, len(self._running_process_stack)-1)

        self.dispatch_next_process()

        if len(self._running_process_stack) > 2:
            self._running_process_stack[len(self._running_process_stack)-3].state = State.waiting  # if stack is more than 2

    def update_running_stack(self):
        for i in range(0, len(self._running_process_stack)):
            self._running_process_stack[i].state = State.runnable
            self.io_sys.move_process(self._running_process_stack[i], i)

    def update_waiting_stack(self):
        for i in range(len(self._waiting_process_stack)):
            self._running_process_stack[i].state = State.waiting
            self.io_sys.move_process(self._waiting_process_stack[i], i)

    def pause_system(self):
        """Pause the currently running process.
        As long as the dispatcher doesn't dispatch another process this
        effectively pauses the system.
        """
        proc = self._running_process_stack[len(self._running_process_stack)-1]
        proc.state = State.waiting

        if len(self._running_process_stack) > 2:
            proc_two = self._running_process_stack[len(self._running_process_stack)-2]
            proc_two.state = State.waiting


    def resume_system(self):
        """Resume running the system."""
        self.dispatch_next_process()



    def wait_until_finished(self):
        """Hang around until all runnable processes are finished."""
        while len(self._running_process_stack) > 0:
            pass

    def proc_finished(self, process):
        """Receive notification that "proc" has finished.
        Only called from running processes.
        """
        process.iosys.remove_window_from_process(process)
        self._running_process_stack.remove(process)
        self.dispatch_next_process()

    def proc_waiting(self, process):
        """Receive notification that process is waiting for input."""
        process.state = State.waiting
        self._running_process_stack.remove(process)
        self._waiting_process_stack.append(process)

        # self.io_sys.move_process(process, len(self._waiting_process_stack)-1)
        for i in range(0, 8):
            if not self._location_list[i]:
                self.io_sys.move_process(process, i)
                self._location_list[i] = process
                break
        process.block_event.wait()
        self.dispatch_next_process()

    def proc_resume(self, process):
        for i in range(0, 8):
            if self._location_list[i] == process:
                self._location_list[i] = False
                break

        process.state = State.runnable
        self._waiting_process_stack.remove(process)
        self._running_process_stack.append(process)
        self.io_sys.move_process(process, len(self._running_process_stack)-1)
        self.dispatch_next_process()

    def proc_kill(self, process):

        process.state = State.killed
        process.block_event.set()
        if process.type == Type.background:
            self._running_process_stack.remove(process)
            self.io_sys.remove_window_from_process(process)
            self.update_running_stack()
        else:
            self._waiting_process_stack.remove(process)
            self.io_sys.remove_window_from_process(process)
            for i in range(0, 8):
                if self._location_list[i] == process:
                    self._location_list[i] = False
                    break



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
