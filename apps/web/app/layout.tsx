import type { Metadata } from "next";

import { PageShell } from "@/components/layout/page-shell";
import { Providers } from "@/app/providers";
import "./globals.css";


export const metadata: Metadata = {
  title: "팩트 기반 AI 콘텐츠 스튜디오",
  description: "경제·금융·지정학 콘텐츠 생성을 위한 한국어 대시보드"
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="ko">
      <body>
        <Providers>
          <PageShell>{children}</PageShell>
        </Providers>
      </body>
    </html>
  );
}

