import { BarChart3, Users, Calendar } from "lucide-react";

type DashboardType = "sales" | "crm" | "activity";

interface DashboardTabsProps {
    activeDashboard: DashboardType;
    onDashboardChange: (dashboard: DashboardType) => void;
}

export const DashboardTabs = ({ activeDashboard, onDashboardChange }: DashboardTabsProps) => {
    return (
        <div className="border-b mb-6">
            <div className="flex space-x-1">
                <TabButton
                    isActive={activeDashboard === "sales"}
                    onClick={() => onDashboardChange("sales")}
                    icon={<BarChart3 className="h-4 w-4 mr-2" />}
                    label="Sales"
                />
                <TabButton
                    isActive={activeDashboard === "crm"}
                    onClick={() => onDashboardChange("crm")}
                    icon={<Users className="h-4 w-4 mr-2" />}
                    label="CRM"
                />
                <TabButton
                    isActive={activeDashboard === "activity"}
                    onClick={() => onDashboardChange("activity")}
                    icon={<Calendar className="h-4 w-4 mr-2" />}
                    label="Activity"
                />
            </div>
        </div>
    );
};

interface TabButtonProps {
    isActive: boolean;
    onClick: () => void;
    icon: React.ReactNode;
    label: string;
}

const TabButton = ({ isActive, onClick, icon, label }: TabButtonProps) => {
    return (
        <button
            onClick={onClick}
            className={`flex items-center px-4 py-2 border-b-2 font-medium text-sm transition-colors
        ${
            isActive
                ? "border-primary text-primary"
                : "border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300"
        }`}
        >
            {icon}
            {label}
        </button>
    );
};
