import React, { useState } from "react";
import { cn } from "@/lib/utils";
import { BarChart3, Users, Calendar, Building, MapPin, ChevronDown } from "lucide-react";

type MainTabType = "sales" | "crm" | "activity";
type SalesSubTabType = "location" | "department";
type TabType = MainTabType | SalesSubTabType;

interface DashboardTabsProps {
    activeDashboard: TabType;
    onDashboardChange: (tab: TabType) => void;
}

export const DashboardTabs = ({ activeDashboard, onDashboardChange }: DashboardTabsProps) => {
    const [salesTabExpanded, setSalesTabExpanded] = useState(true);

    const isSalesTab = activeDashboard === "location" || activeDashboard === "department";
    const mainTab = isSalesTab ? "sales" : activeDashboard;

    return (
        <div className="flex flex-col gap-2">
            <div className="flex space-x-1 bg-background p-1 rounded-lg border w-fit">
                <TabButton
                    isActive={mainTab === "sales"}
                    onClick={() => {
                        if (mainTab !== "sales") {
                            onDashboardChange("location");
                            setSalesTabExpanded(true);
                        } else {
                            setSalesTabExpanded(!salesTabExpanded);
                        }
                    }}
                    icon={<BarChart3 className="h-4 w-4 mr-1" />}
                    hasSubMenu={true}
                    expanded={salesTabExpanded}
                >
                    Sales
                </TabButton>
                <TabButton
                    isActive={mainTab === "crm"}
                    onClick={() => onDashboardChange("crm")}
                    icon={<Users className="h-4 w-4 mr-1" />}
                >
                    CRM
                </TabButton>
                <TabButton
                    isActive={mainTab === "activity"}
                    onClick={() => onDashboardChange("activity")}
                    icon={<Calendar className="h-4 w-4 mr-1" />}
                >
                    Activity
                </TabButton>
            </div>

            {mainTab === "sales" && salesTabExpanded && (
                <div className="ml-8 flex space-x-1 bg-background p-1 rounded-lg border border-primary/20 w-fit">
                    <TabButton
                        isActive={activeDashboard === "location"}
                        onClick={() => onDashboardChange("location")}
                        icon={<MapPin className="h-4 w-4 mr-1" />}
                        isSubTab={true}
                    >
                        Sales by Location
                    </TabButton>
                    <TabButton
                        isActive={activeDashboard === "department"}
                        onClick={() => onDashboardChange("department")}
                        icon={<Building className="h-4 w-4 mr-1" />}
                        isSubTab={true}
                    >
                        Sales by Department
                    </TabButton>
                </div>
            )}
        </div>
    );
};

interface TabButtonProps {
    isActive: boolean;
    onClick: () => void;
    children: React.ReactNode;
    icon?: React.ReactNode;
    hasSubMenu?: boolean;
    expanded?: boolean;
    isSubTab?: boolean;
}

const TabButton = ({
    isActive,
    onClick,
    children,
    icon,
    hasSubMenu = false,
    expanded = false,
    isSubTab = false,
}: TabButtonProps) => {
    return (
        <button
            onClick={onClick}
            className={cn(
                "px-4 py-2 text-sm font-medium rounded-md flex items-center",
                isActive ? "bg-primary text-primary-foreground shadow-sm" : "text-muted-foreground hover:bg-muted/80",
                isSubTab && "text-xs py-1.5",
            )}
        >
            {icon}
            {children}
            {hasSubMenu && (
                <ChevronDown className={cn("h-4 w-4 ml-1 transition-transform", expanded && "transform rotate-180")} />
            )}
        </button>
    );
};
