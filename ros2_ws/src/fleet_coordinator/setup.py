from setuptools import setup

package_name = 'fleet_coordinator'

setup(
    name=package_name,
    version='0.0.0',
    packages=[package_name],
    data_files=[
        ('share/ament_index/resource_index/packages', ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='rick',
    maintainer_email='rickfriedman@vt.edu',
    description='Central fleet coordination: shares robot positions so robots avoid each other.',
    license='TODO: License declaration',
    entry_points={
        'console_scripts': [
            'fleet_state = fleet_coordinator.fleet_state:main',
        ],
    },
)
