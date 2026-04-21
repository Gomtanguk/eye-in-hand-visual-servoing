# eye-in-hand-visual-servoing

카메라를 엔드이펙터에 장착한 Eye-in-Hand 구성에서, 객체 탐지와 추적 결과를 이용해 로봇 TCP를 실시간 추종시키는 ROS 2 기반 협동로봇 프로젝트입니다. 인증 액션, UI, 로깅, 태스크 노드까지 포함한 통합 구성을 목표로 합니다.

## Quick Summary

- Domain: Eye-in-Hand 비전 서보잉과 인증 기반 태스크 자동화
- Stack: ROS 2 Humble, Python, YOLO, ByteTrack, Doosan ROS 2, PyQt
- Key Packages: `eye_in_hand`, `eye_in_hand_interfaces`, `doosan-robot2`

## Project Goal

- 카메라 입력으로 객체를 추적하고, 그 오차를 기반으로 로봇 TCP를 실시간 제어합니다.
- 단순 추종에서 끝나지 않고, lock 판정 이후 인증과 태스크 실행까지 연결되는 상위 상태기계를 구성합니다.
- 비전, 제어, UI, 로깅을 나눠서 유지보수하기 쉬운 ROS 2 패키지 구조로 정리합니다.

## Problem Statement

- 비전 기반 추종은 검출 노이즈, 프레임 간 흔들림, 작은 오차 진동 때문에 제어가 쉽게 불안정해집니다.
- 실제 작업에서는 단순히 목표를 따라가는 것만으로 충분하지 않고, 일정 조건을 만족했을 때만 후속 태스크를 실행해야 합니다.
- 이 프로젝트는 추적 안정화, lock 판정, 인증, 태스크 실행을 단계적으로 연결해 실험용 제어를 시스템 수준 워크플로우로 확장합니다.

## Key Features

- YOLO + ByteTrack 기반 객체 탐지와 추적
- 화면 중심 대비 오차를 `error_norm`으로 정규화
- `speedl` 기반 TCP 실시간 추종
- `lock_on` / `lock_done` 판정 로직
- 인증 액션 이후 태스크 실행
- UI와 로거를 통한 상태 모니터링 및 기록

## Repository Structure

```text
eye-in-hand-visual-servoing/
├── docs/
│   └── archive/
├── src/
│   ├── eye_in_hand/
│   ├── eye_in_hand_interfaces/
│   └── doosan-robot2/
├── README.md
└── requirements.txt
```

## Main Packages

- `eye_in_hand`
  - `tcp_follow`
  - `yolo_camera`
  - `auth_action`
  - `salute`
  - `shoot`
  - `safety_monitor`
  - `orchestrator`
  - `follow_ui_node`
  - `follow_logger_node`
- `eye_in_hand_interfaces`
  - `Auth.action`

## System Flow

1. `yolo_camera_node`가 객체를 탐지하고 추적합니다.
2. 중심점 오차를 정규화해 `error_norm`으로 발행합니다.
3. `tcp_follow_node`가 이를 TCP 속도 명령으로 변환합니다.
4. 추적 오차가 충분히 작고 안정적이면 `lock_done` 상태로 진입합니다.
5. `orchestrator`가 인증 액션을 호출합니다.
6. 인증 성공 시 `shoot`, `salute` 같은 후속 태스크를 실행합니다.

## Technical Highlights

### 1. Detection and Tracking

- 카메라 프레임에서 YOLO가 객체를 탐지합니다.
- ByteTrack이 프레임 간 동일 객체를 이어 붙여 추적 안정성을 높입니다.
- 추적 대상이 유지되면 중심점과 목표 지점의 상대 오차를 계산합니다.

### 2. Normalized Error Interface

- 이미지 좌표계에서 목표 중심과 화면 중심의 차이를 계산합니다.
- 해상도와 시야각 차이의 영향을 줄이기 위해 오차를 `-1 ~ 1` 범위의 `error_norm`으로 정규화합니다.
- 이 값이 비전 노드, 제어 노드, UI 사이의 공통 인터페이스 역할을 합니다.

### 3. IBVS-Style TCP Following

- `tcp_follow_node`는 `error_norm`을 입력으로 받아 TCP 속도 명령으로 변환합니다.
- Deadzone과 EMA 필터를 적용해 작은 진동과 노이즈를 줄입니다.
- 최종적으로 `speedl` 명령을 사용해 Doosan 로봇 TCP를 목표 방향으로 실시간 이동시킵니다.

### 4. Lock Decision and Orchestration

- 추적 오차가 충분히 작고 일정 시간 유지되면 `lock_done` 상태로 판정합니다.
- 추적 손실이나 목표 이탈 시에는 SEARCH 또는 TRACK 단계로 되돌립니다.
- 이 판정이 인증과 태스크 실행으로 넘어가는 상위 오케스트레이션의 기준 신호가 됩니다.

### 5. Post-Lock Task Execution

- `orchestrator`는 `lock_done` 이후 `auth_action`으로 승인 흐름을 시작합니다.
- 인증이 성공하면 `shoot` 또는 `salute` 같은 태스크 노드를 트리거합니다.
- 즉, 이 프로젝트는 추종 제어, 승인, 후속 행동을 하나의 상태기계로 연결한 구조입니다.

## Build

```bash
source /opt/ros/humble/setup.bash
cd <workspace-root>
colcon build --symlink-install
source install/setup.bash
```

## Run

```bash
ros2 launch eye_in_hand eye_in_hand.launch.py
```

개별 노드 실행 예시:

```bash
ros2 run eye_in_hand yolo_camera
ros2 run eye_in_hand tcp_follow
ros2 run eye_in_hand orchestrator
```

## Environment

- Ubuntu 22.04
- ROS 2 Humble
- Python 3.10 계열
- Doosan 로봇
- Intel RealSense D435i
- PyQt 기반 UI

## Portfolio Notes

- 현재 패키지명은 기능 기준으로 `eye_in_hand`, `eye_in_hand_interfaces`로 정리했습니다.
- 데모 영상은 저장소 밖 링크나 별도 배포 채널로 공유하는 것을 권장합니다.
- 발표자료와 압축본은 로컬 `docs/archive/`에 `eye-in-hand-visual-servoing-*` 형식으로 정리했습니다.
- `data/`는 필요 시 세션 로그나 로컬 측정 데이터를 두는 선택적 로컬 디렉토리입니다.
