import { useState } from "react";
import { DatePicker } from "./ui/date-picker";
import { useFrappeGetCall, useFrappeGetDocList } from "frappe-react-sdk";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { SalesOrderTable } from "./SalesOrderTable";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Separator } from "@/components/ui/separator";

interface Territory {
    name: string;
    creation: string;
}

interface State {
    name: string;
    creation: string;
    state: string;
}

interface District {
    name: string;
    creation: string;
    state: string;
    district: string;
}

interface City {
    name: string;
    creation: string;
    city: string;
}

interface SalesOrderFilters {
    territory?: string;
    state?: string;
    district?: string;
    city?: string;
    status?: string;
    from_date?: string;
    to_date?: string;
}

export const Dashboard = () => {
    const [selectedTerritory, setSelectedTerritory] = useState<string>("all");
    const [selectedState, setSelectedState] = useState<string>("all");
    const [selectedDistrict, setSelectedDistrict] = useState<string>("all");
    const [selectedCity, setSelectedCity] = useState<string>("all");
    const [salesOrderStatus, setSalesOrderStatus] = useState<string>("all");
    const [fromDate, setFromDate] = useState<Date>();
    const [toDate, setToDate] = useState<Date>();

    // Fetch territories
    const { data: territories } = useFrappeGetDocList("Territory", {
        fields: ["name", "creation"],
        asDict: true,
        limit: 0,
    });

    // Fetch states based on selected territory
    const { data: states } = useFrappeGetDocList("State", {
        fields: ["name", "creation", "state"],
        filters: selectedTerritory !== "all" ? [["territory", "=", selectedTerritory]] : [],
        asDict: true,
        limit: 0,
    });

    // Fetch districts based on selected state
    const { data: districts } = useFrappeGetDocList("District", {
        fields: ["name", "creation", "state", "district"],
        filters: selectedState !== "all" ? [["state", "=", selectedState]] : [],
        asDict: true,
        limit: 0,
    });

    // Fetch cities based on selected district
    const { data: cities } = useFrappeGetDocList("City", {
        fields: ["name", "creation", "city"],
        filters: selectedDistrict !== "all" ? [["district", "=", selectedDistrict]] : [],
        asDict: true,
        limit: 0,
    });

    // Prepare filters for sales orders
    const getSalesOrderFilters = (): SalesOrderFilters => {
        const filters: SalesOrderFilters = {};

        if (selectedTerritory !== "all") {
            filters.territory = selectedTerritory;
        }
        if (selectedState !== "all") {
            filters.state = selectedState;
        }
        if (selectedDistrict !== "all") {
            filters.district = selectedDistrict;
        }
        if (selectedCity !== "all") {
            filters.city = selectedCity;
        }
        if (salesOrderStatus !== "all") {
            filters.status = salesOrderStatus;
        }
        if (fromDate) {
            filters.from_date = fromDate.toISOString().split("T")[0];
        }
        if (toDate) {
            filters.to_date = toDate.toISOString().split("T")[0];
        }

        return filters;
    };

    // Fetch sales orders with filters
    const { data: salesOrders, isLoading: isLoadingSalesOrders } = useFrappeGetCall(
        "suntek_app.api.sales_dashboard.sales_order.get_sales_order_data",
        {
            filters: getSalesOrderFilters(),
        },
    );

    return (
        <div className="min-h-screen bg-gray-50/50 p-6 space-y-6">
            <div className="flex items-center justify-between">
                <h1 className="text-3xl font-bold text-gray-900">Sales Dashboard</h1>
                <div className="text-sm text-gray-500">Last updated: {new Date().toLocaleString()}</div>
            </div>

            <Card className="shadow-sm">
                <CardHeader>
                    <CardTitle className="text-lg font-semibold">Filters</CardTitle>
                </CardHeader>
                <CardContent>
                    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                        <div className="space-y-2">
                            <label className="text-sm font-medium text-gray-700">Territory</label>
                            <Select
                                value={selectedTerritory}
                                onValueChange={(value) => {
                                    setSelectedTerritory(value);
                                    setSelectedState("all");
                                    setSelectedDistrict("all");
                                    setSelectedCity("all");
                                }}
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
                                onValueChange={(value) => {
                                    setSelectedState(value);
                                    setSelectedDistrict("all");
                                    setSelectedCity("all");
                                }}
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
                                onValueChange={(value) => {
                                    setSelectedDistrict(value);
                                    setSelectedCity("all");
                                }}
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
                                onValueChange={setSelectedCity}
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

                        <div className="space-y-2">
                            <label className="text-sm font-medium text-gray-700">Sales Order Status</label>
                            <Select
                                value={salesOrderStatus}
                                onValueChange={setSalesOrderStatus}
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
                                    setDate={setFromDate}
                                />
                                <DatePicker
                                    label="To"
                                    date={toDate}
                                    setDate={setToDate}
                                />
                            </div>
                        </div>
                    </div>
                </CardContent>
            </Card>

            <Separator className="my-6" />

            {/* Display sales orders data */}
            <div className="mt-8">
                {isLoadingSalesOrders ? (
                    <div className="flex items-center justify-center h-64">
                        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-gray-900"></div>
                    </div>
                ) : (
                    <SalesOrderTable data={salesOrders?.data || []} />
                )}
            </div>
        </div>
    );
};
