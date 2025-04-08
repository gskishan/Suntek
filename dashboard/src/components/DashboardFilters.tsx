import { DatePicker } from "./ui/date-picker";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Separator } from "@/components/ui/separator";

interface DashboardFiltersProps {
    selectedTerritory: string;
    selectedState: string;
    selectedDistrict: string;
    selectedCity: string;
    salesOrderStatus: string;
    fromDate: Date | undefined;
    toDate: Date | undefined;
    territories: Array<{ name: string; creation: string }>;
    states: Array<{ name: string; creation: string; state: string }>;
    districts: Array<{ name: string; creation: string; district: string }>;
    cities: Array<{ name: string; creation: string; city: string }>;
    onTerritoryChange: (value: string) => void;
    onStateChange: (value: string) => void;
    onDistrictChange: (value: string) => void;
    onCityChange: (value: string) => void;
    onStatusChange: (value: string) => void;
    onFromDateChange: (date: Date | undefined) => void;
    onToDateChange: (date: Date | undefined) => void;
}

export const DashboardFilters = ({
    selectedTerritory,
    selectedState,
    selectedDistrict,
    selectedCity,
    salesOrderStatus,
    fromDate,
    toDate,
    territories,
    states,
    districts,
    cities,
    onTerritoryChange,
    onStateChange,
    onDistrictChange,
    onCityChange,
    onStatusChange,
    onFromDateChange,
    onToDateChange,
}: DashboardFiltersProps) => {
    return (
        <Card className="shadow-sm">
            <CardHeader>
                <CardTitle className="text-lg font-semibold">Filters</CardTitle>
            </CardHeader>
            <CardContent className="space-y-6">
                {/* Location Filters */}
                <div>
                    <h3 className="text-sm font-medium text-gray-700 mb-4">Location</h3>
                    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
                        <div className="space-y-2">
                            <label className="text-sm font-medium text-gray-700">Territory</label>
                            <Select
                                value={selectedTerritory}
                                onValueChange={onTerritoryChange}
                            >
                                <SelectTrigger className="w-full">
                                    <SelectValue placeholder="Select Territory" />
                                </SelectTrigger>
                                <SelectContent className="max-h-[300px] overflow-y-auto">
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

                        <div className="space-y-2">
                            <label className="text-sm font-medium text-gray-700">State</label>
                            <Select
                                value={selectedState}
                                onValueChange={onStateChange}
                            >
                                <SelectTrigger className="w-full">
                                    <SelectValue placeholder="Select State" />
                                </SelectTrigger>
                                <SelectContent className="max-h-[300px] overflow-y-auto">
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

                        <div className="space-y-2">
                            <label className="text-sm font-medium text-gray-700">District</label>
                            <Select
                                value={selectedDistrict}
                                onValueChange={onDistrictChange}
                            >
                                <SelectTrigger className="w-full">
                                    <SelectValue placeholder="Select District" />
                                </SelectTrigger>
                                <SelectContent className="max-h-[300px] overflow-y-auto">
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

                        <div className="space-y-2">
                            <label className="text-sm font-medium text-gray-700">City</label>
                            <Select
                                value={selectedCity}
                                onValueChange={onCityChange}
                            >
                                <SelectTrigger className="w-full">
                                    <SelectValue placeholder="Select City" />
                                </SelectTrigger>
                                <SelectContent className="max-h-[300px] overflow-y-auto">
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
                    </div>
                </div>

                <Separator />

                {/* Order Filters */}
                <div>
                    <h3 className="text-sm font-medium text-gray-700 mb-4">Order Details</h3>
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                        <div className="space-y-2">
                            <label className="text-sm font-medium text-gray-700">Status</label>
                            <Select
                                value={salesOrderStatus}
                                onValueChange={onStatusChange}
                            >
                                <SelectTrigger className="w-full">
                                    <SelectValue placeholder="Select Status" />
                                </SelectTrigger>
                                <SelectContent className="max-h-[300px] overflow-y-auto">
                                    <SelectItem value="all">All Statuses</SelectItem>
                                    <SelectItem value="Draft">Draft</SelectItem>
                                    <SelectItem value="Submitted">Submitted</SelectItem>
                                    <SelectItem value="Cancelled">Cancelled</SelectItem>
                                </SelectContent>
                            </Select>
                        </div>

                        <div className="space-y-2">
                            <label className="text-sm font-medium text-gray-700">Date Range</label>
                            <div className="flex gap-4">
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
                </div>
            </CardContent>
        </Card>
    );
};
