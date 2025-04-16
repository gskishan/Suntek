import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { CalendarRange, Zap, TrendingUp, CheckCircle, AlertTriangle, DollarSign } from "lucide-react";

export type DateRangeType =
    | "today"
    | "yesterday"
    | "thisWeek"
    | "lastWeek"
    | "thisMonth"
    | "lastMonth"
    | "thisQuarter"
    | "lastQuarter"
    | "thisYear"
    | "lastYear"
    | "thisFY"
    | "lastFY"
    | "last30Days"
    | "last90Days"
    | "last365Days"
    | "allTime"
    | "custom"
    // Statistical presets
    | "completed"
    | "inProgress"
    | "largeCapacity"
    | "mediumCapacity"
    | "smallCapacity"
    | "draft"
    | "cancelled";

interface DateQuickFiltersProps {
    onSelect: (range: { from: Date | undefined; to: Date | undefined; type: DateRangeType }) => void;
    activeRange: DateRangeType;
    onLimitChange?: (limit: number | null) => void;
    onStatusChange?: (status: string) => void;
    onMultiStatusChange?: (statuses: string[]) => void;
    onMinCapacityChange?: (value: number | null) => void;
    onMaxCapacityChange?: (value: number | null) => void;
}

export function DateQuickFilters({
    onSelect,
    activeRange,
    onLimitChange,
    onStatusChange,
    onMultiStatusChange,
    onMinCapacityChange,
    onMaxCapacityChange,
}: DateQuickFiltersProps) {
    const handleRangeSelect = (rangeType: DateRangeType) => {
        const now = new Date();
        const today = new Date(now);
        today.setHours(0, 0, 0, 0);

        // Set end of day for the toDate
        let fromDate: Date | undefined;
        let toDate: Date | undefined = new Date(now);
        toDate.setHours(23, 59, 59, 999);

        // Reset all filters first to prevent previous filters from affecting new preset
        if (onStatusChange) onStatusChange("");
        if (onMultiStatusChange) onMultiStatusChange([]);
        if (onMinCapacityChange) onMinCapacityChange(null);
        if (onMaxCapacityChange) onMaxCapacityChange(null);
        if (onLimitChange) onLimitChange(100); // Default limit

        // For statistical presets, we need to handle other filters too
        if (rangeType === "completed") {
            // Completed orders - Completed status + No limit + No date range
            fromDate = undefined;
            toDate = undefined;
            if (onStatusChange) onStatusChange("Completed");
            // Set limit to "All items" for Completed Orders
            if (onLimitChange) {
                onLimitChange(null);
            }
            return onSelect({ from: fromDate, to: toDate, type: rangeType });
        } else if (rangeType === "inProgress") {
            // In progress orders - Set multiple in-progress statuses + No date range + No limit
            fromDate = undefined;
            toDate = undefined;
            // Use multiStatusChange if available, otherwise fallback to single status
            if (onMultiStatusChange) {
                onMultiStatusChange(["To Deliver and Bill", "To Deliver", "To Bill"]);
            } else if (onStatusChange) {
                // Fallback in case multi-select is not yet implemented
                onStatusChange("To Deliver and Bill");
            }
            if (onLimitChange) {
                onLimitChange(null);
            }
            return onSelect({ from: fromDate, to: toDate, type: rangeType });
        } else if (rangeType === "draft") {
            // Draft orders - Draft status + No date range + No limit
            fromDate = undefined;
            toDate = undefined;
            if (onStatusChange) onStatusChange("Draft");
            // Set limit to "All items" for Draft Orders
            if (onLimitChange) {
                onLimitChange(null);
            }
            return onSelect({ from: fromDate, to: toDate, type: rangeType });
        } else if (rangeType === "cancelled") {
            // Cancelled orders - Cancelled status + No date range + No limit
            fromDate = undefined;
            toDate = undefined;
            if (onStatusChange) onStatusChange("Cancelled");
            // Set limit to "All items" for Cancelled Orders
            if (onLimitChange) {
                onLimitChange(null);
            }
            return onSelect({ from: fromDate, to: toDate, type: rangeType });
        } else if (rangeType === "largeCapacity") {
            // Large capacity projects (>50kW) + No date range + No limit
            fromDate = undefined;
            toDate = undefined;
            if (onMinCapacityChange) onMinCapacityChange(50);
            if (onMaxCapacityChange) onMaxCapacityChange(null);
            if (onLimitChange) {
                onLimitChange(null);
            }
            return onSelect({ from: fromDate, to: toDate, type: rangeType });
        } else if (rangeType === "mediumCapacity") {
            // Medium capacity projects (10-50kW) + No date range + No limit
            fromDate = undefined;
            toDate = undefined;
            if (onMinCapacityChange) onMinCapacityChange(10);
            if (onMaxCapacityChange) onMaxCapacityChange(50);
            if (onLimitChange) {
                onLimitChange(null);
            }
            return onSelect({ from: fromDate, to: toDate, type: rangeType });
        } else if (rangeType === "smallCapacity") {
            // Small capacity projects (<10kW) + No date range + No limit
            fromDate = undefined;
            toDate = undefined;
            if (onMinCapacityChange) onMinCapacityChange(0);
            if (onMaxCapacityChange) onMaxCapacityChange(10);
            if (onLimitChange) {
                onLimitChange(null);
            }
            return onSelect({ from: fromDate, to: toDate, type: rangeType });
        }

        // Original date presets
        else if (rangeType === "today") {
            fromDate = new Date(today);
        } else if (rangeType === "yesterday") {
            fromDate = new Date(today);
            fromDate.setDate(fromDate.getDate() - 1);
            toDate = new Date(fromDate);
            toDate.setHours(23, 59, 59, 999);
        } else if (rangeType === "thisWeek") {
            fromDate = new Date(today);
            const dayOfWeek = fromDate.getDay(); // 0 is Sunday, 1 is Monday, etc.
            const diff = fromDate.getDate() - dayOfWeek + (dayOfWeek === 0 ? -6 : 1); // Adjust to get Monday
            fromDate.setDate(diff);
        } else if (rangeType === "lastWeek") {
            // Last week: Monday to Sunday of previous week
            const thisMonday = new Date(today);
            const dayOfWeek = thisMonday.getDay();
            const diffToMonday = dayOfWeek === 0 ? -6 : 1 - dayOfWeek; // Calculate days to last Monday
            thisMonday.setDate(thisMonday.getDate() + diffToMonday);

            fromDate = new Date(thisMonday);
            fromDate.setDate(fromDate.getDate() - 7); // Go back 7 days to get last Monday

            toDate = new Date(fromDate);
            toDate.setDate(toDate.getDate() + 6); // Last Sunday is 6 days after last Monday
            toDate.setHours(23, 59, 59, 999);
        } else if (rangeType === "thisMonth") {
            fromDate = new Date(today.getFullYear(), today.getMonth(), 1);
        } else if (rangeType === "lastMonth") {
            // Last month: 1st to last day of previous month
            const lastMonth = new Date(today.getFullYear(), today.getMonth() - 1, 1);
            fromDate = new Date(lastMonth);

            // Last day of last month
            toDate = new Date(today.getFullYear(), today.getMonth(), 0);
            toDate.setHours(23, 59, 59, 999);
        } else if (rangeType === "thisQuarter") {
            const quarter = Math.floor(today.getMonth() / 3);
            fromDate = new Date(today.getFullYear(), quarter * 3, 1);
        } else if (rangeType === "lastQuarter") {
            const currentQuarter = Math.floor(today.getMonth() / 3);
            const lastQuarterStartMonth = ((currentQuarter - 1 + 4) % 4) * 3; // Ensure positive with modulo
            const lastQuarterYear = currentQuarter === 0 ? today.getFullYear() - 1 : today.getFullYear();

            fromDate = new Date(lastQuarterYear, lastQuarterStartMonth, 1);
            toDate = new Date(fromDate.getFullYear(), fromDate.getMonth() + 3, 0);
            toDate.setHours(23, 59, 59, 999);
        } else if (rangeType === "thisYear") {
            fromDate = new Date(today.getFullYear(), 0, 1);
        } else if (rangeType === "lastYear") {
            fromDate = new Date(today.getFullYear() - 1, 0, 1);
            toDate = new Date(today.getFullYear() - 1, 11, 31);
            toDate.setHours(23, 59, 59, 999);
        } else if (rangeType === "thisFY") {
            // Fiscal year April to March
            const month = today.getMonth();
            const year = today.getFullYear();

            if (month >= 3) {
                // April onwards is the new fiscal year
                fromDate = new Date(year, 3, 1);
            } else {
                fromDate = new Date(year - 1, 3, 1);
            }
        } else if (rangeType === "lastFY") {
            const month = today.getMonth();
            const year = today.getFullYear();

            if (month >= 3) {
                // Current FY started in April of this year, so last FY was April last year to March this year
                fromDate = new Date(year - 1, 3, 1);
                toDate = new Date(year, 2, 31);
            } else {
                // Current FY started in April of last year, so last FY was April two years ago to March last year
                fromDate = new Date(year - 2, 3, 1);
                toDate = new Date(year - 1, 2, 31);
            }
            toDate.setHours(23, 59, 59, 999);
        } else if (rangeType === "last30Days") {
            fromDate = new Date(today);
            fromDate.setDate(today.getDate() - 30);
        } else if (rangeType === "last90Days") {
            fromDate = new Date(today);
            fromDate.setDate(today.getDate() - 90);
        } else if (rangeType === "last365Days") {
            fromDate = new Date(today);
            fromDate.setDate(today.getDate() - 365);
        } else if (rangeType === "allTime") {
            fromDate = undefined;
            toDate = undefined;

            // Set limit to "All items" when All Time is selected
            if (onLimitChange) {
                onLimitChange(null);
            }
        } else if (rangeType === "custom") {
            // Keep existing date range but mark as custom
            return onSelect({
                from: undefined,
                to: undefined,
                type: rangeType,
            });
        }

        onSelect({ from: fromDate, to: toDate, type: rangeType });
    };

    // Date presets
    const dateFilters: { label: string; value: DateRangeType; icon: React.ReactNode }[] = [
        { label: "Today", value: "today", icon: <CalendarRange className="h-3 w-3 mr-1" /> },
        { label: "Yesterday", value: "yesterday", icon: <CalendarRange className="h-3 w-3 mr-1" /> },
        { label: "This Week", value: "thisWeek", icon: <CalendarRange className="h-3 w-3 mr-1" /> },
        { label: "This Month", value: "thisMonth", icon: <CalendarRange className="h-3 w-3 mr-1" /> },
        { label: "Last 30 Days", value: "last30Days", icon: <CalendarRange className="h-3 w-3 mr-1" /> },
        { label: "All Time", value: "allTime", icon: <CalendarRange className="h-3 w-3 mr-1" /> },
    ];

    // More date options
    const moreDateFilters: { label: string; value: DateRangeType; icon: React.ReactNode }[] = [
        { label: "Last Week", value: "lastWeek", icon: <CalendarRange className="h-3 w-3 mr-1" /> },
        { label: "Last Month", value: "lastMonth", icon: <CalendarRange className="h-3 w-3 mr-1" /> },
        { label: "This Quarter", value: "thisQuarter", icon: <CalendarRange className="h-3 w-3 mr-1" /> },
        { label: "Last Quarter", value: "lastQuarter", icon: <CalendarRange className="h-3 w-3 mr-1" /> },
        { label: "This Year", value: "thisYear", icon: <CalendarRange className="h-3 w-3 mr-1" /> },
        { label: "Last Year", value: "lastYear", icon: <CalendarRange className="h-3 w-3 mr-1" /> },
        { label: "This FY", value: "thisFY", icon: <CalendarRange className="h-3 w-3 mr-1" /> },
        { label: "Last FY", value: "lastFY", icon: <CalendarRange className="h-3 w-3 mr-1" /> },
        { label: "Last 90 Days", value: "last90Days", icon: <CalendarRange className="h-3 w-3 mr-1" /> },
        { label: "Last 365 Days", value: "last365Days", icon: <CalendarRange className="h-3 w-3 mr-1" /> },
    ];

    // Statistical presets
    const statFilters: { label: string; value: DateRangeType; icon: React.ReactNode }[] = [
        { label: "Completed Orders", value: "completed", icon: <CheckCircle className="h-3 w-3 mr-1" /> },
        { label: "In Progress Orders", value: "inProgress", icon: <AlertTriangle className="h-3 w-3 mr-1" /> },
        { label: "Draft Orders", value: "draft", icon: <AlertTriangle className="h-3 w-3 mr-1" /> },
        { label: "Cancelled Orders", value: "cancelled", icon: <AlertTriangle className="h-3 w-3 mr-1" /> },
        { label: "Large Capacity (>50kW)", value: "largeCapacity", icon: <Zap className="h-3 w-3 mr-1" /> },
        { label: "Medium Capacity (10-50kW)", value: "mediumCapacity", icon: <Zap className="h-3 w-3 mr-1" /> },
        { label: "Small Capacity (<10kW)", value: "smallCapacity", icon: <Zap className="h-3 w-3 mr-1" /> },
    ];

    // Start with Less view by default
    const [showLess, setShowLess] = useState(true);

    return (
        <div className="rounded-lg border border-slate-200">
            <div className="px-3 py-2 bg-gradient-to-r from-slate-50 to-slate-100 border-b border-slate-200">
                <div className="flex items-center justify-between">
                    <div className="flex items-center">
                        <CalendarRange className="h-4 w-4 text-primary mr-1.5" />
                        <h3 className="text-sm font-medium text-slate-700">Presets</h3>
                    </div>
                    <Button
                        size="sm"
                        variant="ghost"
                        className="text-xs h-7 text-slate-600 hover:text-primary px-2 py-0"
                        onClick={() => setShowLess(!showLess)}
                    >
                        {showLess ? "More..." : "Less"}
                    </Button>
                </div>
            </div>
            <div className="p-3 bg-white">
                {/* Date Presets Section */}
                <div className="mb-3">
                    <div className="text-xs text-slate-500 font-medium mb-1.5">Common Date Filters</div>
                    <div className="flex flex-wrap gap-1.5">
                        {dateFilters.map((filter) => (
                            <Button
                                key={filter.value}
                                variant={activeRange === filter.value ? "default" : "outline"}
                                size="sm"
                                className={`text-xs h-7 ${
                                    activeRange === filter.value
                                        ? "bg-primary hover:bg-primary/90"
                                        : "bg-white hover:bg-slate-50 border-slate-200 text-slate-700"
                                }`}
                                onClick={() => handleRangeSelect(filter.value)}
                            >
                                {filter.icon}
                                {filter.label}
                                {activeRange === filter.value && (
                                    <span className="ml-1 h-1.5 w-1.5 rounded-full bg-white inline-block"></span>
                                )}
                            </Button>
                        ))}
                    </div>
                </div>

                {!showLess && (
                    <>
                        {/* Stats Presets Section */}
                        <div className="mb-3">
                            <div className="text-xs text-slate-500 font-medium mb-1.5">Statistical Presets</div>
                            <div className="flex flex-wrap gap-1.5">
                                {statFilters.map((filter) => (
                                    <Button
                                        key={filter.value}
                                        variant={activeRange === filter.value ? "default" : "outline"}
                                        size="sm"
                                        className={`text-xs h-7 ${
                                            activeRange === filter.value
                                                ? "bg-primary hover:bg-primary/90"
                                                : "bg-white hover:bg-slate-50 border-slate-200 text-slate-700"
                                        }`}
                                        onClick={() => handleRangeSelect(filter.value)}
                                    >
                                        {filter.icon}
                                        {filter.label}
                                        {activeRange === filter.value && (
                                            <span className="ml-1 h-1.5 w-1.5 rounded-full bg-white inline-block"></span>
                                        )}
                                    </Button>
                                ))}
                            </div>
                        </div>

                        {/* More Date Filters Section */}
                        <div>
                            <div className="text-xs text-slate-500 font-medium mb-1.5">More Date Ranges</div>
                            <div className="flex flex-wrap gap-1.5">
                                {moreDateFilters.map((filter) => (
                                    <Button
                                        key={filter.value}
                                        variant={activeRange === filter.value ? "default" : "outline"}
                                        size="sm"
                                        className={`text-xs h-7 ${
                                            activeRange === filter.value
                                                ? "bg-primary hover:bg-primary/90"
                                                : "bg-white hover:bg-slate-50 border-slate-200 text-slate-700"
                                        }`}
                                        onClick={() => handleRangeSelect(filter.value)}
                                    >
                                        {filter.icon}
                                        {filter.label}
                                        {activeRange === filter.value && (
                                            <span className="ml-1 h-1.5 w-1.5 rounded-full bg-white inline-block"></span>
                                        )}
                                    </Button>
                                ))}
                            </div>
                        </div>
                    </>
                )}
            </div>
        </div>
    );
}
