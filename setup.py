from setuptools import setup, find_packages
from setuptools.command.install_scripts import install_scripts
import sys


class ManualAdminInstallation(install_scripts):
    def run(self):
        install_scripts.run(self)
        for script in self.get_outputs():
            if "matrix-admin" in script:
                with open(script, 'r+') as f:
                    content = f.read()
                    if not content.startswith('#!'):
                        f.seek(0)
                        f.write('#!{python}\n\n'.format(python=sys.executable))
                        f.write(content)


setup(
    name='matrix', 
    version='0.1.0', 
    description='A module to handle projects and connections to the Matrix repo server',
    author='MrEsi',
    author_email='mresi@here.there',
    packages=find_packages(where="matrix"),
    # package_dir={"": "matrix"},
    include_package_data=True,
    entry_points={
        'console_scripts': [
            'matrix-admin=matrix.matrix_admin:main',
        ]
    },
    cmdclass={'install_scripts': ManualAdminInstallation},
)
