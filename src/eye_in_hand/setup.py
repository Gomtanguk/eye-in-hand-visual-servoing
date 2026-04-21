import os
from glob import glob
from setuptools import find_packages, setup

package_name = "eye_in_hand"

resource_files = ["resource/" + package_name] + glob("resource/.env")
model_files = glob("resource/*.pt")

setup(
    name=package_name,
    version="0.0.0",
    packages=find_packages(exclude=["test"]),
    data_files=[
        ("share/ament_index/resource_index/packages", resource_files),
        ("share/" + package_name, ["package.xml"]),
        (os.path.join("share", package_name, "launch"), glob("launch/*.launch.py")),
        (os.path.join("share", package_name, "resource"), model_files),
    ],
    install_requires=["setuptools"],
    zip_safe=True,
    maintainer="june",
    maintainer_email="mhn06005@gmail.com",
    description="TODO: Package description",
    license="TODO: License declaration",
    extras_require={"test": ["pytest"]},
    entry_points={
        "console_scripts": [
            "tcp_follow = eye_in_hand.tcp_follow_node:main",
            "yolo_camera = eye_in_hand.yolo_camera_node:main",
            "auth_action = eye_in_hand.auth_action_server:main",
            "salute = eye_in_hand.salute_node:main",
            "shoot = eye_in_hand.shoot_node:main",
            "safety_monitor = eye_in_hand.safety_monitor_node:main",
            "orchestrator = eye_in_hand.orchestrator:main",
            'follow_ui_node = eye_in_hand.follow_ui_node:main',
            'follow_logger_node = eye_in_hand.follow_logger_node:main',
        ],
    },
)

