import { Badge } from "@/components/ui/badge";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";


type JobLog = {
  type: string;
  status: string;
  startedAt: string;
  note: string;
};

export function JobLogTable({ items }: { items: ReadonlyArray<JobLog> }) {
  return (
    <div className="overflow-hidden rounded-3xl border border-slate-200">
      <Table>
        <TableHead>
          <TableRow>
            <TableHeader>작업 유형</TableHeader>
            <TableHeader>상태</TableHeader>
            <TableHeader>시작 시각</TableHeader>
            <TableHeader>메모</TableHeader>
          </TableRow>
        </TableHead>
        <TableBody>
          {items.map((item) => (
            <TableRow key={`${item.type}-${item.startedAt}`}>
              <TableCell className="font-medium text-ink">{item.type}</TableCell>
              <TableCell>
                <Badge
                  tone={
                    item.status === "성공"
                      ? "success"
                      : item.status === "실행 중"
                        ? "warning"
                        : item.status === "실패"
                          ? "danger"
                          : "default"
                  }
                >
                  {item.status}
                </Badge>
              </TableCell>
              <TableCell>{item.startedAt}</TableCell>
              <TableCell>{item.note}</TableCell>
            </TableRow>
          ))}
        </TableBody>
      </Table>
    </div>
  );
}
