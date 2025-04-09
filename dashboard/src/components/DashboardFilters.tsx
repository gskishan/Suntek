import { DatePicker } from "./ui/date-picker";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Separator } from "@/components/ui/separator";
import { Button } from "@/components/ui/button";
import { useState } from "react";
import { ChevronDown, ChevronUp } from "lucide-react";

interface DashboardFiltersProps {
    selectedState: string;
    selectedTerritory: string;
    selectedCity: string;
    selectedDistrict: string;
    selectedDepartment: string;
    salesOrderStatus: string;
    fromDate: Date | undefined;
    toDate: Date | undefined;
    states: Array<{ name: string; creation: string; state: string }>;
    territories: Array<{ name: string; creation: string }>;
    cities: Array<{ name: string; creation: string; city: string }>;
    districts: Array<{ name: string; creation: string; district: string }>;
    departments: Array<{ name: string; creation: string }>;
    onStateChange: (value: string) => void;
    onTerritoryChange: (value: string) => void;
    onCityChange: (value: string) => void;
    onDistrictChange: (value: string) => void;
    onDepartmentChange: (value: string) => void;
    onStatusChange: (value: string) => void;
    onFromDateChange: (date: Date | undefined) => void;
    onToDateChange: (date: Date | undefined) => void;
    onApplyFilters: () => void;
}

export const DashboardFilters = ({
    selectedState,
    selectedTerritory,
    selectedCity,
    selectedDistrict,
    selectedDepartment,
    salesOrderStatus,
    fromDate,
    toDate,
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
    onFromDateChange,
    onToDateChange,
    onApplyFilters,
}: DashboardFiltersProps) => {
    const [isExpanded, setIsExpanded] = useState(false);

    const toggleExpand = () => {
        setIsExpanded(!isExpanded);
    };

    return (
        <Card className="shadow-sm">
            <CardHeader
                className="py-3 flex flex-row items-center justify-between cursor-pointer"
                onClick={toggleExpand}
            >
                <CardTitle className="text-lg font-semibold">Filters</CardTitle>
                <div>{isExpanded ? <ChevronUp className="h-5 w-5" /> : <ChevronDown className="h-5 w-5" />}</div>
            </CardHeader>
            {isExpanded && (
                <CardContent className="space-y-4 pt-0">
                    <div className="grid grid-cols-1 md:grid-cols-3 lg:grid-cols-4 gap-3">
                        <div className="space-y-1">
                            <label className="text-xs font-medium text-gray-700">State</label>
                            <Select
                                value={selectedState}
                                onValueChange={(value) => {
                                    onStateChange(value);
                                    // Automatically apply filters when a state is selected and it's not "all"
                                    if (value !== "all") {
                                        setTimeout(() => {
                                            onApplyFilters();
                                        }, 0);
                                    }
                                }}
                            >
                                <SelectTrigger className="w-full h-9">
                                    <SelectValue placeholder="Select State" />
                                </SelectTrigger>
                                <SelectContent className="max-h-[200px] overflow-y-auto">
                                    <SelectItem value="all">All States</SelectItem>
                                    {states?.map((state) => (
                                        <SelectItem
                                            key={state.creation}
                                            value={state.name}
                                        >
                                            {state.state}
                                        </SelectItem>
                                    ))}
                                </SelectContent>
                            </Select>
                        </div>

                        <div className="space-y-1">
                            <label className="text-xs font-medium text-gray-700">Territory</label>
                            <Select
                                value={selectedTerritory}
                                onValueChange={onTerritoryChange}
                            >
                                <SelectTrigger className="w-full h-9">
                                    <SelectValue placeholder="Select Territory" />
                                </SelectTrigger>
                                <SelectContent className="max-h-[200px] overflow-y-auto">
                                    <SelectItem value="all">All Territories</SelectItem>
                                    {territories?.map((territory) => (
                                        <SelectItem
                                            key={territory.creation}
                                            value={territory.name}
                                        >
                                            {territory.name}
                                        </SelectItem>
                                    ))}
                                </SelectContent>
                            </Select>
                        </div>

                        <div className="space-y-1">
                            <label className="text-xs font-medium text-gray-700">City</label>
                            <Select
                                value={selectedCity}
                                onValueChange={onCityChange}
                            >
                                <SelectTrigger className="w-full h-9">
                                    <SelectValue placeholder="Select City" />
                                </SelectTrigger>
                                <SelectContent className="max-h-[200px] overflow-y-auto">
                                    <SelectItem value="all">All Cities</SelectItem>
                                    {cities?.map((city) => (
                                        <SelectItem
                                            key={city.creation}
                                            value={city.name}
                                        >
                                            {city.city}
                                        </SelectItem>
                                    ))}
                                </SelectContent>
                            </Select>
                        </div>

                        <div className="space-y-1">
                            <label className="text-xs font-medium text-gray-700">District</label>
                            <Select
                                value={selectedDistrict}
                                onValueChange={onDistrictChange}
                            >
                                <SelectTrigger className="w-full h-9">
                                    <SelectValue placeholder="Select District" />
                                </SelectTrigger>
                                <SelectContent className="max-h-[200px] overflow-y-auto">
                                    <SelectItem value="all">All Districts</SelectItem>
                                    {districts?.map((district) => (
                                        <SelectItem
                                            key={district.creation}
                                            value={district.name}
                                        >
                                            {district.district}
                                        </SelectItem>
                                    ))}
                                </SelectContent>
                            </Select>
                        </div>

                        <div className="space-y-1">
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

                        <div className="space-y-1">
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

                        <div className="space-y-1 md:col-span-2">
                            <label className="text-xs font-medium text-gray-700">Date Range</label>
                            <div className="flex gap-2">
                                <DatePicker
                                    label="From"
                                    date={fromDate}
                                    setDate={onFromDateChange}
                                />
                                <DatePicker
                                    label="To"
                                    date={toDate}
                                    setDate={onToDateChange}
                                />
                            </div>
                        </div>
                    </div>

                    <div className="flex justify-end pt-2">
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
