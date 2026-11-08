"""Offline smoke test for the core commands taught by the skill."""
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

@unittest.skipUnless(shutil.which('uv'), 'uv is required')
class ProjectWorkflow(unittest.TestCase):
    def test_lock_freshness_and_execution(self):
        with tempfile.TemporaryDirectory(prefix='uv-skill-test-') as directory:
            def run(*args):
                return subprocess.run(['uv', *args], cwd=directory, text=True, capture_output=True)
            for args in [
                ('init', '--bare', '--name', 'skill-smoke', '--no-workspace'),
                ('lock', '--offline'),
                ('sync', '--locked', '--offline'),
                ('run', '--locked', '--offline', 'python', '-c', 'print("skill-smoke-ok")'),
            ]:
                result = run(*args)
                self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn('skill-smoke-ok', result.stdout)
            project = Path(directory, 'pyproject.toml')
            project.write_text(project.read_text() + '\n[dependency-groups]\ntest = []\n')
            stale = run('lock', '--check', '--offline')
            self.assertNotEqual(stale.returncode, 0, 'Stale metadata must fail freshness verification')
            self.assertIn('lockfile', stale.stderr.lower())
            frozen = run('sync', '--frozen', '--offline')
            self.assertEqual(frozen.returncode, 0, frozen.stderr)

if __name__ == '__main__':
    unittest.main()
