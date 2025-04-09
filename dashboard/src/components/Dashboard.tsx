import { useState, useEffect, useCallback, useMemo } from "react";
import { useFrappeGetCall, useFrappeGetDocList } from "frappe-react-sdk";
import { SalesOrderTable } from "./SalesOrderTable";
import { DashboardFilters } from "./DashboardFilters";
import { Separator } from "@/components/ui/separator";
import { Button } from "@/components/ui/button";
import { RefreshCw } from "lucide-react";

interface SalesOrderFilters {
    state?: string[];
    territory?: string[];
    city?: string[];
    district?: string[];
    department?: string;
    status?: string;
    from_date?: string;
    to_date?: string;
}

export const Dashboard = () => {
    const [selectedStates, setSelectedStates] = useState<string[]>([]);
    const [selectedTerritories, setSelectedTerritories] = useState<string[]>([]);
    const [selectedCities, setSelectedCities] = useState<string[]>([]);
    const [selectedDistricts, setSelectedDistricts] = useState<string[]>([]);
    const [selectedDepartment, setSelectedDepartment] = useState<string>("all");
    const [salesOrderStatus, setSalesOrderStatus] = useState<string>("all");
    const [fromDate, setFromDate] = useState<Date>();
    const [toDate, setToDate] = useState<Date>();
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
        const params: Record<string, any> = { show_sql: "1" };

        // Always include state filter if it's not empty, even if filters are not "applied"
        if (selectedStates.length > 0) {
            // Convert array to comma-separated string for API compatibility
            params.state = selectedStates.join(",");
        }

        if (filtersApplied) {
            // Add all filters when filters are explicitly applied
            if (selectedStates.length > 0) params.state = selectedStates.join(",");
            if (selectedTerritories.length > 0) params.territory = selectedTerritories.join(",");
            if (selectedCities.length > 0) params.city = selectedCities.join(",");
            if (selectedDistricts.length > 0) params.district = selectedDistricts.join(",");
            if (selectedDepartment !== "all") params.department = selectedDepartment;
            if (salesOrderStatus !== "all") params.status = salesOrderStatus;
            if (fromDate) params.from_date = fromDate.toISOString().split("T")[0];
            if (toDate) params.to_date = toDate.toISOString().split("T")[0];
        }

        return params;
    }, [
        filtersApplied,
        selectedStates,
        selectedTerritories,
        selectedCities,
        selectedDistricts,
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

        // Add a delay to ensure state updates are processed
        setTimeout(() => {
            refreshSalesOrders();
        }, 50);
    }, [refreshSalesOrders]);

    // Handle clear filters
    const handleClearFilters = useCallback(() => {
        // Reset all filters
        setSelectedStates([]);
        setSelectedTerritories([]);
        setSelectedCities([]);
        setSelectedDistricts([]);
        setSelectedDepartment("all");
        setSalesOrderStatus("all");
        setFromDate(undefined);
        setToDate(undefined);

        // Keep filtersApplied true to ensure the API call goes through with cleared filters
        setLastUpdated(new Date());

        // Add a delay to ensure state updates are processed
        setTimeout(() => {
            refreshSalesOrders();
        }, 50);
    }, [refreshSalesOrders]);

    // Handle refresh button click
    const handleRefresh = useCallback(() => {
        // Reset all filters
        setSelectedStates([]);
        setSelectedTerritories([]);
        setSelectedCities([]);
        setSelectedDistricts([]);
        setSelectedDepartment("all");
        setSalesOrderStatus("all");
        setFromDate(undefined);
        setToDate(undefined);

        // Reset filters applied flag
        setFiltersApplied(false);
        setLastUpdated(new Date());

        // Add a delay before refreshing to ensure state updates are processed
        setTimeout(() => {
            refreshSalesOrders();
        }, 50);
    }, [refreshSalesOrders]);

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
                selectedStates={selectedStates}
                selectedTerritories={selectedTerritories}
                selectedCities={selectedCities}
                selectedDistricts={selectedDistricts}
                selectedDepartment={selectedDepartment}
                salesOrderStatus={salesOrderStatus}
                fromDate={fromDate}
                toDate={toDate}
                states={states || []}
                territories={territories}
                cities={cities}
                districts={districts}
                departments={departments || []}
                onStateChange={(values) => {
                    setSelectedStates(values);
                    // Reset dependent filters when states change
                    setSelectedTerritories([]);
                    setSelectedCities([]);
                    setSelectedDistricts([]);

                    // Automatically apply filters when states are selected
                    if (values.length > 0) {
                        setFiltersApplied(true);
                        setTimeout(() => {
                            refreshSalesOrders();
                        }, 50);
                    }
                }}
                onTerritoryChange={(values) => {
                    setSelectedTerritories(values);
                    // Reset dependent filters
                    setSelectedCities([]);
                    setSelectedDistricts([]);

                    // Automatically apply filters when territories are selected
                    if (values.length > 0) {
                        setFiltersApplied(true);
                        setTimeout(() => {
                            refreshSalesOrders();
                        }, 50);
                    }
                }}
                onCityChange={(values) => {
                    setSelectedCities(values);
                    setSelectedDistricts([]);

                    // Automatically apply filters when cities are selected
                    if (values.length > 0) {
                        setFiltersApplied(true);
                        setTimeout(() => {
                            refreshSalesOrders();
                        }, 50);
                    }
                }}
                onDistrictChange={(values) => {
                    setSelectedDistricts(values);

                    // Automatically apply filters when districts are selected
                    if (values.length > 0) {
                        setFiltersApplied(true);
                        setTimeout(() => {
                            refreshSalesOrders();
                        }, 50);
                    }
                }}
                onDepartmentChange={setSelectedDepartment}
                onStatusChange={setSalesOrderStatus}
                onFromDateChange={setFromDate}
                onToDateChange={setToDate}
                onApplyFilters={handleApplyFilters}
                onClearFilters={handleClearFilters}
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
