import { useState, useEffect, useCallback, useMemo } from "react";
import { useFrappeGetCall, useFrappeGetDocList } from "frappe-react-sdk";
import { HierarchicalDataTable } from "./HierarchicalDataTable";
import { DashboardFilters } from "./DashboardFilters";
import { Button } from "@/components/ui/button";
import { RefreshCw, ShieldAlert } from "lucide-react";
import { Card } from "@/components/ui/card";

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
    const [limit, setLimit] = useState<number | null>(100);
    const [lastUpdated, setLastUpdated] = useState<Date>(new Date());

    const [permissionError, setPermissionError] = useState<string | null>(null);

    const { data: states } = useFrappeGetDocList("State", {
        fields: ["name", "creation", "state"],
        asDict: true,
        limit: 0,
    });

    const { data: allTerritories } = useFrappeGetDocList("Territory", {
        fields: ["name", "creation"],
        asDict: true,
        limit: 0,
    });

    const { data: allCities } = useFrappeGetDocList("City", {
        fields: ["name", "creation", "city"],
        asDict: true,
        limit: 0,
    });

    const { data: allDistricts } = useFrappeGetDocList("District", {
        fields: ["name", "creation", "district"],
        asDict: true,
        limit: 0,
    });

    const { data: departments } = useFrappeGetDocList("Department", {
        fields: ["name", "creation"],
        asDict: true,
        limit: 0,
    });

    const territories = useMemo(() => {
        return allTerritories || [];
    }, [allTerritories]);

    const cities = useMemo(() => {
        return allCities || [];
    }, [allCities]);

    const districts = useMemo(() => {
        return allDistricts || [];
    }, [allDistricts]);

    const queryParams = useMemo(() => {
        const params: Record<string, any> = {
            limit: limit === null ? "all" : limit.toString(),
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

    const {
        data: salesOrdersResponse,
        isLoading: isLoadingSalesOrders,
        error: salesOrdersError,
        mutate: refreshSalesOrders,
    } = useFrappeGetCall("suntek_app.api.sales_dashboard.sales_order.get_sales_order_data", queryParams, {
        revalidateOnFocus: false,
        revalidateOnReconnect: false,
    });

    const salesOrdersData = useMemo(() => {
        if (!salesOrdersResponse) return null;

        const response = salesOrdersResponse as any;
        if (response.message && response.message.data) {
            return response.message.data;
        }
        if (response.data) {
            return response.data;
        }
        return null;
    }, [salesOrdersResponse]);

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

    const handleApplyFilters = useCallback(() => {
        setLastUpdated(new Date());
        setTimeout(() => {
            refreshSalesOrders();
        }, 50);
    }, [refreshSalesOrders]);

    const handleClearFilters = useCallback(() => {
        setSelectedStates([]);
        setSelectedTerritories([]);
        setSelectedCities([]);
        setSelectedDistricts([]);
        setSelectedDepartment("all");
        setSalesOrderStatus("all");
        setSelectedTypeOfCase("all");
        setFromDate(undefined);
        setToDate(undefined);
        setLimit(100);
        setLastUpdated(new Date());
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

            <div className="flex flex-row gap-4 h-[calc(100vh-180px)]">
                <div className="transition-all duration-300 ease-in-out flex items-start">
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
                        onDateRangeChange={(range) => {}}
                        dateRange={{ from: undefined, to: undefined }}
                        search=""
                    />
                </div>

                <div className="flex-grow transition-all duration-300 ease-in-out overflow-hidden flex flex-col">
                    {/* Filters summary */}
                    {(selectedStates.length > 0 ||
                        selectedTerritories.length > 0 ||
                        selectedCities.length > 0 ||
                        selectedDistricts.length > 0 ||
                        selectedDepartment !== "all" ||
                        salesOrderStatus !== "all" ||
                        selectedTypeOfCase !== "all" ||
                        limit !== 100 ||
                        fromDate !== undefined ||
                        toDate !== undefined) && (
                        <div className="bg-blue-50 p-2 text-sm text-blue-800 mb-3 rounded-md">
                            <span className="font-medium">Filters applied: </span>
                            {selectedStates.length > 0 && (
                                <span className="mr-2">States ({selectedStates.length})</span>
                            )}
                            {selectedTerritories.length > 0 && (
                                <span className="mr-2">Territories ({selectedTerritories.length})</span>
                            )}
                            {selectedCities.length > 0 && (
                                <span className="mr-2">Cities ({selectedCities.length})</span>
                            )}
                            {selectedDistricts.length > 0 && (
                                <span className="mr-2">Districts ({selectedDistricts.length})</span>
                            )}
                            {selectedDepartment !== "all" && <span className="mr-2">Department</span>}
                            {salesOrderStatus !== "all" && <span className="mr-2">Status: {salesOrderStatus}</span>}
                            {selectedTypeOfCase !== "all" && <span className="mr-2">Type: {selectedTypeOfCase}</span>}
                            {limit !== 100 && <span className="mr-2">Limit: {limit}</span>}
                            {fromDate && <span className="mr-2">From: {fromDate.toLocaleDateString()}</span>}
                            {toDate && <span className="mr-2">To: {toDate.toLocaleDateString()}</span>}
                        </div>
                    )}

                    {permissionError && (
                        <Card className="p-8 border-red-200 bg-red-50 rounded-lg">
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

                    {!permissionError && (
                        <>
                            {isLoadingSalesOrders ? (
                                <div className="flex justify-center items-center h-64">
                                    <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-gray-900"></div>
                                </div>
                            ) : (
                                <>
                                    {salesOrdersData && salesOrdersData.length > 0 ? (
                                        <>
                                            <HierarchicalDataTable data={salesOrdersData} />
                                            <div className="text-xs text-gray-500 text-right mt-2">
                                                Last updated: {lastUpdated.toLocaleString()}
                                            </div>
                                        </>
                                    ) : (
                                        <div className="flex flex-col justify-center items-center h-64 bg-gray-50 rounded-lg border border-gray-200">
                                            <svg
                                                xmlns="http://www.w3.org/2000/svg"
                                                className="h-16 w-16 text-gray-400 mb-4"
                                                fill="none"
                                                viewBox="0 0 24 24"
                                                stroke="currentColor"
                                            >
                                                <path
                                                    strokeLinecap="round"
                                                    strokeLinejoin="round"
                                                    strokeWidth={1.5}
                                                    d="M9.172 16.172a4 4 0 015.656 0M9 10h.01M15 10h.01M12 2a10 10 0 110 20 10 10 0 010-20z"
                                                />
                                            </svg>
                                            <h3 className="text-xl font-medium text-gray-700">No data found</h3>
                                            <p className="text-sm text-gray-500 text-center mt-2 max-w-md">
                                                No sales data is available for the selected filters. Try adjusting your
                                                filters or selecting a different date range.
                                            </p>
                                        </div>
                                    )}
                                </>
                            )}
                        </>
                    )}
                </div>
            </div>
        </div>
    );
};
