import os
import subprocess
import dotbot
import dotbot.util


class Shell(dotbot.Plugin):
    '''
    Run arbitrary shell commands.
    '''

    _directive = 'shell'

    def can_handle(self, directive):
        return directive == self._directive

    def handle(self, directive, data):
        if directive != self._directive:
            raise ValueError('Shell cannot handle directive %s' %
                directive)
        return self._process_commands(data)

    def _process_commands(self, data):
        success = True
        defaults = self._context.defaults().get('shell', {})
        for item in data:
            stdin = defaults.get('stdin', False)
            stdout = defaults.get('stdout', False)
            stderr = defaults.get('stderr', False)
            quiet = defaults.get('quiet', False)
            if isinstance(item, dict):
                cmd = item['command']
                msg = item.get('description', None)
                stdin = item.get('stdin', stdin)
                stdout = item.get('stdout', stdout)
                stderr = item.get('stderr', stderr)
                quiet = item.get('quiet', quiet)
                cond_cmd = item.get('if', None)
            elif isinstance(item, list):
                cmd = item[0]
                msg = item[1] if len(item) > 1 else None
            else:
                cmd = item
                msg = None
            if msg is None:
                self._log.lowinfo(cmd)
            elif quiet:
                self._log.lowinfo('%s' % msg)
            else:
                self._log.lowinfo('%s [%s]' % (msg, cmd))
            
            if cond_cmd is not None:
                cond = dotbot.util.shell_command(
                    cond_cmd,
                    cwd=self._context.base_directory(),
                    enable_stdin=stdin,
                    enable_stdout=stdout,
                    enable_stderr=stderr,
                )
                
                if cond != 0:
                    continue

            ret = dotbot.util.shell_command(
                cmd,
                cwd=self._context.base_directory(),
                enable_stdin=stdin,
                enable_stdout=stdout,
                enable_stderr=stderr
            )
            if ret != 0:
                success = False
                self._log.warning('Command [%s] failed' % cmd)
        if success:
            self._log.info('All commands have been executed')
        else:
            self._log.error('Some commands were not successfully executed')
        return success
