import { useState, useEffect, useCallback, useMemo } from "react";
import { useFrappeGetCall, useFrappeGetDocList } from "frappe-react-sdk";
import { SalesOrderTable } from "./SalesOrderTable";
import { DashboardFilters } from "./DashboardFilters";
import { Separator } from "@/components/ui/separator";
import { Button } from "@/components/ui/button";
import { RefreshCw } from "lucide-react";

interface SalesOrderFilters {
    state?: string;
    territory?: string;
    city?: string;
    district?: string;
    department?: string;
    status?: string;
    from_date?: string;
    to_date?: string;
}

export const Dashboard = () => {
    const [selectedState, setSelectedState] = useState<string>("all");
    const [selectedTerritory, setSelectedTerritory] = useState<string>("all");
    const [selectedCity, setSelectedCity] = useState<string>("all");
    const [selectedDistrict, setSelectedDistrict] = useState<string>("all");
    const [selectedDepartment, setSelectedDepartment] = useState<string>("all");
    const [salesOrderStatus, setSalesOrderStatus] = useState<string>("all");
    const [fromDate, setFromDate] = useState<Date>();
    const [toDate, setToDate] = useState<Date>();
    const [refreshKey, setRefreshKey] = useState<number>(0);
    const [lastUpdated, setLastUpdated] = useState<Date>(new Date());
    const [filtersApplied, setFiltersApplied] = useState<boolean>(false);

    // Fetch all states
    const { data: states } = useFrappeGetDocList("State", {
        fields: ["name", "creation", "state"],
        asDict: true,
        limit: 0,
    });

    // Fetch all territories
    const { data: allTerritories } = useFrappeGetDocList("Territory", {
        fields: ["name", "creation"],
        asDict: true,
        limit: 0,
    });

    // Fetch all cities
    const { data: allCities } = useFrappeGetDocList("City", {
        fields: ["name", "creation", "city"],
        asDict: true,
        limit: 0,
    });

    // Fetch all districts
    const { data: allDistricts } = useFrappeGetDocList("District", {
        fields: ["name", "creation", "district"],
        asDict: true,
        limit: 0,
    });

    // Fetch all departments
    const { data: departments } = useFrappeGetDocList("Department", {
        fields: ["name", "creation"],
        asDict: true,
        limit: 0,
    });

    // Filter territories, cities, and districts based on selected values
    const territories = useMemo(() => {
        return allTerritories || [];
    }, [allTerritories]);

    const cities = useMemo(() => {
        return allCities || [];
    }, [allCities]);

    const districts = useMemo(() => {
        return allDistricts || [];
    }, [allDistricts]);

    // Build query parameters for API call
    const queryParams = useMemo(() => {
        const params: Record<string, string> = { show_sql: "1" };

        // Always include state filter if it's not "all", even if filters are not "applied"
        if (selectedState !== "all") {
            params.state = selectedState;
            // Set filtersApplied to true if state is selected but filters aren't applied
            if (!filtersApplied) {
                setTimeout(() => setFiltersApplied(true), 0);
            }
        }

        if (filtersApplied) {
            // State is already handled above
            if (selectedTerritory !== "all") params.territory = selectedTerritory;
            if (selectedCity !== "all") params.city = selectedCity;
            if (selectedDistrict !== "all") params.district = selectedDistrict;
            if (selectedDepartment !== "all") params.department = selectedDepartment;
            if (salesOrderStatus !== "all") params.status = salesOrderStatus;
            if (fromDate) params.from_date = fromDate.toISOString().split("T")[0];
            if (toDate) params.to_date = toDate.toISOString().split("T")[0];
        }

        return params;
    }, [
        filtersApplied,
        selectedState,
        selectedTerritory,
        selectedCity,
        selectedDistrict,
        selectedDepartment,
        salesOrderStatus,
        fromDate,
        toDate,
    ]);

    // Fetch sales orders with filters
    const {
        data: salesOrders,
        isLoading: isLoadingSalesOrders,
        mutate: refreshSalesOrders,
    } = useFrappeGetCall("suntek_app.api.sales_dashboard.sales_order.get_sales_order_data", queryParams, {
        revalidateOnFocus: false,
        revalidateOnReconnect: false,
    });

    // Handle apply filters
    const handleApplyFilters = useCallback(() => {
        setFiltersApplied(true);
        setLastUpdated(new Date());
        refreshSalesOrders();
    }, [refreshSalesOrders]);

    // Handle refresh button click
    const handleRefresh = useCallback(() => {
        // Reset all filters
        setSelectedState("all");
        setSelectedTerritory("all");
        setSelectedCity("all");
        setSelectedDistrict("all");
        setSelectedDepartment("all");
        setSalesOrderStatus("all");
        setFromDate(undefined);
        setToDate(undefined);

        // Reset filters applied flag
        setFiltersApplied(false);
        setRefreshKey((prev) => prev + 1);
        setLastUpdated(new Date());

        // Add a slight delay before refreshing to ensure state updates are processed
        setTimeout(() => {
            refreshSalesOrders();
        }, 10);
    }, [refreshSalesOrders]);

    // Log data sizes for debugging
    useEffect(() => {
        if (salesOrders?.data) {
            console.log(`Data size: ${JSON.stringify(salesOrders.data).length} characters`);
            console.log(`Number of states: ${salesOrders.data.length}`);
            console.log(`Applied filters:`, queryParams);
        }
    }, [salesOrders, queryParams]);

    // Log state changes for debugging
    useEffect(() => {
        console.log(`State changed to: ${selectedState}`);
        console.log(`Current filters applied state: ${filtersApplied}`);
        console.log(`Current query params:`, queryParams);
    }, [selectedState, filtersApplied, queryParams]);

    return (
        <div className="min-h-screen bg-gray-50/50 p-6 space-y-6">
            <div className="flex items-center justify-between">
                <h1 className="text-3xl font-bold text-gray-900">Sales Dashboard</h1>
                <div className="flex items-center gap-4">
                    <Button
                        variant="outline"
                        size="sm"
                        onClick={handleRefresh}
                        className="flex items-center gap-2"
                    >
                        <RefreshCw className="h-4 w-4" />
                        Refresh
                    </Button>
                    <div className="text-sm text-gray-500">Last updated: {lastUpdated.toLocaleString()}</div>
                </div>
            </div>

            <DashboardFilters
                selectedState={selectedState}
                selectedTerritory={selectedTerritory}
                selectedCity={selectedCity}
                selectedDistrict={selectedDistrict}
                selectedDepartment={selectedDepartment}
                salesOrderStatus={salesOrderStatus}
                fromDate={fromDate}
                toDate={toDate}
                states={states || []}
                territories={territories}
                cities={cities}
                districts={districts}
                departments={departments || []}
                onStateChange={(value) => {
                    setSelectedState(value);
                    setSelectedTerritory("all");
                    setSelectedCity("all");
                    setSelectedDistrict("all");

                    // Automatically apply filters when a state is selected
                    if (value !== "all") {
                        setFiltersApplied(true);
                        setTimeout(() => {
                            refreshSalesOrders();
                        }, 0);
                    }
                }}
                onTerritoryChange={(value) => {
                    setSelectedTerritory(value);
                    setSelectedCity("all");
                    setSelectedDistrict("all");
                }}
                onCityChange={(value) => {
                    setSelectedCity(value);
                    setSelectedDistrict("all");
                }}
                onDistrictChange={setSelectedDistrict}
                onDepartmentChange={setSelectedDepartment}
                onStatusChange={setSalesOrderStatus}
                onFromDateChange={setFromDate}
                onToDateChange={setToDate}
                onApplyFilters={handleApplyFilters}
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
