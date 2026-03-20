# 데이터베이스 스키마

코드 기준 원본은 `apps/api/app/infrastructure/db/models.py` 이다.

## 1. 테이블 목록

### `projects`
| 필드 | 타입 | 설명 |
|---|---|---|
| `id` | string(36) | 프로젝트 식별자 |
| `name` | string | 프로젝트명 |
| `description` | text | 프로젝트 설명 |
| `issue_focus` | string nullable | 집중 이슈 범위 |
| `status` | string | 프로젝트 상태 |
| `created_at` | datetime | 생성 시각 |
| `updated_at` | datetime | 수정 시각 |

### `issues`
| 필드 | 타입 | 설명 |
|---|---|---|
| `id` | string(36) | 이슈 식별자 |
| `project_id` | fk | 프로젝트 연결 |
| `title` | string | 이슈 제목 |
| `category` | string | economy / investing / geopolitics |
| `summary` | text | 이슈 요약 |
| `priority_score` | float | 우선순위 점수 |
| `ranking_reasons` | json list | 랭킹 사유 |

### `articles`
| 필드 | 타입 | 설명 |
|---|---|---|
| `id` | string(36) | 기사 식별자 |
| `issue_id` | fk | 이슈 연결 |
| `title` | string | 기사 제목 |
| `source_name` | string | 출처명 |
| `url` | string | 원문 URL |
| `published_at` | datetime | 발행 시각 |
| `summary` | text | 기사 요약 |
| `credibility_score` | float | 출처 신뢰도 |
| `raw_payload` | json | 원본 응답 보관 |

### `statistics`
| 필드 | 타입 | 설명 |
|---|---|---|
| `id` | string(36) | 지표 식별자 |
| `project_id` | fk | 프로젝트 연결 |
| `indicator_code` | string | 공식 지표 코드 |
| `name` | string | 지표명 |
| `source_name` | string | ECOS/KOSIS/FRED/OECD |
| `latest_value` | float | 최신값 |
| `previous_value` | float nullable | 이전값 |
| `frequency` | string | 주기 |
| `release_date` | string | 발표일 |
| `unit` | string | 단위 |
| `stale` | boolean | 신선도 경고 |
| `series_payload` | json | 시계열 데이터 |

### `market_data`
| 필드 | 타입 | 설명 |
|---|---|---|
| `id` | string(36) | 자산 식별자 |
| `project_id` | fk | 프로젝트 연결 |
| `symbol` | string | 자산 심볼 |
| `display_name` | string | 표시명 |
| `asset_class` | string | equities / rates / commodities / fx / macro |
| `source_name` | string | 제공자명 |
| `latest_value` | float | 최신값 |
| `change_percent` | float | 변동률 |
| `as_of` | string | 기준 시각 |
| `chart_payload` | json | 차트 데이터 |

### `snapshots`
| 필드 | 타입 | 설명 |
|---|---|---|
| `id` | string(36) | 스냅샷 식별자 |
| `project_id` | fk | 프로젝트 연결 |
| `title` | string | 캡처 제목 |
| `source_url` | string | 출처 URL |
| `image_url` | string | 저장된 이미지 경로 |
| `note` | text | 캡처 메모 |
| `captured_at` | string | 캡처 시각 |
| `source_title` | string | 페이지 제목 |

### `evidences`
| 필드 | 타입 | 설명 |
|---|---|---|
| `id` | string(36) | 근거 식별자 |
| `project_id` | fk | 프로젝트 연결 |
| `source_kind` | string | article / statistic / market_data / snapshot |
| `label` | string | 근거 라벨 |
| `source_name` | string | 출처명 |
| `source_url` | string | 출처 URL |
| `indicator_code` | string nullable | 지표 코드 |
| `release_date` | string nullable | 발표일 |
| `value` | float nullable | 값 |
| `status` | string | verified / stale / conflict / missing |
| `note` | text | 비고 |
| `metadata_json` | json | 추가 메타데이터 |

### `scripts`
| 필드 | 타입 | 설명 |
|---|---|---|
| `id` | string(36) | 대본 식별자 |
| `project_id` | fk | 프로젝트 연결 |
| `issue_id` | fk nullable | 원천 이슈 |
| `title` | string | 대본 제목 |
| `outline` | json list | 개요 |
| `hook` | text | 도입 |
| `body` | text | 본론 |
| `conclusion` | text | 결론 |
| `status` | string | draft / review / approved |
| `version_number` | int | 버전 |
| `prompt_snapshot` | json | 생성 프롬프트 스냅샷 |

### `script_sections`
| 필드 | 타입 | 설명 |
|---|---|---|
| `id` | string(36) | 섹션 식별자 |
| `script_id` | fk | 대본 연결 |
| `heading` | string | 섹션 제목 |
| `content` | text | 섹션 본문 |
| `order_index` | int | 순서 |
| `evidence_ids` | json list | 연결된 근거 ID |

### `character_profiles`
| 필드 | 타입 | 설명 |
|---|---|---|
| `id` | string(36) | 캐릭터 식별자 |
| `project_id` | fk | 프로젝트 연결 |
| `name` | string | 캐릭터명 |
| `description` | text | 설명 |
| `prompt_template` | text | 기본 프롬프트 |
| `style_rules` | json list | 스타일 규칙 |
| `reference_assets` | json list | 참조 자산 |
| `locked` | boolean | 프로젝트 잠금 여부 |

### `scenes`
| 필드 | 타입 | 설명 |
|---|---|---|
| `id` | string(36) | 장면 식별자 |
| `project_id` | fk | 프로젝트 연결 |
| `script_id` | fk nullable | 대본 연결 |
| `title` | string | 장면명 |
| `description` | text | 장면 설명 |
| `image_prompt` | text | 이미지 프롬프트 |
| `motion_prompt` | text | 모션 프롬프트 |
| `order_index` | int | 순서 |

### `image_assets`
| 필드 | 타입 | 설명 |
|---|---|---|
| `id` | string(36) | 이미지 자산 ID |
| `scene_id` | fk | 장면 연결 |
| `prompt` | text | 사용 프롬프트 |
| `asset_url` | string | 저장 경로 |
| `thumbnail_url` | string | 썸네일 경로 |
| `status` | string | pending / ready / failed |
| `provider_name` | string | 제공자명 |
| `revision_note` | text | 수정 메모 |

### `video_assets`
| 필드 | 타입 | 설명 |
|---|---|---|
| `id` | string(36) | 영상 자산 ID |
| `scene_id` | fk | 장면 연결 |
| `prompt` | text | 영상 프롬프트 |
| `motion_notes` | text | 모션 노트 |
| `bundle_path` | string | 번들 경로 |
| `status` | string | pending / ready / failed |
| `provider_name` | string | 제공자명 |

### `jobs`
| 필드 | 타입 | 설명 |
|---|---|---|
| `id` | string(36) | 작업 식별자 |
| `project_id` | fk | 프로젝트 연결 |
| `job_type` | string | 작업 유형 |
| `status` | string | pending / running / success / failed |
| `payload` | json | 입력 데이터 |
| `result` | json | 결과 데이터 |
| `error_message` | text | 오류 메시지 |
| `retry_count` | int | 재시도 횟수 |

### `project_revisions`
| 필드 | 타입 | 설명 |
|---|---|---|
| `id` | string(36) | 리비전 식별자 |
| `project_id` | fk | 프로젝트 연결 |
| `entity_type` | string | script, scene, image_asset 등 |
| `entity_id` | string | 원본 엔터티 ID |
| `version_number` | int | 버전 번호 |
| `snapshot_json` | json | 스냅샷 |
| `change_note` | text | 변경 메모 |

### `app_settings`
| 필드 | 타입 | 설명 |
|---|---|---|
| `id` | string(36) | 설정 식별자 |
| `category` | string | api / storage / model / output |
| `key` | string | 설정 키 |
| `value` | text | 설정 값 |
| `secret` | boolean | 비밀값 여부 |

## 2. 핵심 관계

- `projects` 1:N `issues`
- `issues` 1:N `articles`
- `projects` 1:N `statistics`
- `projects` 1:N `market_data`
- `projects` 1:N `snapshots`
- `projects` 1:N `scripts`
- `scripts` 1:N `script_sections`
- `projects` 1:N `character_profiles`
- `projects` 1:N `scenes`
- `scenes` 1:N `image_assets`
- `scenes` 1:N `video_assets`
- `projects` 1:N `jobs`
- `projects` 1:N `project_revisions`

## 3. 설계 메모

- 숫자 근거 추적은 `evidences`와 `script_sections.evidence_ids`로 구현
- 공식 통계와 보조 시장 데이터는 별도 테이블로 분리
- 버전 복원은 `project_revisions`에서 담당
- 장기 실행 작업은 `jobs`에서 감사 추적 가능
