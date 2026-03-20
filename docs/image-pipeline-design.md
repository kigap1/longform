# 이미지 파이프라인 설계

Character Consistency Engine과 Image Generation Engine은 다음 순서로 동작한다.

## 1. 장면 선택

- 사용자가 프로젝트와 `scene_id`를 선택한다.
- 장면의 `title`, `description`, 기존 `image_prompt`를 불러온다.

## 2. 캐릭터 해석

- 프로젝트 내 `locked=true` 캐릭터가 있으면 그 캐릭터를 항상 우선 사용한다.
- 잠금 캐릭터가 없을 때만 요청의 `character_profile_id` 또는 첫 번째 캐릭터를 사용한다.
- 이 규칙으로 프로젝트 전체 캐릭터 일관성을 유지한다.

## 3. 프롬프트 빌드

- 기본 입력:
  - 장면 제목/설명
  - 장면별 기본 프롬프트 또는 사용자 override
  - 선택된 캐릭터 프로필
  - 한국어 인포그래픽 레이아웃 입력
  - 선택 스냅샷 참조
  - 사용자 추가 지시
- 출력 규칙:
  - 한국어 자막/숫자 우선
  - 세로형 인포그래픽 레이아웃
  - 캐릭터 얼굴/의상/톤 일관성 유지
  - 스냅샷은 구도 참고용으로만 사용

## 4. 제공자 호출

- 현재는 `MockImageGeneratorAdapter`가 placeholder 이미지를 반환한다.
- 인터페이스는 다음 실연동을 염두에 두고 설계됐다:
  - 다중 reference image 입력
  - 기존 이미지 기반 edit/regenerate
  - 장면별 prompt override
  - 레이아웃 구조화 입력
- 즉, Nano Banana 스타일의 reference-aware/edit-capable provider를 adapter 교체만으로 연결할 수 있다.

## 5. 저장

- 최종 prompt는 `Scene.image_prompt`에 저장해 장면별 편집 기준으로 사용한다.
- 생성 결과는 `ImageAsset`에 저장한다.
- 생성/재생성/프롬프트 수정은 모두 `ProjectRevision` snapshot으로 남긴다.

## 6. 재생성

- 단일 scene 재생성은 최신 이미지가 있으면 provider의 edit 경로를 사용한다.
- 최신 이미지가 없으면 일반 generate 경로로 fallback한다.
- revision note로 최초 생성과 재생성을 구분한다.
