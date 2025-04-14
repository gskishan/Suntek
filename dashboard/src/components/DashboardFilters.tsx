import { DatePicker } from "./ui/date-picker";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { useState, useMemo } from "react";
import { ChevronLeft, SlidersHorizontal } from "lucide-react";
import { MultiSelect } from "./ui/multi-select";
import { DateRange } from "react-day-picker";

interface DashboardFiltersProps {
    selectedStates: string[];
    selectedTerritories: string[];
    selectedCities: string[];
    selectedDistricts: string[];
    selectedDepartment: string;
    salesOrderStatus: string;
    selectedTypeOfCase: string;
    fromDate: Date | undefined;
    toDate: Date | undefined;
    limit: number | null;
    states: Array<{ name: string; creation: string; state: string }>;
    territories: Array<{ name: string; creation: string }>;
    cities: Array<{ name: string; creation: string; city: string }>;
    districts: Array<{ name: string; creation: string; district: string }>;
    departments: Array<{ name: string; creation: string }>;
    onStateChange: (values: string[]) => void;
    onTerritoryChange: (values: string[]) => void;
    onCityChange: (values: string[]) => void;
    onDistrictChange: (values: string[]) => void;
    onDepartmentChange: (value: string) => void;
    onStatusChange: (value: string) => void;
    onTypeOfCaseChange: (value: string) => void;
    onLimitChange: (limit: number | null) => void;
    onFromDateChange: (date: Date | undefined) => void;
    onToDateChange: (date: Date | undefined) => void;
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
    selectedTypeOfCase,
    fromDate,
    toDate,
    limit,
    states,
    territories,
    cities,
    districts,
    departments,
    onStateChange,
    onTerritoryChange,
    onCityChange,
    onDistrictChange,
    onDepartmentChange,
    onStatusChange,
    onTypeOfCaseChange,
    onLimitChange,
    onFromDateChange,
    onToDateChange,
    onApplyFilters,
    onClearFilters,
}: DashboardFiltersProps) => {
    const [isExpanded, setIsExpanded] = useState(false);

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
            limit !== 100 ||
            fromDate !== undefined ||
            toDate !== undefined
        );
    }, [
        selectedStates,
        selectedTerritories,
        selectedCities,
        selectedDistricts,
        selectedDepartment,
        salesOrderStatus,
        selectedTypeOfCase,
        limit,
        fromDate,
        toDate,
    ]);

    return (
        <Card
            className={`shadow-sm transition-all duration-300 ease-in-out ${isExpanded ? "h-[calc(80vh-140px)] w-[400px]" : "h-[50px] w-[50px] my-0 mt-0 rounded-md"}`}
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
                    className="space-y-4 pt-0 overflow-y-auto"
                    style={{ maxHeight: "calc(80vh - 200px)" }}
                >
                    <div className="flex flex-col space-y-4">
                        {/* Location Filters Row - Two fields per row */}
                        <div className="grid grid-cols-2 gap-3">
                            <div className="space-y-1 w-full">
                                <label className="text-xs font-medium text-gray-700">States</label>
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
                                <label className="text-xs font-medium text-gray-700">Territories</label>
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

                            <div className="space-y-1 w-full">
                                <label className="text-xs font-medium text-gray-700">Cities</label>
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
                                <label className="text-xs font-medium text-gray-700">Districts</label>
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

                        {/* Status and Type Filters Row - Two fields per row */}
                        <div className="grid grid-cols-2 gap-3">
                            <div className="space-y-1 w-full">
                                <label className="text-xs font-medium text-gray-700">Department</label>
                                <Select
                                    value={selectedDepartment}
                                    onValueChange={onDepartmentChange}
                                >
                                    <SelectTrigger className="w-full h-9">
                                        <SelectValue placeholder="Select Department" />
                                    </SelectTrigger>
                                    <SelectContent className="max-h-[200px] overflow-y-auto">
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
                                <label className="text-xs font-medium text-gray-700">Status</label>
                                <Select
                                    value={salesOrderStatus}
                                    onValueChange={onStatusChange}
                                >
                                    <SelectTrigger className="w-full h-9">
                                        <SelectValue placeholder="Select Status" />
                                    </SelectTrigger>
                                    <SelectContent className="max-h-[200px] overflow-y-auto">
                                        <SelectItem value="all">All Statuses</SelectItem>
                                        <SelectItem value="Draft">Draft</SelectItem>
                                        <SelectItem value="On Hold">On Hold</SelectItem>
                                        <SelectItem value="To Deliver and Bill">To Deliver and Bill</SelectItem>
                                        <SelectItem value="To Bill">To Bill</SelectItem>
                                        <SelectItem value="To Deliver">To Deliver</SelectItem>
                                        <SelectItem value="Completed">Completed</SelectItem>
                                        <SelectItem value="Cancelled">Cancelled</SelectItem>
                                        <SelectItem value="Closed">Closed</SelectItem>
                                    </SelectContent>
                                </Select>
                            </div>

                            <div className="space-y-1 w-full">
                                <label className="text-xs font-medium text-gray-700">Type of Case</label>
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
                                        <SelectItem value="No Subsidy No Discom">No Subsidy No Discom</SelectItem>
                                    </SelectContent>
                                </Select>
                            </div>

                            <div className="space-y-1 w-full">
                                <label className="text-xs font-medium text-gray-700">Limit</label>
                                <Select
                                    value={limit === null ? "all" : limit.toString()}
                                    onValueChange={(value) => onLimitChange(value === "all" ? null : parseInt(value))}
                                >
                                    <SelectTrigger className="w-full h-9">
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
                        </div>

                        {/* Date Range Row - Two fields in one row */}
                        <div className="grid grid-cols-2 gap-3">
                            <div className="space-y-1 w-full">
                                <label className="text-xs font-medium text-gray-700">From Date</label>
                                <DatePicker
                                    label="From"
                                    date={fromDate}
                                    setDate={onFromDateChange}
                                />
                            </div>
                            <div className="space-y-1 w-full">
                                <label className="text-xs font-medium text-gray-700">To Date</label>
                                <DatePicker
                                    label="To"
                                    date={toDate}
                                    setDate={onToDateChange}
                                />
                            </div>
                        </div>
                    </div>

                    <div className="flex justify-end pt-2 gap-2">
                        {filtersApplied && (
                            <Button
                                variant="outline"
                                onClick={onClearFilters}
                                className="px-4 py-2"
                            >
                                Clear Filters
                            </Button>
                        )}
                        <Button
                            onClick={onApplyFilters}
                            className="px-4 py-2"
                        >
                            Apply Filters
                        </Button>
                    </div>
                </CardContent>
            )}
        </Card>
    );
};
