import { ChevronDown, ChevronRight } from "lucide-react";
import { MetricDisplay } from "./MetricsDisplay";
import { Package, DollarSign } from "lucide-react";

interface LocationItemProps {
    name: string;
    count: number;
    totalAmount: number;
    isExpanded: boolean;
    onToggle: () => void;
    level: "territory" | "state" | "district" | "city";
    className?: string;
}

export const LocationItem = ({
    name,
    count,
    totalAmount,
    isExpanded,
    onToggle,
    level,
    className = "",
}: LocationItemProps) => {
    const getLocationLabel = () => {
        switch (level) {
            case "territory":
                return "Territory";
            case "state":
                return "State";
            case "district":
                return "District";
            case "city":
                return "City";
        }
    };

    return (
        <button
            onClick={onToggle}
            className={`flex items-center justify-between w-full text-md font-medium text-gray-800 hover:bg-gray-50 p-3 rounded-lg transition-colors ${className}`}
        >
            <div className="flex items-center">
                {isExpanded ? (
                    <ChevronDown className="h-4 w-4 mr-2 text-gray-500" />
                ) : (
                    <ChevronRight className="h-4 w-4 mr-2 text-gray-500" />
                )}
                {name}
            </div>
            <div className="flex items-center space-x-4">
                <MetricDisplay
                    icon={Package}
                    value={count}
                    label="Orders"
                    tooltip={`Total number of orders in ${name}`}
                />
                <MetricDisplay
                    icon={DollarSign}
                    value={`₹${totalAmount.toLocaleString()}`}
                    label="Revenue"
                    tooltip={`Total revenue from all orders in ${name}`}
                />
            </div>
        </button>
    );
};
