# eye-in-hand-visual-servoing

카메라를 엔드이펙터에 장착한 Eye-in-Hand 구성에서, 객체 탐지와 추적 결과를 이용해 로봇 TCP를 실시간 추종시키는 ROS 2 기반 협동로봇 프로젝트입니다. 인증 액션, UI, 로깅, 태스크 노드까지 포함한 통합 구성을 목표로 합니다.

## Quick Summary

- Domain: Eye-in-Hand 비전 서보잉과 인증 기반 태스크 자동화
- Stack: ROS 2 Humble, Python, YOLO, ByteTrack, Doosan ROS 2, PyQt
- Key Packages: `eye_in_hand`, `eye_in_hand_interfaces`, `doosan-robot2`

## 구조

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

## 패키지

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

## 핵심 흐름

- `yolo_camera_node`가 객체 탐지와 추적을 수행합니다.
- 탐지 결과를 `error_norm`으로 정규화합니다.
- `tcp_follow_node`가 `speedl` 기반으로 TCP 추종을 수행합니다.
- `orchestrator`가 lock 완료 이후 인증과 태스크 흐름을 제어합니다.
- `follow_ui_node`와 `follow_logger_node`가 모니터링과 기록을 담당합니다.

## 알고리즘 개요

### 1. 객체 탐지와 추적

- 카메라 프레임에서 YOLO가 객체를 탐지합니다.
- ByteTrack이 프레임 간 동일 객체를 이어 붙여 추적 안정성을 높입니다.
- 추적 대상이 유지되면 중심점과 목표 지점의 상대 오차를 계산합니다.

### 2. 정규화 오차 계산

- 이미지 좌표계에서 목표 중심과 화면 중심의 차이를 계산합니다.
- 해상도와 시야각 차이의 영향을 줄이기 위해 오차를 `-1 ~ 1` 범위의 `error_norm`으로 정규화합니다.
- 이 정규화 값이 제어 노드와 UI 사이의 공통 인터페이스 역할을 합니다.

### 3. IBVS 기반 TCP 추종

- `tcp_follow_node`는 `error_norm`을 입력으로 받아 TCP 속도 명령으로 변환합니다.
- Deadzone과 EMA 필터를 적용해 작은 진동과 노이즈를 줄입니다.
- 최종적으로 `speedl` 명령을 사용해 Doosan 로봇 TCP를 목표 방향으로 실시간 이동시킵니다.

### 4. lock_on / lock_done 판정

- 추적 오차가 충분히 작고 일정 시간 유지되면 `lock_done` 상태로 판정합니다.
- 이 판정은 인증과 태스크 실행으로 넘어가는 상위 오케스트레이션의 기준 신호가 됩니다.
- 추적 손실이나 목표 이탈 시 상태를 다시 SEARCH 또는 TRACK 단계로 되돌립니다.

### 5. 인증 후 태스크 실행

- `orchestrator`는 `lock_done` 이후 `auth_action`으로 승인 흐름을 시작합니다.
- 인증이 성공하면 `shoot` 또는 `salute` 같은 태스크 노드를 트리거합니다.
- 즉, 이 프로젝트는 단순 추종 제어가 아니라 추종, 정렬, 승인, 태스크 실행이 연결된 상태기계 구조입니다.

## 워크스페이스 빌드

```bash
source /opt/ros/humble/setup.bash
cd <workspace-root>
colcon build --symlink-install
source install/setup.bash
```

## 실행 예시

```bash
ros2 launch eye_in_hand eye_in_hand.launch.py
```

개별 노드 실행 예시:

```bash
ros2 run eye_in_hand yolo_camera
ros2 run eye_in_hand tcp_follow
ros2 run eye_in_hand orchestrator
```

## 환경

- Ubuntu 22.04
- ROS 2 Humble
- Python 3.10 계열
- Doosan 로봇
- Intel RealSense D435i
- PyQt 기반 UI

## 참고

- 현재 패키지명은 기능 기준으로 `eye_in_hand`, `eye_in_hand_interfaces`로 정리했습니다.
- 데모 영상은 `docs/eye-in-hand-visual-servoing-demo-video.mp4`로 관리합니다.
- 발표자료와 압축본은 로컬 `docs/archive/`에 `eye-in-hand-visual-servoing-*` 형식으로 정리했습니다.
- `data/`는 필요 시 세션 로그나 로컬 측정 데이터를 두는 선택적 로컬 디렉토리입니다.
