import { DatePicker } from "./ui/date-picker";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { useState, useMemo, useEffect } from "react";
import {
    ChevronLeft,
    SlidersHorizontal,
    MapPin,
    Users,
    Tag,
    Package,
    Hash,
    Zap,
    ChevronDown,
    ChevronRight,
    CalendarRange,
    X,
    Loader2,
} from "lucide-react";
import { MultiSelect } from "./ui/multi-select";
import { DateRange } from "react-day-picker";
import { Input } from "@/components/ui/input";
import { DateQuickFilters, DateRangeType } from "./DateQuickFilters";
import { Badge } from "@/components/ui/badge";

interface FilterSectionProps {
    title: string;
    icon: React.ReactNode;
    children: React.ReactNode;
    isOpen: boolean;
    toggleOpen: () => void;
    badgeCount?: number;
    onReset?: () => void;
    showReset?: boolean;
}

const FilterSection = ({
    title,
    icon,
    children,
    isOpen,
    toggleOpen,
    badgeCount = 0,
    onReset,
    showReset = false,
}: FilterSectionProps) => {
    return (
        <div className="border border-slate-200 rounded-md overflow-hidden shadow-sm">
            <div
                className="flex items-center justify-between p-3 bg-slate-50 cursor-pointer hover:bg-slate-100 transition-colors"
                onClick={toggleOpen}
            >
                <div className="flex items-center">
                    {icon}
                    <h3 className="text-sm font-medium text-slate-700 ml-1.5">{title}</h3>
                    {badgeCount > 0 && (
                        <Badge
                            className="ml-2 bg-primary text-xs py-0 h-5 px-1.5"
                            variant="default"
                        >
                            {badgeCount}
                        </Badge>
                    )}
                </div>
                <div className="flex items-center gap-1">
                    {showReset && badgeCount > 0 && (
                        <button
                            className="p-1 rounded-sm hover:bg-slate-200 transition-colors"
                            onClick={(e) => {
                                e.stopPropagation();
                                if (onReset) onReset();
                            }}
                        >
                            <X className="h-3.5 w-3.5 text-slate-500" />
                        </button>
                    )}
                    {isOpen ? (
                        <ChevronDown className="h-4 w-4 text-slate-500" />
                    ) : (
                        <ChevronRight className="h-4 w-4 text-slate-500" />
                    )}
                </div>
            </div>
            {isOpen && <div className="p-3 bg-white">{children}</div>}
        </div>
    );
};

interface DashboardFiltersProps {
    selectedStates: string[];
    selectedTerritories: string[];
    selectedCities: string[];
    selectedDistricts: string[];
    selectedDepartment: string;
    salesOrderStatus: string;
    salesOrderStatuses?: string[];
    selectedTypeOfCase: string;
    selectedTypeOfStructure: string;
    selectedSalesPersons: string[];
    fromDate: Date | undefined;
    toDate: Date | undefined;
    dateRangeType: DateRangeType;
    limit: number | null;
    minCapacity: number | null;
    maxCapacity: number | null;
    states: Array<{ name: string; creation: string; state: string }>;
    territories: Array<{ name: string; creation: string }>;
    cities: Array<{ name: string; creation: string; city: string }>;
    districts: Array<{ name: string; creation: string; district: string }>;
    departments: Array<{ name: string; creation: string }>;
    salesPersons: Array<{ name: string; sales_person_name: string }>;
    onStateChange: (values: string[]) => void;
    onTerritoryChange: (values: string[]) => void;
    onCityChange: (values: string[]) => void;
    onDistrictChange: (values: string[]) => void;
    onDepartmentChange: (value: string) => void;
    onStatusChange: (value: string) => void;
    onMultiStatusChange?: (values: string[]) => void;
    onTypeOfCaseChange: (value: string) => void;
    onTypeOfStructureChange: (value: string) => void;
    onSalesPersonChange: (values: string[]) => void;
    onLimitChange: (limit: number | null) => void;
    onFromDateChange: (date: Date | undefined) => void;
    onToDateChange: (date: Date | undefined) => void;
    onDateRangeChange: (range: { from: Date | undefined; to: Date | undefined; type: DateRangeType }) => void;
    onMinCapacityChange: (value: number | null) => void;
    onMaxCapacityChange: (value: number | null) => void;
    onApplyFilters: () => void;
    onClearFilters: () => void;
    dateRange: DateRange;
    search: string;
}

export const DashboardFilters = ({
    selectedStates,
    selectedTerritories,
    selectedCities,
    selectedDistricts,
    selectedDepartment,
    salesOrderStatus,
    salesOrderStatuses = [],
    selectedTypeOfCase,
    selectedTypeOfStructure,
    selectedSalesPersons,
    fromDate,
    toDate,
    dateRangeType,
    limit,
    minCapacity,
    maxCapacity,
    states,
    territories,
    cities,
    districts,
    departments,
    salesPersons,
    onStateChange,
    onTerritoryChange,
    onCityChange,
    onDistrictChange,
    onDepartmentChange,
    onStatusChange,
    onMultiStatusChange,
    onTypeOfCaseChange,
    onTypeOfStructureChange,
    onSalesPersonChange,
    onLimitChange,
    onFromDateChange,
    onToDateChange,
    onDateRangeChange,
    onMinCapacityChange,
    onMaxCapacityChange,
    onApplyFilters,
    onClearFilters,
}: DashboardFiltersProps) => {
    const [isExpanded, setIsExpanded] = useState(false);
    const [isLoading, setIsLoading] = useState(false);

    // Section open/close states
    const [dateFilterOpen, setDateFilterOpen] = useState(false);
    const [locationFilterOpen, setLocationFilterOpen] = useState(false);
    const [classificationFilterOpen, setClassificationFilterOpen] = useState(false);
    const [salesTeamFilterOpen, setSalesTeamFilterOpen] = useState(false);
    const [additionalFilterOpen, setAdditionalFilterOpen] = useState(false);

    const toggleExpand = () => {
        setIsExpanded(!isExpanded);
    };

    // Check if any filters are applied
    const filtersApplied = useMemo(() => {
        return (
            selectedStates.length > 0 ||
            selectedTerritories.length > 0 ||
            selectedCities.length > 0 ||
            selectedDistricts.length > 0 ||
            selectedDepartment !== "all" ||
            salesOrderStatus !== "all" ||
            selectedTypeOfCase !== "all" ||
            selectedTypeOfStructure !== "all" ||
            selectedSalesPersons.length > 0 ||
            limit !== 100 ||
            fromDate !== undefined ||
            toDate !== undefined ||
            minCapacity !== null ||
            maxCapacity !== null
        );
    }, [
        selectedStates,
        selectedTerritories,
        selectedCities,
        selectedDistricts,
        selectedDepartment,
        salesOrderStatus,
        selectedTypeOfCase,
        selectedTypeOfStructure,
        selectedSalesPersons,
        limit,
        fromDate,
        toDate,
        minCapacity,
        maxCapacity,
    ]);

    // Calculate badge counts for each section
    const dateBadgeCount = useMemo(() => {
        let count = 0;
        if (fromDate) count++;
        if (toDate) count++;
        if (dateRangeType !== "custom") count++;
        return count;
    }, [fromDate, toDate, dateRangeType]);

    const locationBadgeCount = useMemo(() => {
        let count = 0;
        count += selectedStates.length;
        count += selectedTerritories.length;
        count += selectedCities.length;
        count += selectedDistricts.length;
        return count;
    }, [selectedStates, selectedTerritories, selectedCities, selectedDistricts]);

    const statusesBadgeCount = useMemo(() => {
        if (salesOrderStatuses && salesOrderStatuses.length > 0) {
            return salesOrderStatuses.length;
        }
        return salesOrderStatus !== "all" ? 1 : 0;
    }, [salesOrderStatus, salesOrderStatuses]);

    const classificationBadgeCount = useMemo(() => {
        let count = 0;
        if (selectedDepartment !== "all") count++;
        count += statusesBadgeCount;
        if (selectedTypeOfCase !== "all") count++;
        if (selectedTypeOfStructure !== "all") count++;
        return count;
    }, [selectedDepartment, statusesBadgeCount, selectedTypeOfCase, selectedTypeOfStructure]);

    const salesTeamBadgeCount = useMemo(() => {
        return selectedSalesPersons.length;
    }, [selectedSalesPersons]);

    const additionalBadgeCount = useMemo(() => {
        let count = 0;
        if (limit !== 100) count++;
        if (minCapacity !== null) count++;
        if (maxCapacity !== null) count++;
        return count;
    }, [limit, minCapacity, maxCapacity]);

    // Get the filters applied label
    const getFiltersAppliedLabel = useMemo(() => {
        const filters = [];

        // Format date to DD/MM/YYYY
        const formatDate = (date: Date) => {
            const day = date.getDate().toString().padStart(2, "0");
            const month = (date.getMonth() + 1).toString().padStart(2, "0");
            const year = date.getFullYear();
            return `${day}/${month}/${year}`;
        };

        if (selectedStates.length > 0) {
            filters.push(`States: ${selectedStates.length}`);
        }
        if (selectedTerritories.length > 0) {
            filters.push(`Territories: ${selectedTerritories.length}`);
        }
        if (selectedCities.length > 0) {
            filters.push(`Cities: ${selectedCities.length}`);
        }
        if (selectedDistricts.length > 0) {
            filters.push(`Districts: ${selectedDistricts.length}`);
        }
        if (selectedDepartment !== "all") {
            filters.push(`Department: ${selectedDepartment}`);
        }
        if (salesOrderStatus !== "all") {
            filters.push(`Status: ${salesOrderStatus}`);
        }
        if (selectedTypeOfCase !== "all") {
            filters.push(`Type: ${selectedTypeOfCase}`);
        }
        if (selectedTypeOfStructure !== "all") {
            filters.push(`Structure: ${selectedTypeOfStructure}`);
        }
        if (selectedSalesPersons.length > 0) {
            filters.push(`Sales Persons: ${selectedSalesPersons.length}`);
        }
        if (limit !== 100) {
            filters.push(`Limit: ${limit}`);
        }
        if (fromDate) {
            filters.push(`From: ${formatDate(fromDate)}`);
        }
        if (toDate) {
            filters.push(`To: ${formatDate(toDate)}`);
        }
        if (minCapacity !== null) {
            filters.push(`Min Capacity: ${minCapacity} kW`);
        }
        if (maxCapacity !== null) {
            filters.push(`Max Capacity: ${maxCapacity} kW`);
        }

        return filters.length > 0 ? filters.join(", ") : "No filters applied";
    }, [
        selectedStates,
        selectedTerritories,
        selectedCities,
        selectedDistricts,
        selectedDepartment,
        salesOrderStatus,
        selectedTypeOfCase,
        selectedTypeOfStructure,
        selectedSalesPersons,
        limit,
        fromDate,
        toDate,
        minCapacity,
        maxCapacity,
    ]);

    // Auto-expand sections when they have filters applied
    useEffect(() => {
        if (dateBadgeCount > 0) {
            setDateFilterOpen(true);
        }
    }, [dateBadgeCount]);

    useEffect(() => {
        if (locationBadgeCount > 0) {
            setLocationFilterOpen(true);
        }
    }, [locationBadgeCount]);

    useEffect(() => {
        if (classificationBadgeCount > 0) {
            setClassificationFilterOpen(true);
        }
    }, [classificationBadgeCount]);

    useEffect(() => {
        if (salesTeamBadgeCount > 0) {
            setSalesTeamFilterOpen(true);
        }
    }, [salesTeamBadgeCount]);

    useEffect(() => {
        if (additionalBadgeCount > 0) {
            setAdditionalFilterOpen(true);
        }
    }, [additionalBadgeCount]);

    // Handle apply filters with loading state
    const handleApplyFilters = () => {
        setIsLoading(true);
        // Add timeout to simulate loading
        setTimeout(() => {
            onApplyFilters();
            setIsLoading(false);
        }, 400);
    };

    const handleClearFilters = () => {
        setIsLoading(true);
        setTimeout(() => {
            onClearFilters();
            setIsLoading(false);
        }, 400);
    };

    return (
        <Card
            className={`shadow-sm transition-all duration-300 ease-in-out ${isExpanded ? "h-[calc(88vh-100px)] w-[400px]" : "h-[50px] w-[50px] my-0 mt-0 rounded-md"}`}
        >
            <CardHeader
                className={`${isExpanded ? "px-4 py-3 flex flex-row items-center justify-between" : "p-0 flex items-center justify-center h-full"} cursor-pointer hover:bg-gray-50`}
                onClick={toggleExpand}
            >
                {isExpanded ? (
                    <>
                        <CardTitle className="text-lg font-semibold">Filters</CardTitle>
                        <ChevronLeft className="h-5 w-5" />
                    </>
                ) : (
                    <div className="flex flex-col items-center justify-center">
                        <SlidersHorizontal className="h-5 w-5 text-gray-600" />
                    </div>
                )}
            </CardHeader>
            {isExpanded && (
                <CardContent
                    className="space-y-4 pt-0 overflow-y-auto px-4"
                    style={{ maxHeight: "calc(88vh - 160px)" }}
                >
                    <div className="text-xs text-gray-500 italic mb-2 mt-2">
                        {filtersApplied ? (
                            <div className="bg-slate-100 p-2 rounded-md border border-slate-200">
                                <span className="font-medium">Filters Applied:</span> {getFiltersAppliedLabel}
                            </div>
                        ) : (
                            <div>No filters applied</div>
                        )}
                    </div>

                    {/* Date Quick Filters - Always visible */}
                    <div>
                        <DateQuickFilters
                            onSelect={onDateRangeChange}
                            activeRange={dateRangeType}
                            onLimitChange={onLimitChange}
                            onStatusChange={onStatusChange}
                            onMultiStatusChange={onMultiStatusChange}
                            onMinCapacityChange={onMinCapacityChange}
                            onMaxCapacityChange={onMaxCapacityChange}
                        />
                    </div>

                    <div className="flex flex-col space-y-3 mt-2">
                        {/* Date Range Section - Only date pickers */}
                        <FilterSection
                            title="Date Range Options"
                            icon={<CalendarRange className="h-4 w-4 text-slate-500" />}
                            isOpen={dateFilterOpen}
                            toggleOpen={() => setDateFilterOpen(!dateFilterOpen)}
                            badgeCount={dateBadgeCount}
                            onReset={() => {
                                onFromDateChange(undefined);
                                onToDateChange(undefined);
                                onDateRangeChange({
                                    from: undefined,
                                    to: undefined,
                                    type: "custom",
                                });
                            }}
                            showReset={true}
                        >
                            <div className="space-y-3">
                                <div className="grid grid-cols-2 gap-3">
                                    <DatePicker
                                        label="From Date"
                                        date={fromDate}
                                        setDate={onFromDateChange}
                                    />
                                    <DatePicker
                                        label="To Date"
                                        date={toDate}
                                        setDate={onToDateChange}
                                    />
                                </div>
                            </div>
                        </FilterSection>

                        {/* Location Filters Section */}
                        <FilterSection
                            title="Location"
                            icon={<MapPin className="h-4 w-4 text-slate-500" />}
                            isOpen={locationFilterOpen}
                            toggleOpen={() => setLocationFilterOpen(!locationFilterOpen)}
                            badgeCount={locationBadgeCount}
                            onReset={() => {
                                onStateChange([]);
                                onTerritoryChange([]);
                                onCityChange([]);
                                onDistrictChange([]);
                            }}
                            showReset={true}
                        >
                            <div className="space-y-4">
                                <div className="grid grid-cols-2 gap-3">
                                    <div className="space-y-1 w-full">
                                        <label className="text-xs font-medium text-gray-600">States</label>
                                        <MultiSelect
                                            values={selectedStates}
                                            onValuesChange={(values: string[]) => {
                                                onStateChange(values);
                                            }}
                                            options={states.map((state) => ({
                                                value: state.name,
                                                label: state.state,
                                            }))}
                                            placeholder="Select States"
                                        />
                                    </div>

                                    <div className="space-y-1 w-full">
                                        <label className="text-xs font-medium text-gray-600">Territories</label>
                                        <MultiSelect
                                            values={selectedTerritories}
                                            onValuesChange={onTerritoryChange}
                                            options={territories.map((territory) => ({
                                                value: territory.name,
                                                label: territory.name,
                                            }))}
                                            placeholder="Select Territories"
                                        />
                                    </div>
                                </div>

                                <div className="grid grid-cols-2 gap-3">
                                    <div className="space-y-1 w-full">
                                        <label className="text-xs font-medium text-gray-600">Cities</label>
                                        <MultiSelect
                                            values={selectedCities}
                                            onValuesChange={onCityChange}
                                            options={cities.map((city) => ({
                                                value: city.name,
                                                label: city.city,
                                            }))}
                                            placeholder="Select Cities"
                                        />
                                    </div>

                                    <div className="space-y-1 w-full">
                                        <label className="text-xs font-medium text-gray-600">Districts</label>
                                        <MultiSelect
                                            values={selectedDistricts}
                                            onValuesChange={onDistrictChange}
                                            options={districts.map((district) => ({
                                                value: district.name,
                                                label: district.district,
                                            }))}
                                            placeholder="Select Districts"
                                        />
                                    </div>
                                </div>
                            </div>
                        </FilterSection>

                        {/* Classification Filters Section */}
                        <FilterSection
                            title="Classification"
                            icon={<Tag className="h-4 w-4 text-slate-500" />}
                            isOpen={classificationFilterOpen}
                            toggleOpen={() => setClassificationFilterOpen(!classificationFilterOpen)}
                            badgeCount={classificationBadgeCount}
                            onReset={() => {
                                onDepartmentChange("all");
                                onStatusChange("all");
                                onTypeOfCaseChange("all");
                                onTypeOfStructureChange("all");
                            }}
                            showReset={true}
                        >
                            <div className="space-y-4">
                                <div className="grid grid-cols-2 gap-3">
                                    <div className="space-y-1 w-full">
                                        <label className="text-xs font-medium text-gray-600">Department</label>
                                        <Select
                                            value={selectedDepartment}
                                            onValueChange={onDepartmentChange}
                                        >
                                            <SelectTrigger className="w-full h-9">
                                                <SelectValue placeholder="Select Department" />
                                            </SelectTrigger>
                                            <SelectContent>
                                                <SelectItem value="all">All Departments</SelectItem>
                                                {departments?.map((department) => (
                                                    <SelectItem
                                                        key={department.creation}
                                                        value={department.name}
                                                    >
                                                        {department.name}
                                                    </SelectItem>
                                                ))}
                                            </SelectContent>
                                        </Select>
                                    </div>

                                    <div className="space-y-1 w-full">
                                        <label className="text-xs font-medium text-gray-600">Status</label>
                                        {onMultiStatusChange ? (
                                            <MultiSelect
                                                values={salesOrderStatuses || []}
                                                onValuesChange={onMultiStatusChange}
                                                options={[
                                                    { value: "Draft", label: "Draft" },
                                                    { value: "On Hold", label: "On Hold" },
                                                    { value: "To Deliver and Bill", label: "To Deliver and Bill" },
                                                    { value: "To Bill", label: "To Bill" },
                                                    { value: "To Deliver", label: "To Deliver" },
                                                    { value: "Completed", label: "Completed" },
                                                    { value: "Cancelled", label: "Cancelled" },
                                                    { value: "Closed", label: "Closed" },
                                                ]}
                                                placeholder="Select Statuses"
                                            />
                                        ) : (
                                            <Select
                                                value={salesOrderStatus}
                                                onValueChange={onStatusChange}
                                            >
                                                <SelectTrigger className="w-full h-9">
                                                    <SelectValue placeholder="Select Status" />
                                                </SelectTrigger>
                                                <SelectContent>
                                                    <SelectItem value="all">All Statuses</SelectItem>
                                                    <SelectItem value="Draft">Draft</SelectItem>
                                                    <SelectItem value="On Hold">On Hold</SelectItem>
                                                    <SelectItem value="To Deliver and Bill">
                                                        To Deliver and Bill
                                                    </SelectItem>
                                                    <SelectItem value="To Bill">To Bill</SelectItem>
                                                    <SelectItem value="To Deliver">To Deliver</SelectItem>
                                                    <SelectItem value="Completed">Completed</SelectItem>
                                                    <SelectItem value="Cancelled">Cancelled</SelectItem>
                                                    <SelectItem value="Closed">Closed</SelectItem>
                                                </SelectContent>
                                            </Select>
                                        )}
                                    </div>
                                </div>

                                <div className="grid grid-cols-2 gap-3">
                                    <div className="space-y-1 w-full">
                                        <label className="text-xs font-medium text-gray-600">Type of Case</label>
                                        <Select
                                            value={selectedTypeOfCase}
                                            onValueChange={onTypeOfCaseChange}
                                        >
                                            <SelectTrigger className="w-full h-9">
                                                <SelectValue placeholder="Select Type of Case" />
                                            </SelectTrigger>
                                            <SelectContent>
                                                <SelectItem value="all">All Types</SelectItem>
                                                <SelectItem value="Subsidy">Subsidy</SelectItem>
                                                <SelectItem value="Non Subsidy">Non Subsidy</SelectItem>
                                                <SelectItem value="No Subsidy No Discom">
                                                    No Subsidy No Discom
                                                </SelectItem>
                                            </SelectContent>
                                        </Select>
                                    </div>

                                    <div className="space-y-1 w-full">
                                        <label className="text-xs font-medium text-gray-600">Type of Structure</label>
                                        <Select
                                            value={selectedTypeOfStructure}
                                            onValueChange={onTypeOfStructureChange}
                                        >
                                            <SelectTrigger className="w-full h-9">
                                                <SelectValue placeholder="Select Type of Structure" />
                                            </SelectTrigger>
                                            <SelectContent>
                                                <SelectItem value="all">All Structures</SelectItem>
                                                <SelectItem value="Customized">Customized</SelectItem>
                                                <SelectItem value="Shed">Shed</SelectItem>
                                                <SelectItem value="Elevated">Elevated</SelectItem>
                                                <SelectItem value="On Shed">On Shed</SelectItem>
                                                <SelectItem value="On Shed Aluminium Triangle">
                                                    On Shed Aluminium Triangle
                                                </SelectItem>
                                                <SelectItem value="Onsite Fabrication">Onsite Fabrication</SelectItem>
                                                <SelectItem value="Others">Others</SelectItem>
                                                <SelectItem value="Regular Structure">Regular Structure</SelectItem>
                                                <SelectItem value="RCC">RCC</SelectItem>
                                            </SelectContent>
                                        </Select>
                                    </div>
                                </div>
                            </div>
                        </FilterSection>

                        {/* Sales Persons Section */}
                        <FilterSection
                            title="Sales Team"
                            icon={<Users className="h-4 w-4 text-slate-500" />}
                            isOpen={salesTeamFilterOpen}
                            toggleOpen={() => setSalesTeamFilterOpen(!salesTeamFilterOpen)}
                            badgeCount={salesTeamBadgeCount}
                            onReset={() => {
                                onSalesPersonChange([]);
                            }}
                            showReset={true}
                        >
                            <div className="space-y-2">
                                <div className="space-y-1 w-full">
                                    <label className="text-xs font-medium text-gray-600">Sales Persons</label>
                                    <MultiSelect
                                        values={selectedSalesPersons}
                                        onValuesChange={onSalesPersonChange}
                                        options={salesPersons.map((person) => ({
                                            value: person.name,
                                            label: person.sales_person_name || person.name,
                                        }))}
                                        placeholder="Select Sales Persons"
                                    />
                                </div>
                            </div>
                        </FilterSection>

                        {/* Additional Filters Section */}
                        <FilterSection
                            title="Additional Filters"
                            icon={<Package className="h-4 w-4 text-slate-500" />}
                            isOpen={additionalFilterOpen}
                            toggleOpen={() => setAdditionalFilterOpen(!additionalFilterOpen)}
                            badgeCount={additionalBadgeCount}
                            onReset={() => {
                                onLimitChange(100);
                                onMinCapacityChange(null);
                                onMaxCapacityChange(null);
                            }}
                            showReset={true}
                        >
                            <div className="space-y-4">
                                <div className="space-y-1 w-full">
                                    <div className="flex items-center mb-1">
                                        <Hash className="h-3.5 w-3.5 text-slate-500 mr-1" />
                                        <label className="text-xs font-medium text-gray-600">Results Limit</label>
                                    </div>
                                    <Select
                                        value={limit === null ? "all" : limit.toString()}
                                        onValueChange={(value) =>
                                            onLimitChange(value === "all" ? null : parseInt(value))
                                        }
                                    >
                                        <SelectTrigger className="w-full h-8 text-sm bg-white">
                                            <SelectValue placeholder="Select Limit" />
                                        </SelectTrigger>
                                        <SelectContent>
                                            <SelectItem value="all">All items</SelectItem>
                                            <SelectItem value="50">50 items</SelectItem>
                                            <SelectItem value="100">100 items</SelectItem>
                                            <SelectItem value="200">200 items</SelectItem>
                                            <SelectItem value="500">500 items</SelectItem>
                                            <SelectItem value="1000">1000 items</SelectItem>
                                        </SelectContent>
                                    </Select>
                                </div>

                                {/* Capacity Range */}
                                <div className="space-y-2">
                                    <div className="flex items-center mb-1">
                                        <Zap className="h-3.5 w-3.5 text-slate-500 mr-1" />
                                        <label className="text-xs font-medium text-gray-600">Capacity Range</label>
                                    </div>
                                    <div className="grid grid-cols-2 gap-3">
                                        <div className="space-y-1 w-full">
                                            <label className="text-xs font-medium text-gray-500">
                                                Min Capacity (kW)
                                            </label>
                                            <Input
                                                type="number"
                                                placeholder="Min capacity"
                                                value={minCapacity === null ? "" : minCapacity}
                                                onChange={(e) => {
                                                    const value = e.target.value;
                                                    onMinCapacityChange(value === "" ? null : parseFloat(value));
                                                }}
                                                className="h-8 text-sm bg-white"
                                            />
                                        </div>
                                        <div className="space-y-1 w-full">
                                            <label className="text-xs font-medium text-gray-500">
                                                Max Capacity (kW)
                                            </label>
                                            <Input
                                                type="number"
                                                placeholder="Max capacity"
                                                value={maxCapacity === null ? "" : maxCapacity}
                                                onChange={(e) => {
                                                    const value = e.target.value;
                                                    onMaxCapacityChange(value === "" ? null : parseFloat(value));
                                                }}
                                                className="h-8 text-sm bg-white"
                                            />
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </FilterSection>
                    </div>

                    <div className="flex justify-end pt-4 pb-2 gap-2">
                        {filtersApplied && (
                            <Button
                                variant="outline"
                                onClick={handleClearFilters}
                                className="px-4 py-2 text-sm"
                                disabled={isLoading}
                            >
                                {isLoading ? <Loader2 className="h-4 w-4 animate-spin" /> : "Clear Filters"}
                            </Button>
                        )}
                        <Button
                            onClick={handleApplyFilters}
                            className="px-4 py-2 cursor-pointer text-sm"
                            disabled={isLoading}
                        >
                            {isLoading ? (
                                <>
                                    <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                                    Applying...
                                </>
                            ) : (
                                "Apply Filters"
                            )}
                        </Button>
                    </div>
                </CardContent>
            )}
        </Card>
    );
};
