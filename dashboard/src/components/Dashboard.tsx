import { useState, useEffect, useCallback, useMemo } from "react";
import { useFrappeGetCall, useFrappeGetDocList } from "frappe-react-sdk";
import { HierarchicalDataTable } from "./HierarchicalDataTable";
import { DashboardFilters } from "./DashboardFilters";
import { Button } from "@/components/ui/button";
import { RefreshCw, ShieldAlert, Users, Calendar, ExternalLink, Building, MapPin, Lock } from "lucide-react";
import { Card } from "@/components/ui/card";
import { DashboardTabs } from "./DashboardTabs";
import { DateRangeType } from "./DateQuickFilters";

// Add the frappe declaration for API calls
declare global {
    const frappe: {
        call: (args: { method: string; args?: Record<string, unknown> }) => Promise<unknown>;
    };
}

type MainTabType = "sales" | "crm" | "activity";
type SalesSubTabType = "location" | "department";
type TabType = MainTabType | SalesSubTabType;

interface DashboardProps {
    userName: string;
    userInitial: string;
}

export const Dashboard = ({ userName, userInitial }: DashboardProps) => {
    const [dashboardType, setDashboardType] = useState<TabType>("location");
    const [selectedStates, setSelectedStates] = useState<string[]>([]);
    const [selectedTerritories, setSelectedTerritories] = useState<string[]>([]);
    const [selectedCities, setSelectedCities] = useState<string[]>([]);
    const [selectedDistricts, setSelectedDistricts] = useState<string[]>([]);
    const [selectedDepartment, setSelectedDepartment] = useState<string>("all");
    const [salesOrderStatus, setSalesOrderStatus] = useState<string>("all");
    const [salesOrderStatuses, setSalesOrderStatuses] = useState<string[]>([]);
    const [selectedTypeOfCase, setSelectedTypeOfCase] = useState<string>("all");
    const [selectedTypeOfStructure, setSelectedTypeOfStructure] = useState<string>("all");
    const [selectedSalesPersons, setSelectedSalesPersons] = useState<string[]>([]);
    const [fromDate, setFromDate] = useState<Date | undefined>(undefined);
    const [toDate, setToDate] = useState<Date | undefined>(undefined);
    const [dateRangeType, setDateRangeType] = useState<DateRangeType>("custom");
    const [limit, setLimit] = useState<number | null>(100);
    const [minCapacity, setMinCapacity] = useState<number | null>(null);
    const [maxCapacity, setMaxCapacity] = useState<number | null>(null);
    const [lastUpdated, setLastUpdated] = useState<Date>(new Date());
    const [isLoadingDepartmentOrders, setIsLoadingDepartmentOrders] = useState(false);
    const [isLoadingSalesOrders, setIsLoadingSalesOrders] = useState<boolean>(false);
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

    // Fix the queryParams to correctly handle "All Items"
    const getQueryParams = useMemo(() => {
        const params: Record<string, string | boolean> = {};

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
            // If "multiple" is selected, pass the actual array of statuses as comma-separated
            if (salesOrderStatus === "multiple" && salesOrderStatuses.length > 0) {
                params.status = salesOrderStatuses.join(",");
            } else {
                params.status = salesOrderStatus;
            }
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

        // For limit, use 'all' when limit is null or 0
        if (limit === null || limit === 0) {
            params.limit = "all";
        } else {
            params.limit = limit.toString();
        }

        return params;
    }, [
        selectedStates,
        selectedTerritories,
        selectedCities,
        selectedDistricts,
        selectedDepartment,
        salesOrderStatus,
        salesOrderStatuses,
        selectedTypeOfCase,
        selectedTypeOfStructure,
        selectedSalesPersons,
        fromDate,
        toDate,
        limit,
        minCapacity,
        maxCapacity,
    ]);

    // Update the existing API calls to use getQueryParams
    const {
        data: salesOrdersResponseData,
        isValidating: salesOrdersLoading,
        error: salesOrdersError,
        mutate: refreshSalesOrders,
    } = useFrappeGetCall("suntek_app.api.sales_dashboard.sales_order.get_sales_order_data", getQueryParams);

    // Department Orders Response
    const {
        data: departmentOrdersResponseData,
        isValidating: departmentOrdersLoading,
        mutate: refreshDepartmentOrders,
    } = useFrappeGetCall(
        "suntek_app.api.sales_dashboard.sales_order.get_sales_order_data_by_department",
        getQueryParams,
    );

    // Function to manually refresh sales orders
    const refreshSalesOrdersManually = useCallback(() => {
        if (dashboardType === "location") {
            refreshSalesOrders();
        } else if (dashboardType === "department") {
            refreshDepartmentOrders();
        }
        setLastUpdated(new Date());
    }, [dashboardType, refreshSalesOrders, refreshDepartmentOrders]);

    // Update isLoadingSalesOrders when salesOrdersLoading changes
    useEffect(() => {
        setIsLoadingSalesOrders(salesOrdersLoading);
    }, [salesOrdersLoading]);

    // Update isLoadingDepartmentOrders when departmentOrdersLoading changes
    useEffect(() => {
        setIsLoadingDepartmentOrders(departmentOrdersLoading);
    }, [departmentOrdersLoading]);

    // Update permission error when salesOrdersError changes
    useEffect(() => {
        if (salesOrdersError) {
            // Use a type assertion but be more specific with unknown
            // eslint-disable-next-line @typescript-eslint/no-explicit-any
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

    // Handle date range changes
    const handleDateRangeChange = useCallback(
        (range: { from: Date | undefined; to: Date | undefined; type: DateRangeType }) => {
            setFromDate(range.from);
            setToDate(range.to);
            setDateRangeType(range.type);
            // Automatically apply preset filters (but not custom filters)
            if (range.type !== "custom") {
                setTimeout(() => {
                    refreshSalesOrdersManually();
                }, 50);
            }
        },
        [refreshSalesOrdersManually],
    );

    // Handle multiple status changes
    const handleMultiStatusChange = useCallback((statuses: string[]) => {
        setSalesOrderStatuses(statuses);
        if (statuses.length === 0) {
            setSalesOrderStatus("all");
        } else if (statuses.length === 1) {
            setSalesOrderStatus(statuses[0]);
        } else {
            setSalesOrderStatus("multiple");
        }
    }, []);

    // Handle dashboard type changes
    const handleDashboardChange = useCallback((type: TabType) => {
        // Reset filters when changing tabs
        setSelectedStates([]);
        setSelectedTerritories([]);
        setSelectedCities([]);
        setSelectedDistricts([]);
        setSelectedDepartment("all");
        setSalesOrderStatus("all");
        setSalesOrderStatuses([]);
        setSelectedTypeOfCase("all");
        setSelectedTypeOfStructure("all");
        setSelectedSalesPersons([]);
        setFromDate(undefined);
        setToDate(undefined);
        setDateRangeType("custom");
        setLimit(100);
        setMinCapacity(null);
        setMaxCapacity(null);

        // Change the dashboard type
        setDashboardType(type);
    }, []);

    // Handle applying filters
    const handleApplyFilters = useCallback(() => {
        setLastUpdated(new Date());
        refreshSalesOrdersManually();
    }, [refreshSalesOrdersManually]);

    // Handle clearing filters
    const handleClearFilters = useCallback(() => {
        // Reset all filters
        setSelectedStates([]);
        setSelectedTerritories([]);
        setSelectedCities([]);
        setSelectedDistricts([]);
        setSelectedDepartment("all");
        setSalesOrderStatus("all");
        setSalesOrderStatuses([]);
        setSelectedTypeOfCase("all");
        setSelectedTypeOfStructure("all");
        setSelectedSalesPersons([]);
        setFromDate(undefined);
        setToDate(undefined);
        setDateRangeType("custom");
        setLimit(100);
        setMinCapacity(null);
        setMaxCapacity(null);
        setLastUpdated(new Date());

        // After clearing filters, fetch data with default parameters
        refreshSalesOrdersManually();
    }, [refreshSalesOrdersManually]);

    // Navigate to ERP
    const erpUrl = useMemo(() => {
        return "/app";
    }, []);

    const navigateToERP = useCallback(() => {
        window.location.href = erpUrl;
    }, [erpUrl]);

    // Process the salesOrdersResponseData to get the actual data array
    const salesOrdersData = useMemo(() => {
        if (!salesOrdersResponseData) return null;

        // eslint-disable-next-line @typescript-eslint/no-explicit-any
        const response = salesOrdersResponseData as any;
        let data = null;

        if (response.message && response.message.data) {
            data = response.message.data;
        } else if (response.data) {
            data = response.data;
        }

        return data;
    }, [salesOrdersResponseData]);

    // Process the departmentOrdersResponseData to get the actual data array
    const departmentOrdersData = useMemo(() => {
        if (!departmentOrdersResponseData) return [];

        // eslint-disable-next-line @typescript-eslint/no-explicit-any
        const response = departmentOrdersResponseData as any;
        let data = [];

        if (response.message && response.message.data) {
            data = response.message.data;
        } else if (response.data) {
            data = response.data;
        }

        return data;
    }, [departmentOrdersResponseData]);

    return (
        <div className="py-4 space-y-4">
            <div className="flex items-center justify-between">
                <h1 className="text-2xl font-bold">Dashboard</h1>
                <div className="flex items-center gap-3">
                    <div className="flex items-center">
                        <span className="text-sm text-slate-600 mr-2">Welcome, {userName}</span>
                        <div className="w-8 h-8 bg-slate-200 rounded-full flex items-center justify-center text-slate-600 text-sm">
                            {userInitial || userName?.charAt(0)?.toUpperCase() || "U"}
                        </div>
                    </div>
                </div>
            </div>

            {/* Dashboard Tabs and Actions */}
            <div className="flex items-center justify-between">
                <DashboardTabs
                    activeDashboard={dashboardType}
                    onDashboardChange={handleDashboardChange}
                />
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
                        onClick={refreshSalesOrdersManually}
                        disabled={isLoadingSalesOrders || isLoadingDepartmentOrders}
                        className="flex items-center gap-2"
                    >
                        <RefreshCw
                            className={`h-4 w-4 ${isLoadingSalesOrders || isLoadingDepartmentOrders ? "animate-spin" : ""}`}
                        />
                        Refresh Data
                    </Button>
                </div>
            </div>

            {/* Sales by Location Dashboard Content */}
            {dashboardType === "location" && (
                <div className="flex flex-row gap-4 h-[calc(100vh-180px)]">
                    <div className="transition-all duration-300 ease-in-out flex items-start">
                        <DashboardFilters
                            selectedStates={selectedStates}
                            selectedTerritories={selectedTerritories}
                            selectedCities={selectedCities}
                            selectedDistricts={selectedDistricts}
                            selectedDepartment={selectedDepartment}
                            salesOrderStatus={salesOrderStatus}
                            salesOrderStatuses={salesOrderStatuses}
                            selectedTypeOfCase={selectedTypeOfCase}
                            selectedTypeOfStructure={selectedTypeOfStructure}
                            selectedSalesPersons={selectedSalesPersons}
                            fromDate={fromDate}
                            toDate={toDate}
                            dateRangeType={dateRangeType}
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
                            onMultiStatusChange={handleMultiStatusChange}
                            onTypeOfCaseChange={setSelectedTypeOfCase}
                            onTypeOfStructureChange={setSelectedTypeOfStructure}
                            onSalesPersonChange={setSelectedSalesPersons}
                            onDateRangeChange={handleDateRangeChange}
                            onLimitChange={setLimit}
                            onFromDateChange={setFromDate}
                            onToDateChange={setToDate}
                            onMinCapacityChange={setMinCapacity}
                            onMaxCapacityChange={setMaxCapacity}
                            onApplyFilters={handleApplyFilters}
                            onClearFilters={handleClearFilters}
                            dateRange={{ from: fromDate, to: toDate }}
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
                                                <MapPin className="h-16 w-16 text-gray-400 mb-4" />
                                                <h3 className="text-xl font-medium text-gray-700">No data found</h3>
                                                <p className="text-sm text-gray-500 text-center mt-2 max-w-md">
                                                    No location sales data is available for the selected filters. Try
                                                    adjusting your filters or selecting a different date range.
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

            {/* Sales by Department Dashboard Content */}
            {dashboardType === "department" && (
                <div className="flex flex-row gap-4 h-[calc(100vh-180px)]">
                    <div className="transition-all duration-300 flex items-start">
                        <DashboardFilters
                            selectedStates={selectedStates}
                            selectedTerritories={selectedTerritories}
                            selectedCities={selectedCities}
                            selectedDistricts={selectedDistricts}
                            selectedDepartment={selectedDepartment}
                            salesOrderStatus={salesOrderStatus}
                            salesOrderStatuses={salesOrderStatuses}
                            selectedTypeOfCase={selectedTypeOfCase}
                            selectedTypeOfStructure={selectedTypeOfStructure}
                            selectedSalesPersons={selectedSalesPersons}
                            fromDate={fromDate}
                            toDate={toDate}
                            dateRangeType={dateRangeType}
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
                            onMultiStatusChange={handleMultiStatusChange}
                            onTypeOfCaseChange={setSelectedTypeOfCase}
                            onTypeOfStructureChange={setSelectedTypeOfStructure}
                            onSalesPersonChange={setSelectedSalesPersons}
                            onDateRangeChange={handleDateRangeChange}
                            onLimitChange={setLimit}
                            onFromDateChange={setFromDate}
                            onToDateChange={setToDate}
                            onMinCapacityChange={setMinCapacity}
                            onMaxCapacityChange={setMaxCapacity}
                            onApplyFilters={handleApplyFilters}
                            onClearFilters={handleClearFilters}
                            dateRange={{ from: fromDate, to: toDate }}
                            search=""
                        />
                    </div>

                    <div className="flex-grow transition-all duration-300 ease-in-out overflow-hidden flex flex-col">
                        {permissionError ? (
                            <div className="p-6 bg-gray-50 rounded-lg border border-gray-200">
                                <div className="flex flex-col items-center justify-center text-center">
                                    <Lock className="h-16 w-16 text-gray-400 mb-4" />
                                    <h3 className="text-xl font-medium text-gray-700 mb-2">Permission Required</h3>
                                    <p className="text-gray-500 max-w-md">
                                        You need to have System Manager or Sales Manager role to view this data. Please
                                        contact your administrator for access.
                                    </p>
                                </div>
                            </div>
                        ) : (
                            <>
                                {isLoadingDepartmentOrders ? (
                                    <div className="flex justify-center items-center h-64">
                                        <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-gray-900"></div>
                                    </div>
                                ) : (
                                    <>
                                        {departmentOrdersData && departmentOrdersData.length > 0 ? (
                                            <>
                                                <HierarchicalDataTable
                                                    data={departmentOrdersData}
                                                    viewType="department"
                                                />
                                                <div className="text-xs text-gray-500 text-right mt-2">
                                                    Last updated: {lastUpdated.toLocaleString()}
                                                </div>
                                            </>
                                        ) : (
                                            <div className="flex flex-col justify-center items-center h-full bg-gray-50 rounded-lg border border-gray-200">
                                                <Building className="h-16 w-16 text-gray-400 mb-4" />
                                                <h3 className="text-xl font-medium text-gray-700">No data found</h3>
                                                <p className="text-sm text-gray-500 text-center mt-2 max-w-md">
                                                    No department sales data is available for the selected filters. Try
                                                    adjusting your filters or selecting a different date range.
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
