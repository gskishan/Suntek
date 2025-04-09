import { DatePicker } from "./ui/date-picker";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { useState } from "react";
import { ChevronDown, ChevronUp } from "lucide-react";
import { MultiSelect } from "./ui/multi-select";

interface DashboardFiltersProps {
    selectedStates: string[];
    selectedTerritories: string[];
    selectedCities: string[];
    selectedDistricts: string[];
    selectedDepartment: string;
    salesOrderStatus: string;
    fromDate: Date | undefined;
    toDate: Date | undefined;
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
    onFromDateChange: (date: Date | undefined) => void;
    onToDateChange: (date: Date | undefined) => void;
    onApplyFilters: () => void;
}

export const DashboardFilters = ({
    selectedStates,
    selectedTerritories,
    selectedCities,
    selectedDistricts,
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
                            <label className="text-xs font-medium text-gray-700">States</label>
                            <MultiSelect
                                values={selectedStates}
                                onValuesChange={(values: string[]) => {
                                    onStateChange(values);
                                    if (values.length > 0) {
                                        setTimeout(() => {
                                            onApplyFilters();
                                        }, 0);
                                    }
                                }}
                                options={states.map((state) => ({
                                    value: state.name,
                                    label: state.state,
                                }))}
                                placeholder="Select States"
                            />
                        </div>

                        <div className="space-y-1">
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

                        <div className="space-y-1">
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

                        <div className="space-y-1">
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
