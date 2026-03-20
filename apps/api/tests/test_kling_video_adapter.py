from unittest import TestCase
from unittest.mock import patch

from app.domain.provider_interfaces import VideoExecutionRequestPayload
from app.infrastructure.providers.kling_video import KlingVideoBridgeAdapter


class _FakeResponse:
    def __init__(self, body: bytes) -> None:
        self.body = body

    def __enter__(self) -> "_FakeResponse":
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        _ = (exc_type, exc, tb)

    def read(self) -> bytes:
        return self.body


class KlingVideoBridgeAdapterTests(TestCase):
    @patch("app.infrastructure.providers.kling_video.time.sleep", return_value=None)
    @patch("app.infrastructure.providers.kling_video.urlopen")
    def test_execute_bundle_retries_once_after_transient_connection_reset(self, mock_urlopen, _mock_sleep) -> None:
        mock_urlopen.side_effect = [
            ConnectionResetError("peer reset"),
            _FakeResponse(b'{"job_id":"kling-job-1","status":"queued","output_path":"/tmp/kling.mp4"}'),
        ]

        adapter = KlingVideoBridgeAdapter(
            api_key="test-key",
            base_url="http://127.0.0.1:9999",
            submit_path="/bridge/submit",
            status_path=None,
            result_path=None,
            retry_delay_seconds=0,
        )

        result = adapter.execute_bundle(
            VideoExecutionRequestPayload(
                project_id="project-1",
                scene_id="scene-1",
                video_asset_id="video-1",
                bundle_path="/tmp/bundle.zip",
                user_instructions="",
            )
        )

        self.assertEqual(mock_urlopen.call_count, 2)
        self.assertEqual(result.provider_job_id, "kling-job-1")
        self.assertEqual(result.status, "queued")
