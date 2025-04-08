import { useState } from "react";
import { useFrappeGetCall, useFrappeGetDocList } from "frappe-react-sdk";
import { SalesOrderTable } from "./SalesOrderTable";
import { DashboardFilters } from "./DashboardFilters";
import { Separator } from "@/components/ui/separator";

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

            <DashboardFilters
                selectedTerritory={selectedTerritory}
                selectedState={selectedState}
                selectedDistrict={selectedDistrict}
                selectedCity={selectedCity}
                salesOrderStatus={salesOrderStatus}
                fromDate={fromDate}
                toDate={toDate}
                territories={territories || []}
                states={states || []}
                districts={districts || []}
                cities={cities || []}
                onTerritoryChange={(value) => {
                    setSelectedTerritory(value);
                    setSelectedState("all");
                    setSelectedDistrict("all");
                    setSelectedCity("all");
                }}
                onStateChange={(value) => {
                    setSelectedState(value);
                    setSelectedDistrict("all");
                    setSelectedCity("all");
                }}
                onDistrictChange={(value) => {
                    setSelectedDistrict(value);
                    setSelectedCity("all");
                }}
                onCityChange={setSelectedCity}
                onStatusChange={setSalesOrderStatus}
                onFromDateChange={setFromDate}
                onToDateChange={setToDate}
            />

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
