import { Tooltip, TooltipContent, TooltipTrigger } from "@/components/ui/tooltip";
import { TableCellMetricProps } from "./types";

export const TableCellMetric = ({ icon: Icon, value, tooltip }: TableCellMetricProps) => {
    return (
        <Tooltip>
            <TooltipTrigger asChild>
                <div className="inline-flex items-center justify-center w-full">
                    <Icon className="h-4 w-4 mr-1.5 flex-shrink-0" />
                    <span className="text-center">{value !== undefined && value !== null ? value : 0}</span>
                </div>
            </TooltipTrigger>
            <TooltipContent
                side="top"
                align="center"
                sideOffset={5}
            >
                <p>{tooltip}</p>
            </TooltipContent>
        </Tooltip>
    );
};
