import { LucideIcon } from "lucide-react";
import { Tooltip, TooltipContent, TooltipTrigger } from "@/components/ui/tooltip";

interface MetricProps {
    icon: LucideIcon;
    value: string | number;
    label: string;
    tooltip: string;
    className?: string;
}

export const MetricDisplay = ({ icon: Icon, value, label, tooltip, className = "" }: MetricProps) => {
    return (
        <Tooltip>
            <TooltipTrigger asChild>
                <div
                    className={`flex items-center text-sm text-gray-600 bg-white px-3 py-1 rounded-full shadow-sm ${className}`}
                >
                    <Icon className="h-4 w-4 mr-1.5" />
                    {label}: {value}
                </div>
            </TooltipTrigger>
            <TooltipContent>
                <p>{tooltip}</p>
            </TooltipContent>
        </Tooltip>
    );
};
