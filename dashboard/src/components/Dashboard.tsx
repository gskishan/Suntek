import { useState, useEffect, useCallback, useMemo } from "react";
import { useFrappeGetCall, useFrappeGetDocList } from "frappe-react-sdk";
import { HierarchicalDataTable } from "./HierarchicalDataTable";
import { DashboardFilters } from "./DashboardFilters";
import { Button } from "@/components/ui/button";
import { RefreshCw, ShieldAlert, Users, Calendar, ExternalLink } from "lucide-react";
import { Card } from "@/components/ui/card";
import { DashboardTabs } from "./DashboardTabs";

type DashboardType = "sales" | "crm" | "activity";

export const Dashboard = () => {
    const [dashboardType, setDashboardType] = useState<DashboardType>("sales");
    const [selectedStates, setSelectedStates] = useState<string[]>([]);
    const [selectedTerritories, setSelectedTerritories] = useState<string[]>([]);
    const [selectedCities, setSelectedCities] = useState<string[]>([]);
    const [selectedDistricts, setSelectedDistricts] = useState<string[]>([]);
    const [selectedDepartment, setSelectedDepartment] = useState<string>("all");
    const [salesOrderStatus, setSalesOrderStatus] = useState<string>("all");
    const [selectedTypeOfCase, setSelectedTypeOfCase] = useState<string>("all");
    const [selectedTypeOfStructure, setSelectedTypeOfStructure] = useState<string>("all");
    const [selectedSalesPersons, setSelectedSalesPersons] = useState<string[]>([]);
    const [fromDate, setFromDate] = useState<Date>();
    const [toDate, setToDate] = useState<Date>();
    const [limit, setLimit] = useState<number | null>(100);
    const [minCapacity, setMinCapacity] = useState<number | null>(null);
    const [maxCapacity, setMaxCapacity] = useState<number | null>(null);
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

    const { data: salesPersons } = useFrappeGetDocList("Sales Person", {
        fields: ["name", "sales_person_name"],
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

        if (selectedTypeOfStructure !== "all") {
            params.type_of_structure = selectedTypeOfStructure;
        }

        if (selectedSalesPersons.length > 0) {
            params.sales_person = selectedSalesPersons.join(",");
        }

        if (fromDate) {
            params.from_date = fromDate.toISOString().split("T")[0];
        }

        if (toDate) {
            params.to_date = toDate.toISOString().split("T")[0];
        }

        if (minCapacity !== null) {
            params.min_capacity = minCapacity.toString();
        }

        if (maxCapacity !== null) {
            params.max_capacity = maxCapacity.toString();
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
        selectedTypeOfStructure,
        selectedSalesPersons,
        fromDate,
        toDate,
        limit,
        minCapacity,
        maxCapacity,
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
        setSelectedTypeOfStructure("all");
        setSelectedSalesPersons([]);
        setFromDate(undefined);
        setToDate(undefined);
        setLimit(100);
        setMinCapacity(null);
        setMaxCapacity(null);
        setLastUpdated(new Date());
        setTimeout(() => {
            refreshSalesOrders();
        }, 50);
    }, [refreshSalesOrders]);

    const handleDashboardChange = useCallback((type: DashboardType) => {
        setDashboardType(type);
    }, []);

    const erpUrl = useMemo(() => {
        return "/app";
    }, []);

    const navigateToERP = useCallback(() => {
        window.location.href = erpUrl;
    }, [erpUrl]);

    return (
        <div className="py-4 space-y-4">
            <div className="flex justify-between items-center">
                <h1 className="text-2xl font-bold">Dashboard</h1>
                <div className="flex items-center gap-2">
                    <Button
                        variant="outline"
                        size="sm"
                        onClick={navigateToERP}
                        className="flex items-center gap-2"
                    >
                        <ExternalLink className="h-4 w-4" />
                        Back to ERP
                    </Button>
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
            </div>

            {/* Dashboard Tabs */}
            <DashboardTabs
                activeDashboard={dashboardType}
                onDashboardChange={handleDashboardChange}
            />

            {/* Sales Dashboard Content */}
            {dashboardType === "sales" && (
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
                            selectedTypeOfStructure={selectedTypeOfStructure}
                            selectedSalesPersons={selectedSalesPersons}
                            fromDate={fromDate}
                            toDate={toDate}
                            limit={limit}
                            minCapacity={minCapacity}
                            maxCapacity={maxCapacity}
                            states={states || []}
                            territories={territories}
                            cities={cities}
                            districts={districts}
                            departments={departments || []}
                            salesPersons={salesPersons || []}
                            onStateChange={setSelectedStates}
                            onTerritoryChange={setSelectedTerritories}
                            onCityChange={setSelectedCities}
                            onDistrictChange={setSelectedDistricts}
                            onDepartmentChange={setSelectedDepartment}
                            onStatusChange={setSalesOrderStatus}
                            onTypeOfCaseChange={setSelectedTypeOfCase}
                            onTypeOfStructureChange={setSelectedTypeOfStructure}
                            onSalesPersonChange={setSelectedSalesPersons}
                            onFromDateChange={setFromDate}
                            onToDateChange={setToDate}
                            onLimitChange={setLimit}
                            onMinCapacityChange={setMinCapacity}
                            onMaxCapacityChange={setMaxCapacity}
                            onApplyFilters={handleApplyFilters}
                            onClearFilters={handleClearFilters}
                            dateRange={{ from: undefined, to: undefined }}
                            search=""
                        />
                    </div>

                    <div className="flex-grow transition-all duration-300 ease-in-out overflow-hidden flex flex-col">
                        {permissionError && (
                            <Card className="p-8 border-red-200 bg-red-50 rounded-lg">
                                <div className="flex items-center gap-4">
                                    <ShieldAlert className="h-10 w-10 text-red-500" />
                                    <div>
                                        <h2 className="text-lg font-semibold text-red-700">Permission Error</h2>
                                        <p className="text-red-600">{permissionError}</p>
                                        <p className="mt-2 text-sm text-red-600">
                                            You need to have System Manager or Sales Manager role to view this data.
                                            Please contact your administrator for access.
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
                                            <div className="flex flex-col justify-center items-center h-full bg-gray-50 rounded-lg border border-gray-200">
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
                                                    No sales data is available for the selected filters. Try adjusting
                                                    your filters or selecting a different date range.
                                                </p>
                                            </div>
                                        )}
                                    </>
                                )}
                            </>
                        )}
                    </div>
                </div>
            )}

            {/* CRM Dashboard Content */}
            {dashboardType === "crm" && (
                <div className="flex flex-col items-center justify-center h-[calc(100vh-220px)] bg-gray-50 rounded-lg border border-gray-200">
                    <Users className="h-16 w-16 text-gray-400 mb-4" />
                    <h2 className="text-2xl font-medium text-gray-700 mb-2">CRM Dashboard</h2>
                    <p className="text-gray-500 text-center max-w-md">The CRM Dashboard is under development.</p>
                </div>
            )}

            {/* Activity Dashboard Content */}
            {dashboardType === "activity" && (
                <div className="flex flex-col items-center justify-center h-[calc(100vh-220px)] bg-gray-50 rounded-lg border border-gray-200">
                    <Calendar className="h-16 w-16 text-gray-400 mb-4" />
                    <h2 className="text-2xl font-medium text-gray-700 mb-2">Activity Dashboard</h2>
                    <p className="text-gray-500 text-center max-w-md">The Activity dashboard is under development.</p>
                </div>
            )}
        </div>
    );
};
