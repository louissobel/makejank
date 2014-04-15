"""
loader that shells out
"""
import shlex
import subprocess
import threading
import time
import signal
import os

from . import BaseLoader

DEFAULT_SUBPROCESS_TIMEOUT = 5
PROCESS_POLL_TIMEOUT = .25

# Needed because python doesn't restore signal handlers
# that it sets to ignore on startup before exec.
# This can cause problems:
# http://stackoverflow.com/questions/23064636/python-subprocess-popen-blocks-with-shell-and-pipe
# http://bugs.python.org/issue1652
def restore_signals():
    signals = ('SIGPIPE', 'SIGXFZ', 'SIGXFSZ')
    for sig in signals:
        if hasattr(signal, sig):
            signal.signal(getattr(signal, sig), signal.SIG_DFL)

def _preexec_fn():
    os.setsid()
    restore_signals()

class ShellLoader(BaseLoader):

    tag = 'shell'

    def dependencies(self, env, arg, kwargs):
        """
        Dependencies are specified by optional
        depends_on kwarg
        TODO: should we warn / explode if nothing specified?
        TODO: need to assert type of depends_on?
        """
        return set(env.resolve_path(d) for d in kwargs.get('depends_on', []))

    def load(self, env, arg, kwargs):
        #command = shlex.split(arg)
        # TODO clearly not done.
        # - stderr to debug log
        # - catch error, propage as ValueError
        # - timeout
        try:
            process = subprocess.Popen(arg,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                shell=True,
                preexec_fn=_preexec_fn,
            )
        except OSError as e:
            raise ValueError("Unable to spawn shell for command %s: %s" % (arg, e.strerror))

        timeout = kwargs.get('timeout')
        # TODO type check timouet?
        if timeout is None: # prevent a None set timeout
            timeout = DEFAULT_SUBPROCESS_TIMEOUT

        start = time.time()
        while 1:
            now = time.time()
            if now - start > timeout:
                break
            else:
                # break if it is done
                r = process.poll()
                if r is not None:
                    break
                else:
                    time.sleep(PROCESS_POLL_TIMEOUT)

        # Check process status
        result = process.poll()
        if result is None:
            # Process is still running.
            terminated = self._terminate(process)
            if not terminated:
                raise ValueError("Unable to terminate timed out process %d, Maybe it setuid?" % process.pid)
            else:
                _, stderr = process.communicate()
                self._log_stderr(env, stderr)
                raise ValueError("Process %r timed out." % arg)
        else:
            stdout, stderr = process.communicate()
            self._log_stderr(env, stderr)
            if process.returncode == 127:
                # Command not found.
                raise SyntaxError("Command %r not found" % arg)
            elif process.returncode != 0:
                raise ValueError("Process %r exited with non-zero exit code %d" % (arg, process.returncode))
            else:
                return stdout

    def _log_stderr(self, env, stderr):
        if stderr:
            for line in stderr.split('\n'):
                env.logger.debug(line)

    def _terminate(self, process):
        # try and kill it (try/except,
        # because maybe it finished between the poll and now)
        # Try first to kill it nicely (SIGTERM)
        # if it's being bad, then SIGKILL
        try:
            still_running = self._try_and_signal(process, signal.SIGTERM)
            if not still_running:
                return True
            else:
                still_running = self._try_and_signal(process, signal.SIGKILL)
                if not still_running:
                    return True
                else:
                    return False

        except OSError as e:
            if e.errno == errno.EPERM:
                # Insufficient permissions to send our signal.
                # The process must have done a setuid!
                return False
            else:
                # Weird. Bubble.
                raise

    def _try_and_signal(self, process, sig):
        """
        Given process p and signum sig,
        attempts to send that signal.

        kill(2) can return 3 errnos, see 'man 2 kill' for details.
         - ESRCH
         - EPERM
         - EINVAL

        ESRCH is not handled, we assume always valid signum coming in.
        The other ones are bubbled up

        Returns True if the process is still running, False otherwise
        """
        try:
            process.send_signal(sig)
        except OSError as e:
            if e.errno == errno.ESRCH:
                # The process disappeared.
                return False
            else:
                raise
        # Give it a second..
        time.sleep(1)
        return (process.poll() is None)
