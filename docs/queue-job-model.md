# 큐 / 작업 모델

## 목적

장기 실행 작업을 사용자 요청-응답 흐름에서 분리하고, 실패 복구와 상태 추적을 가능하게 한다.

## 도메인 모델

- 코드 위치: `apps/api/app/domain/models.py`
- 핵심 타입:
  - `Job`
  - `JobLog`
- 관련 enum:
  - `JobType`
  - `JobStatus`

## 지원 작업 유형

- `issue_discovery`
- `stat_sync`
- `script_generation`
- `image_generation`
- `video_preparation`
- `snapshot_capture`

## 상태 전이

- `pending -> running -> success`
- `pending -> running -> failed`
- `failed -> pending` 재시도 가능

## 저장 모델

- 코드 위치: `apps/api/app/infrastructure/db/models.py`
- 테이블: `jobs`
- 필드:
  - `id`
  - `project_id`
  - `job_type`
  - `status`
  - `payload`
  - `result`
  - `error_message`
  - `retry_count`
  - `created_at`
  - `updated_at`

## 큐 인프라

- Celery 앱: `apps/api/app/infrastructure/queue/celery_app.py`
- 기본 태스크: `apps/api/app/infrastructure/queue/tasks.py`
- 브로커/백엔드: Redis

## 운영 규칙

- 장면 이미지 생성처럼 오래 걸리는 작업은 반드시 큐로 보낸다.
- 작업 실패 시 `error_message`와 로그를 남긴다.
- 재시도 여부는 `Job.can_retry(max_retries)`로 판정한다.
- 프런트는 `GET /api/jobs`와 `GET /api/jobs/{job_id}`로 상태를 조회한다.

