# 비디오 파이프라인 설계

Video Generation Preparation Engine은 장면별 이미지를 세로형 숏폼 영상 워크플로로 넘기기 위한 준비 계층이다.

## 1. 장면 선택

- 프로젝트에서 scene 목록을 선택한다.
- 각 scene의 제목, 설명, `image_prompt`, `motion_prompt`를 읽는다.

## 2. 이미지 참조 결정

- 기본적으로 해당 scene의 최신 `ImageAsset`을 참조 이미지로 사용한다.
- 이미지가 없으면 scene의 텍스트 프롬프트만으로 번들을 준비한다.

## 3. 세로형 비디오 프롬프트 빌드

- 입력 요소:
  - 장면 제목/설명
  - 최신 이미지 URL과 이미지 프롬프트
  - 기존 motion prompt
  - 세로형 지시
    - 비율
    - 길이
    - 프레이밍
    - 자막 스타일
    - 템포
    - 모션 강조도
  - 사용자 추가 지시
- 출력:
  - 장면별 video prompt
  - 모션 노트

## 4. 번들 패키징

- scene별로 zip bundle을 만든다.
- bundle에는 다음이 포함된다:
  - `manifest.json`
  - `video_prompt.txt`
  - `motion_notes.txt`
  - `image_reference.json` (이미지 참조가 있을 때)
  - `README.txt`
- 현재 mock 단계에서는 이미지 바이너리 대신 이미지 참조 URL과 프롬프트를 묶는다.

## 5. 제공자 준비/실행

- `VideoWorkflowPort`는 prepare와 execute를 분리한다.
- 현재는 `MockVeoWorkflowAdapter`가 준비 결과와 mock execution receipt를 만든다.
- 이후 Veo 계열 provider를 붙일 때는 adapter만 교체하면 된다.

## 6. 저장과 추적

- 준비 결과는 `VideoAsset`에 저장한다.
- 준비/실행 모두 `Job` 로그를 남긴다.
- 준비 결과 zip과 실행 receipt는 로컬 storage 아래에 저장된다.
- `ProjectRevision`에는 번들 준비와 실행 snapshot이 각각 기록된다.

## 7. 다운로드

- 준비된 bundle은 `/api/videos/bundles/{video_asset_id}`에서 다운로드할 수 있다.
