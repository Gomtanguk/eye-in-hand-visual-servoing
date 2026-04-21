from openai import OpenAI
import sounddevice as sd
import scipy.io.wavfile as wav
import numpy as np
import tempfile
import os
import sys

from dotenv import load_dotenv

try:
    from ament_index_python.packages import get_package_share_directory
except Exception:
    get_package_share_directory = None

openai_api_key = os.getenv("OPENAI_API_KEY")


def _load_env():
    env_path = None

    if get_package_share_directory is not None:
        try:
            pkg = get_package_share_directory("eye_in_hand")
            env_path = os.path.join(pkg, "resource", ".env")
        except Exception:
            env_path = None

    if not env_path:
        env_path = os.path.abspath(
            os.path.join(os.path.dirname(__file__), "..", "resource",".env")
        )
    
    if os.path.exists(env_path):
        load_dotenv(env_path)
    return env_path

_ENV_PATH = _load_env()
openai_api_key = os.getenv("OPENAI_API_KEY")

class STT:
    def __init__(self, openai_api_key=None, duration=7.0, samplerate=16000):
        # Ensure env is loaded even if this module was imported before env existed
        _load_env()

        api_key = openai_api_key or os.getenv("OPENAI_API_KEY")

        if not api_key:
            raise RuntimeError(
                "OPENAI_API_KEY is not set.\n"
                f"- .env 위치: {_ENV_PATH} (또는 eye_in_hand/resource/.env)\n"
                "- 터미널에서 export OPENAI_API_KEY=... 로 설정하거나\n"
                "- eye_in_hand/resource/.env 에 OPENAI_API_KEY=... 를 넣어주세요.\n"
                "※ .env는 Git에 올리지 마세요."
            )

        self.client = OpenAI(api_key=api_key)

        self.duration = float(duration)  # seconds
        self.samplerate = int(samplerate)  # Whisper는 16kHz를 선호
        

    def speech2text(self):
        print(f"음성 녹음을 시작합니다. \n {self.duration:.1f}초 동안 말해주세요...")
        audio = sd.rec(
            int(self.duration * self.samplerate),
            samplerate=self.samplerate,
            channels=1,
            dtype="int16",
        )
        sd.wait()
        print("녹음 완료. Whisper에 전송 중...")

        # 임시 WAV 파일 저장
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp_wav:
            wav.write(temp_wav.name, self.samplerate, audio)

            # Whisper API 호출
            with open(temp_wav.name, "rb") as f:
                transcript = self.client.audio.transcriptions.create(
                    model="whisper-1", file=f
                )

        print("STT 결과: ", transcript.text)
        return transcript.text