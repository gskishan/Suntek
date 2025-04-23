import React from "react";
import { TableCell } from "@/components/ui/table";
import { LucideIcon } from "lucide-react";

interface StatCellProps {
    icon: LucideIcon;
    value: React.ReactNode;
    width?: string;
    tooltip?: string;
}

export const StatCell: React.FC<StatCellProps> = ({ icon: Icon, value, width = "w-[120px]", tooltip }) => {
    return (
        <TableCell
            className={`${width} text-center`}
            style={{
                verticalAlign: "middle",
                padding: "8px",
                whiteSpace: "nowrap",
            }}
        >
            <div
                className="inline-flex items-center justify-center"
                style={{
                    width: "100%",
                    position: "relative",
                    lineHeight: "1.5",
                }}
                title={tooltip}
            >
                <Icon
                    className="h-4 w-4 mr-1.5"
                    style={{ flexShrink: 0 }}
                />
                <span style={{ display: "inline-block" }}>{value}</span>
            </div>
        </TableCell>
    );
};
