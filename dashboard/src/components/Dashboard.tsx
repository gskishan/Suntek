import { useState, useEffect, useCallback, useMemo } from "react";
import { useFrappeGetCall, useFrappeGetDocList } from "frappe-react-sdk";
import { SalesOrderTable } from "./SalesOrderTable";
import { HierarchicalDataTable } from "./HierarchicalDataTable";
import { DashboardFilters } from "./DashboardFilters";
import { Separator } from "@/components/ui/separator";
import { Button } from "@/components/ui/button";
import { RefreshCw, ShieldAlert } from "lucide-react";
import { Card } from "@/components/ui/card";

interface SalesOrderFilters {
    state?: string[];
    territory?: string[];
    city?: string[];
    district?: string[];
    department?: string;
    status?: string;
    type_of_case?: string;
    from_date?: string;
    to_date?: string;
    limit?: number;
}

export const Dashboard = () => {
    const [selectedStates, setSelectedStates] = useState<string[]>([]);
    const [selectedTerritories, setSelectedTerritories] = useState<string[]>([]);
    const [selectedCities, setSelectedCities] = useState<string[]>([]);
    const [selectedDistricts, setSelectedDistricts] = useState<string[]>([]);
    const [selectedDepartment, setSelectedDepartment] = useState<string>("all");
    const [salesOrderStatus, setSalesOrderStatus] = useState<string>("all");
    const [selectedTypeOfCase, setSelectedTypeOfCase] = useState<string>("all");
    const [fromDate, setFromDate] = useState<Date>();
    const [toDate, setToDate] = useState<Date>();
    const [limit, setLimit] = useState<number>(100);
    const [lastUpdated, setLastUpdated] = useState<Date>(new Date());
    const [filtersApplied, setFiltersApplied] = useState<boolean>(false);

    // Add a state to track permission errors
    const [permissionError, setPermissionError] = useState<string | null>(null);

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

    // Build query parameters from filters
    const queryParams = useMemo(() => {
        const params: Record<string, any> = {
            limit,
        };

        if (selectedStates.length > 0) {
            params.state = selectedStates.join(",");
        }

        if (selectedTerritories.length > 0) {
            params.territory = selectedTerritories.join(",");
        }

        if (selectedCities.length > 0) {
            params.city = selectedCities.join(",");
        }

        if (selectedDistricts.length > 0) {
            params.district = selectedDistricts.join(",");
        }

        if (selectedDepartment !== "all") {
            params.department = selectedDepartment;
        }

        if (salesOrderStatus !== "all") {
            params.status = salesOrderStatus;
        }

        if (selectedTypeOfCase !== "all") {
            params.type_of_case = selectedTypeOfCase;
        }

        if (fromDate) {
            params.from_date = fromDate.toISOString().split("T")[0];
        }

        if (toDate) {
            params.to_date = toDate.toISOString().split("T")[0];
        }

        return params;
    }, [
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
    ]);

    // Fetch sales orders with filters
    const {
        data: salesOrdersResponse,
        isLoading: isLoadingSalesOrders,
        error: salesOrdersError,
        mutate: refreshSalesOrders,
    } = useFrappeGetCall("suntek_app.api.sales_dashboard.sales_order.get_sales_order_data", queryParams, {
        revalidateOnFocus: false,
        revalidateOnReconnect: false,
    });

    // Type-safe access to sales order data
    const salesOrdersData = useMemo(() => {
        if (!salesOrdersResponse) return null;

        // Handle different response formats
        const response = salesOrdersResponse as any;
        if (response.message && response.message.data) {
            return response.message.data;
        }
        if (response.data) {
            return response.data;
        }
        return null;
    }, [salesOrdersResponse]);

    // Check for permission errors
    useEffect(() => {
        if (salesOrdersError) {
            const errorObj = salesOrdersError as any;
            const errorMessage =
                errorObj?.message?.message ||
                errorObj?.error?.message ||
                errorObj?.message ||
                "An error occurred while fetching sales data";

            if (typeof errorMessage === "string" && errorMessage.includes("Access Denied")) {
                setPermissionError(errorMessage);
            } else {
                setPermissionError(null);
            }
        } else {
            setPermissionError(null);
        }
    }, [salesOrdersError]);

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
        setSelectedTypeOfCase("all");
        setFromDate(undefined);
        setToDate(undefined);
        setLimit(100); // Reset limit to default

        // Keep filtersApplied true to ensure the API call goes through with cleared filters
        setLastUpdated(new Date());

        // Add a delay to ensure state updates are processed
        setTimeout(() => {
            refreshSalesOrders();
        }, 50);
    }, [refreshSalesOrders]);

    return (
        <div className="py-4 space-y-4">
            <div className="flex justify-between items-center">
                <h1 className="text-2xl font-bold">Sales Dashboard</h1>
                <Button
                    variant="outline"
                    size="sm"
                    onClick={() => refreshSalesOrders()}
                    disabled={isLoadingSalesOrders}
                    className="flex items-center gap-2"
                >
                    <RefreshCw className={`h-4 w-4 ${isLoadingSalesOrders ? "animate-spin" : ""}`} />
                    Refresh Data
                </Button>
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
                {/* Filters - Left Side */}
                <div className="lg:col-span-4">
                    <DashboardFilters
                        selectedStates={selectedStates}
                        selectedTerritories={selectedTerritories}
                        selectedCities={selectedCities}
                        selectedDistricts={selectedDistricts}
                        selectedDepartment={selectedDepartment}
                        salesOrderStatus={salesOrderStatus}
                        selectedTypeOfCase={selectedTypeOfCase}
                        fromDate={fromDate}
                        toDate={toDate}
                        limit={limit}
                        states={states || []}
                        territories={territories}
                        cities={cities}
                        districts={districts}
                        departments={departments || []}
                        onStateChange={setSelectedStates}
                        onTerritoryChange={setSelectedTerritories}
                        onCityChange={setSelectedCities}
                        onDistrictChange={setSelectedDistricts}
                        onDepartmentChange={setSelectedDepartment}
                        onStatusChange={setSalesOrderStatus}
                        onTypeOfCaseChange={setSelectedTypeOfCase}
                        onFromDateChange={setFromDate}
                        onToDateChange={setToDate}
                        onLimitChange={setLimit}
                        onApplyFilters={handleApplyFilters}
                        onClearFilters={handleClearFilters}
                    />
                </div>

                {/* Main Content - Right Side */}
                <div className="lg:col-span-8">
                    {/* Permission Error Message */}
                    {permissionError && (
                        <Card className="p-8 border-red-200 bg-red-50">
                            <div className="flex items-center gap-4">
                                <ShieldAlert className="h-10 w-10 text-red-500" />
                                <div>
                                    <h2 className="text-lg font-semibold text-red-700">Permission Error</h2>
                                    <p className="text-red-600">{permissionError}</p>
                                    <p className="mt-2 text-sm text-red-600">
                                        You need to have System Manager or Sales Manager role to view this data. Please
                                        contact your administrator for access.
                                    </p>
                                </div>
                            </div>
                        </Card>
                    )}

                    {/* Display sales data only if no permission error */}
                    {!permissionError && (
                        <>
                            {isLoadingSalesOrders ? (
                                <div className="flex justify-center items-center h-64">
                                    <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-gray-900"></div>
                                </div>
                            ) : (
                                salesOrdersData && <HierarchicalDataTable data={salesOrdersData} />
                            )}

                            <div className="text-xs text-gray-500 text-right mt-2">
                                Last updated: {lastUpdated.toLocaleString()}
                            </div>
                        </>
                    )}
                </div>
            </div>
        </div>
    );
};
