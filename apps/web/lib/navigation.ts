import {
  Activity,
  Bot,
  Camera,
  ChartColumn,
  Clapperboard,
  Download,
  FileText,
  FolderKanban,
  LayoutDashboard,
  Search,
  Settings,
  Sparkles
} from "lucide-react";


export const navigationItems = [
  { href: "/dashboard", label: "대시보드", icon: LayoutDashboard },
  { href: "/issues", label: "이슈 탐색", icon: Search },
  { href: "/statistics", label: "통계 검증", icon: ChartColumn },
  { href: "/market", label: "시장 데이터", icon: Activity },
  { href: "/snapshots", label: "차트 / 캡처", icon: Camera },
  { href: "/scripts", label: "대본 생성", icon: FileText },
  { href: "/character", label: "캐릭터 설정", icon: Bot },
  { href: "/images", label: "이미지 생성", icon: Sparkles },
  { href: "/videos", label: "영상 생성", icon: Clapperboard },
  { href: "/review", label: "검수 / 편집", icon: FolderKanban },
  { href: "/downloads", label: "다운로드", icon: Download },
  { href: "/settings", label: "설정", icon: Settings },
  { href: "/jobs", label: "작업 로그", icon: Activity }
] as const;

