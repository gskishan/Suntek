import { useState, useMemo, useRef, useEffect } from "react";
import {
    ChevronDown,
    ChevronRight,
    TrendingUp,
    DollarSign,
    Package,
    Download,
    ExternalLink,
    Calendar,
    User,
    Building,
    MapPin,
    X,
    ChevronUp,
} from "lucide-react";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { Collapsible, CollapsibleContent, CollapsibleTrigger } from "@/components/ui/collapsible";
import { Tooltip, TooltipContent, TooltipTrigger } from "@/components/ui/tooltip";
import { Badge } from "@/components/ui/badge";
import { Card } from "@/components/ui/card";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Button } from "@/components/ui/button";
import { cn } from "@/lib/utils";

// Interfaces for the data structure
interface SalesOrder {
    name: string;
    customer: string;
    creation: string;
    type_of_case: string;
    status: string;
    grand_total: number;
    territory: string;
    state: string | null;
    district: string | null;
    district_name: string | null;
    city: string | null;
    department: string | null;
}

interface DistrictData {
    district: string | null;
    district_name: string | null;
    total_amount: number;
    count: number;
    orders: SalesOrder[];
}

interface CityData {
    city: string | null;
    total_amount: number;
    count: number;
    districts: DistrictData[];
}

interface TerritoryData {
    territory: string;
    total_amount: number;
    count: number;
    cities: CityData[];
}

interface StateData {
    state: string | null;
    total_amount: number;
    count: number;
    territories: TerritoryData[];
}

interface HierarchicalDataTableProps {
    data: StateData[];
}

export const HierarchicalDataTable = ({ data }: HierarchicalDataTableProps) => {
    // Create refs to access row component states
    const stateRowRefs = useRef<Map<string, (expanded: boolean) => void>>(new Map());
    const territoryRowRefs = useRef<Map<string, (expanded: boolean) => void>>(new Map());
    const cityRowRefs = useRef<Map<string, (expanded: boolean) => void>>(new Map());
    const districtRowRefs = useRef<Map<string, (expanded: boolean) => void>>(new Map());

    // State to track full expansion/collapse operation
    const [isFullExpansion, setIsFullExpansion] = useState(false);

    // Normalize data to merge duplicate "Unspecified State" rows
    const normalizedData = useMemo(() => {
        // Make a deep copy of the data to avoid mutating the original
        const dataCopy: StateData[] = JSON.parse(JSON.stringify(data));

        // Check if we have more than one "Unspecified State" row
        const unspecifiedStateRows = dataCopy.filter((state) => !state.state || state.state.trim() === "");

        if (unspecifiedStateRows.length <= 1) {
            return dataCopy; // No duplicates, return as is
        }

        // Remove all "Unspecified State" rows from the data
        const filteredData = dataCopy.filter((state) => state.state && state.state.trim() !== "");

        // Create a merged row by combining all unspecified rows
        const mergedRow: StateData = {
            state: null,
            total_amount: 0,
            count: 0,
            territories: [],
        };

        // Combine data from all unspecified rows
        unspecifiedStateRows.forEach((stateRow) => {
            mergedRow.total_amount += stateRow.total_amount;
            mergedRow.count += stateRow.count;

            // Merge territories
            stateRow.territories.forEach((territory) => {
                // Check if this territory already exists in the merged row
                const existingTerritory = mergedRow.territories.find((t) => t.territory === territory.territory);

                if (existingTerritory) {
                    // Merge into existing territory
                    existingTerritory.total_amount += territory.total_amount;
                    existingTerritory.count += territory.count;

                    // Merge cities
                    territory.cities.forEach((city) => {
                        const existingCity = existingTerritory.cities.find(
                            (c) => (!c.city && !city.city) || c.city === city.city,
                        );

                        if (existingCity) {
                            // Merge into existing city
                            existingCity.total_amount += city.total_amount;
                            existingCity.count += city.count;

                            // Merge districts
                            city.districts.forEach((district) => {
                                const existingDistrict = existingCity.districts.find(
                                    (d) => (!d.district && !district.district) || d.district === district.district,
                                );

                                if (existingDistrict) {
                                    // Merge into existing district
                                    existingDistrict.total_amount += district.total_amount;
                                    existingDistrict.count += district.count;

                                    // Combine orders
                                    existingDistrict.orders = [...existingDistrict.orders, ...district.orders];
                                } else {
                                    // Add as new district
                                    existingCity.districts.push(district);
                                }
                            });
                        } else {
                            // Add as new city
                            existingTerritory.cities.push(city);
                        }
                    });
                } else {
                    // Add as new territory
                    mergedRow.territories.push(territory);
                }
            });
        });

        // Add the merged row to the filtered data
        filteredData.push(mergedRow);

        return filteredData;
    }, [data]);

    // Function to get the base ERP URL for direct links
    const getERPUrl = useMemo(() => {
        return () => {
            // Use the current origin (host) as the base URL for ERP links
            return window.location.origin;
        };
    }, []);

    // Function to map department names to their acronyms
    const getDepartmentAcronym = useMemo(() => {
        return (department: string | null) => {
            if (!department) return "None";

            switch (department) {
                case "Domestic (Residential) Sales Team - SESP":
                    return "DOMESTIC";
                case "Commercial & Industrial (C&I) - SESP":
                    return "C&I";
                case "Channel Partner - SESP":
                    return "CHP";
                default:
                    return department === "not defined" ? "None" : "Other";
            }
        };
    }, []);

    // Function to get a color for the department badge
    const getDepartmentColor = useMemo(() => {
        return (department: string | null) => {
            const acronym = getDepartmentAcronym(department);
            const colors: { [key: string]: string } = {
                DOMESTIC: "bg-blue-100 text-blue-800",
                "C&I": "bg-emerald-100 text-emerald-800",
                CHP: "bg-indigo-100 text-indigo-800",
                None: "bg-gray-100 text-gray-800",
                Other: "bg-pink-100 text-pink-800",
            };
            return colors[acronym] || "bg-gray-100 text-gray-800";
        };
    }, [getDepartmentAcronym]);

    // Functions to register row components for expand/collapse functionality
    const registerStateRow = (key: string, setExpandedFn: (expanded: boolean) => void) => {
        stateRowRefs.current.set(key, setExpandedFn);
    };

    const registerTerritoryRow = (key: string, setExpandedFn: (expanded: boolean) => void) => {
        territoryRowRefs.current.set(key, setExpandedFn);
    };

    const registerCityRow = (key: string, setExpandedFn: (expanded: boolean) => void) => {
        cityRowRefs.current.set(key, setExpandedFn);
    };

    const registerDistrictRow = (key: string, setExpandedFn: (expanded: boolean) => void) => {
        districtRowRefs.current.set(key, setExpandedFn);
    };

    // Functions to expand or collapse all rows
    const expandAll = () => {
        setIsFullExpansion(true);

        // Expand all state rows immediately
        stateRowRefs.current.forEach((setExpanded) => setExpanded(true));
        // The child rows will be expanded by the useEffect in each component
    };

    const collapseAll = () => {
        setIsFullExpansion(false);
        stateRowRefs.current.forEach((setExpanded) => setExpanded(false));
        territoryRowRefs.current.forEach((setExpanded) => setExpanded(false));
        cityRowRefs.current.forEach((setExpanded) => setExpanded(false));
        districtRowRefs.current.forEach((setExpanded) => setExpanded(false));
    };

    // Helper functions
    const getLocationName = useMemo(() => {
        return (
            value: string | null,
            type: "state" | "city" | "district" | "territory",
            districtName?: string | null,
        ) => {
            // Added more robust check for empty values
            if (!value || value.trim() === "") {
                // Return a consistent value for all null/empty cases
                return `Unspecified ${type.charAt(0).toUpperCase() + type.slice(1)}`;
            }
            if (type === "district" && districtName) return districtName;
            if (type === "territory") return `${value} (Zone)`;
            return value;
        };
    }, []);

    const getStatusColor = useMemo(() => {
        return (status: string) => {
            const colors: { [key: string]: string } = {
                "To Deliver and Bill": "bg-yellow-100 text-yellow-800",
                Completed: "bg-green-100 text-green-800",
                Closed: "bg-gray-100 text-gray-800",
                Draft: "bg-blue-100 text-blue-800",
            };
            return colors[status] || "bg-gray-100 text-gray-800";
        };
    }, []);

    const getTypeColor = useMemo(() => {
        return (type: string) => {
            const colors: { [key: string]: string } = {
                Subsidy: "bg-purple-100 text-purple-800",
                "Non Subsidy": "bg-orange-100 text-orange-800",
            };
            return colors[type] || "bg-gray-100 text-gray-800";
        };
    }, []);

    // Helper function to create unique keys even for null values
    const createUniqueKey = useMemo(() => {
        return (value: string | null, prefix: string, index: number): string => {
            if (value) return `${prefix}-${value}`;
            return `${prefix}-unknown-${index}`;
        };
    }, []);

    // Format currency
    const formatCurrency = useMemo(() => {
        return (amount: number) => {
            return `₹${amount.toLocaleString()}`;
        };
    }, []);

    // Calculate average value
    const calculateAverage = useMemo(() => {
        return (total: number, count: number) => {
            return count > 0 ? total / count : 0;
        };
    }, []);

    // Handle export to CSV
    const handleExportCSV = () => {
        // Create flat data array for CSV export
        const flatData: any[] = [];

        normalizedData.forEach((stateData) => {
            const stateName = getLocationName(stateData.state, "state");

            // Add state level summary
            flatData.push({
                level: "State",
                name: stateName,
                orders: stateData.count,
                revenue: stateData.total_amount,
                average: stateData.count > 0 ? stateData.total_amount / stateData.count : 0,
            });

            stateData.territories.forEach((territoryData) => {
                const territoryName = getLocationName(territoryData.territory, "territory");

                // Add territory level summary
                flatData.push({
                    level: "Territory",
                    name: territoryName,
                    state: stateName,
                    orders: territoryData.count,
                    revenue: territoryData.total_amount,
                    average: territoryData.count > 0 ? territoryData.total_amount / territoryData.count : 0,
                });

                territoryData.cities.forEach((cityData) => {
                    const cityName = getLocationName(cityData.city, "city");

                    // Add city level summary
                    flatData.push({
                        level: "City",
                        name: cityName,
                        territory: territoryName,
                        state: stateName,
                        orders: cityData.count,
                        revenue: cityData.total_amount,
                        average: cityData.count > 0 ? cityData.total_amount / cityData.count : 0,
                    });

                    cityData.districts.forEach((districtData) => {
                        const districtName = getLocationName(
                            districtData.district,
                            "district",
                            districtData.district_name,
                        );

                        // Add district level summary
                        flatData.push({
                            level: "District",
                            name: districtName,
                            city: cityName,
                            territory: territoryName,
                            state: stateName,
                            orders: districtData.count,
                            revenue: districtData.total_amount,
                            average: districtData.count > 0 ? districtData.total_amount / districtData.count : 0,
                        });

                        // Add individual orders
                        districtData.orders.forEach((order) => {
                            flatData.push({
                                level: "Order",
                                name: order.name,
                                customer: order.customer,
                                district: districtName,
                                city: cityName,
                                territory: territoryName,
                                state: stateName,
                                amount: order.grand_total,
                                date: new Date(order.creation).toLocaleDateString(),
                                status: order.status,
                                type: order.type_of_case,
                            });
                        });
                    });
                });
            });
        });

        // Convert to CSV
        const headers = Object.keys(flatData[0] || {}).join(",");
        const csvRows = flatData.map((row) =>
            Object.values(row)
                .map((value) => (typeof value === "string" ? `"${value.replace(/"/g, '""')}"` : value))
                .join(","),
        );

        const csvContent = [headers, ...csvRows].join("\n");
        const blob = new Blob([csvContent], { type: "text/csv;charset=utf-8;" });
        const url = URL.createObjectURL(blob);

        // Create download link and trigger download
        const link = document.createElement("a");
        link.setAttribute("href", url);
        link.setAttribute("download", `sales_data_${new Date().toISOString().split("T")[0]}.csv`);
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
    };

    // State for sales order modal
    const [selectedOrder, setSelectedOrder] = useState<SalesOrder | null>(null);

    // Handle opening and closing the modal
    const handleOrderClick = (order: SalesOrder) => {
        setSelectedOrder(order);
    };

    const closeOrderDetails = () => {
        setSelectedOrder(null);
    };

    return (
        <>
            <Card className="overflow-hidden border border-gray-200 shadow-sm">
                <div className="p-2 flex justify-end gap-2 border-b">
                    <Button
                        variant="outline"
                        size="sm"
                        onClick={collapseAll}
                        className="flex items-center gap-1"
                    >
                        <ChevronRight className="h-4 w-4" /> Collapse All
                    </Button>
                    <Button
                        variant="outline"
                        size="sm"
                        onClick={expandAll}
                        className="flex items-center gap-1"
                    >
                        <ChevronDown className="h-4 w-4" /> Expand All
                    </Button>
                </div>
                <ScrollArea className="h-[calc(70vh-120px)] min-h-[300px]">
                    <div className="min-w-[750px]">
                        <Table className="w-full table-fixed">
                            <TableHeader className="bg-gray-50 sticky top-0 z-10">
                                <TableRow>
                                    <TableHead className="w-[300px]">Location</TableHead>
                                    <TableHead className="w-[150px]">Orders</TableHead>
                                    <TableHead className="w-[180px]">Total Revenue</TableHead>
                                    <TableHead className="w-[120px]">Avg. Order Value</TableHead>
                                </TableRow>
                            </TableHeader>
                            <TableBody>
                                {normalizedData.length === 0 ? (
                                    <TableRow>
                                        <TableCell
                                            colSpan={4}
                                            className="h-24 text-center"
                                        >
                                            <div className="flex flex-col items-center justify-center text-muted-foreground">
                                                <p>No sales data found.</p>
                                                <p className="text-sm">
                                                    Try adjusting the filters or refresh the data.
                                                </p>
                                            </div>
                                        </TableCell>
                                    </TableRow>
                                ) : (
                                    normalizedData.map((stateData, stateIndex) => (
                                        <StateRow
                                            key={createUniqueKey(stateData.state, "state", stateIndex)}
                                            stateData={stateData}
                                            stateIndex={stateIndex}
                                            getLocationName={getLocationName}
                                            formatCurrency={formatCurrency}
                                            calculateAverage={calculateAverage}
                                            createUniqueKey={createUniqueKey}
                                            getStatusColor={getStatusColor}
                                            getTypeColor={getTypeColor}
                                            registerRow={registerStateRow}
                                            isFullExpansion={isFullExpansion}
                                            getERPUrl={getERPUrl}
                                            getDepartmentAcronym={getDepartmentAcronym}
                                            getDepartmentColor={getDepartmentColor}
                                        />
                                    ))
                                )}
                            </TableBody>
                        </Table>
                    </div>
                </ScrollArea>
            </Card>

            {/* Order Details Modal - Custom implementation instead of Dialog */}
            {selectedOrder && (
                <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50">
                    <div className="bg-white rounded-lg shadow-lg w-full max-w-2xl mx-auto overflow-hidden">
                        <div className="flex items-center justify-between p-4 border-b">
                            <div>
                                <h3 className="text-lg font-semibold">Sales Order Details</h3>
                                <p className="text-sm text-gray-500">Viewing details for order {selectedOrder.name}</p>
                            </div>
                            <Button
                                variant="ghost"
                                size="icon"
                                onClick={closeOrderDetails}
                                className="rounded-full h-8 w-8"
                            >
                                <X className="h-4 w-4" />
                            </Button>
                        </div>

                        <div className="p-4 space-y-4">
                            <div className="grid grid-cols-2 gap-6">
                                <div className="flex items-center gap-2 text-sm">
                                    <User className="h-4 w-4 text-muted-foreground" />
                                    <span className="font-medium">Customer:</span>
                                    <span className="truncate">{selectedOrder.customer}</span>
                                </div>
                                <div className="flex items-center gap-2 text-sm">
                                    <Calendar className="h-4 w-4 text-muted-foreground" />
                                    <span className="font-medium">Date:</span>{" "}
                                    {new Date(selectedOrder.creation).toLocaleDateString()}
                                </div>
                                <div className="flex items-center gap-2 text-sm">
                                    <Building className="h-4 w-4 text-muted-foreground" />
                                    <span className="font-medium">Department:</span> {selectedOrder.department || "N/A"}
                                </div>
                                <div className="flex items-center gap-2 text-sm">
                                    <MapPin className="h-4 w-4 text-muted-foreground" />
                                    <span className="font-medium">Territory:</span> {selectedOrder.territory}
                                </div>
                                <div className="flex items-center gap-2 text-sm">
                                    <span className="font-medium">State:</span> {selectedOrder.state || "Unspecified"}
                                </div>
                                <div className="flex items-center gap-2 text-sm">
                                    <span className="font-medium">City:</span> {selectedOrder.city || "Unspecified"}
                                </div>
                            </div>

                            <div className="flex justify-between items-center mt-4 pt-4 border-t">
                                <div className="flex items-center gap-4">
                                    <Badge className={getStatusColor(selectedOrder.status)}>
                                        {selectedOrder.status}
                                    </Badge>
                                    <Badge className={getTypeColor(selectedOrder.type_of_case)}>
                                        {selectedOrder.type_of_case}
                                    </Badge>
                                </div>
                                <div className="text-lg font-bold">{formatCurrency(selectedOrder.grand_total)}</div>
                            </div>
                        </div>

                        <div className="p-4 border-t flex justify-end gap-2">
                            <Button
                                variant="outline"
                                onClick={closeOrderDetails}
                            >
                                Close
                            </Button>
                            <Button
                                className="flex items-center gap-2"
                                onClick={() =>
                                    window.open(`${getERPUrl()}/app/sales-order/${selectedOrder.name}`, "_blank")
                                }
                            >
                                <ExternalLink className="h-4 w-4" />
                                View in ERP
                            </Button>
                        </div>
                    </div>
                </div>
            )}
        </>
    );
};

interface StateRowProps {
    stateData: StateData;
    stateIndex: number;
    getLocationName: (
        value: string | null,
        type: "state" | "city" | "district" | "territory",
        districtName?: string | null,
    ) => string;
    formatCurrency: (amount: number) => string;
    calculateAverage: (total: number, count: number) => number;
    createUniqueKey: (value: string | null, prefix: string, index: number) => string;
    getStatusColor: (status: string) => string;
    getTypeColor: (type: string) => string;
    registerRow: (key: string, setExpandedFn: (expanded: boolean) => void) => void;
    isFullExpansion: boolean;
    getERPUrl: () => string;
    getDepartmentAcronym: (department: string | null) => string;
    getDepartmentColor: (department: string | null) => string;
}

const StateRow = ({
    stateData,
    stateIndex,
    getLocationName,
    formatCurrency,
    calculateAverage,
    createUniqueKey,
    getStatusColor,
    getTypeColor,
    registerRow,
    isFullExpansion,
    getERPUrl,
    getDepartmentAcronym,
    getDepartmentColor,
}: StateRowProps) => {
    const [isOpen, setIsOpen] = useState(false);
    const rowKey = createUniqueKey(stateData.state, "state", stateIndex);

    // Register this row with the parent component for expand/collapse control
    useRef(() => {
        registerRow(rowKey, setIsOpen);
    }).current();

    // Respond to full expansion flag
    useEffect(() => {
        if (isFullExpansion) {
            setIsOpen(true);
        }
    }, [isFullExpansion]);

    return (
        <>
            <TableRow className="bg-muted/30 hover:bg-muted font-medium">
                <TableCell>
                    <div
                        className="flex items-center w-full cursor-pointer"
                        onClick={() => setIsOpen(!isOpen)}
                    >
                        {isOpen ? (
                            <ChevronDown className="h-4 w-4 mr-2 inline transition-transform duration-200" />
                        ) : (
                            <ChevronRight className="h-4 w-4 mr-2 inline transition-transform duration-200" />
                        )}
                        {getLocationName(stateData.state, "state")}
                    </div>
                </TableCell>
                <TableCell>
                    <Tooltip>
                        <TooltipTrigger asChild>
                            <div className="flex items-center">
                                <Package className="h-4 w-4 mr-1.5" />
                                {stateData.count}
                            </div>
                        </TooltipTrigger>
                        <TooltipContent>
                            <p>Total number of orders in {getLocationName(stateData.state, "state")}</p>
                        </TooltipContent>
                    </Tooltip>
                </TableCell>
                <TableCell>
                    <Tooltip>
                        <TooltipTrigger asChild>
                            <div className="flex items-center">
                                <DollarSign className="h-4 w-4 mr-1.5" />
                                {formatCurrency(stateData.total_amount)}
                            </div>
                        </TooltipTrigger>
                        <TooltipContent>
                            <p>Total revenue from all orders in {getLocationName(stateData.state, "state")}</p>
                        </TooltipContent>
                    </Tooltip>
                </TableCell>
                <TableCell>
                    <Tooltip>
                        <TooltipTrigger asChild>
                            <div className="flex items-center">
                                <TrendingUp className="h-4 w-4 mr-1.5" />
                                {formatCurrency(calculateAverage(stateData.total_amount, stateData.count))}
                            </div>
                        </TooltipTrigger>
                        <TooltipContent>
                            <p>Average order value in {getLocationName(stateData.state, "state")}</p>
                        </TooltipContent>
                    </Tooltip>
                </TableCell>
            </TableRow>

            {/* Render territories in a separate row when expanded */}
            {isOpen &&
                stateData.territories.map((territoryData, territoryIndex) => (
                    <TerritoryRow
                        key={createUniqueKey(territoryData.territory, "territory", territoryIndex)}
                        territoryData={territoryData}
                        territoryIndex={territoryIndex}
                        getLocationName={getLocationName}
                        formatCurrency={formatCurrency}
                        calculateAverage={calculateAverage}
                        createUniqueKey={createUniqueKey}
                        getStatusColor={getStatusColor}
                        getTypeColor={getTypeColor}
                        registerRow={registerRow}
                        isFullExpansion={isFullExpansion}
                        getERPUrl={getERPUrl}
                        getDepartmentAcronym={getDepartmentAcronym}
                        getDepartmentColor={getDepartmentColor}
                    />
                ))}
        </>
    );
};

interface TerritoryRowProps {
    territoryData: TerritoryData;
    territoryIndex: number;
    getLocationName: (
        value: string | null,
        type: "state" | "city" | "district" | "territory",
        districtName?: string | null,
    ) => string;
    formatCurrency: (amount: number) => string;
    calculateAverage: (total: number, count: number) => number;
    createUniqueKey: (value: string | null, prefix: string, index: number) => string;
    getStatusColor: (status: string) => string;
    getTypeColor: (type: string) => string;
    registerRow: (key: string, setExpandedFn: (expanded: boolean) => void) => void;
    isFullExpansion: boolean;
    getERPUrl: () => string;
    getDepartmentAcronym: (department: string | null) => string;
    getDepartmentColor: (department: string | null) => string;
}

const TerritoryRow = ({
    territoryData,
    territoryIndex,
    getLocationName,
    formatCurrency,
    calculateAverage,
    createUniqueKey,
    getStatusColor,
    getTypeColor,
    registerRow,
    isFullExpansion,
    getERPUrl,
    getDepartmentAcronym,
    getDepartmentColor,
}: TerritoryRowProps) => {
    const [isOpen, setIsOpen] = useState(false);
    const rowKey = createUniqueKey(territoryData.territory, "territory", territoryIndex);

    // Register this row with the parent component for expand/collapse control
    useRef(() => {
        registerRow(rowKey, setIsOpen);
    }).current();

    // Respond to full expansion flag
    useEffect(() => {
        if (isFullExpansion) {
            setIsOpen(true);
        }
    }, [isFullExpansion]);

    return (
        <>
            <TableRow className="hover:bg-muted/50">
                <TableCell className="pl-8">
                    <div
                        className="flex items-center w-full cursor-pointer"
                        onClick={() => setIsOpen(!isOpen)}
                    >
                        {isOpen ? (
                            <ChevronDown className="h-4 w-4 mr-2 inline transition-transform duration-200" />
                        ) : (
                            <ChevronRight className="h-4 w-4 mr-2 inline transition-transform duration-200" />
                        )}
                        {getLocationName(territoryData.territory, "territory")}
                    </div>
                </TableCell>
                <TableCell>
                    <Tooltip>
                        <TooltipTrigger asChild>
                            <div className="flex items-center">
                                <Package className="h-4 w-4 mr-1.5" />
                                {territoryData.count}
                            </div>
                        </TooltipTrigger>
                        <TooltipContent>
                            <p>Total number of orders in {getLocationName(territoryData.territory, "territory")}</p>
                        </TooltipContent>
                    </Tooltip>
                </TableCell>
                <TableCell>
                    <Tooltip>
                        <TooltipTrigger asChild>
                            <div className="flex items-center">
                                <DollarSign className="h-4 w-4 mr-1.5" />
                                {formatCurrency(territoryData.total_amount)}
                            </div>
                        </TooltipTrigger>
                        <TooltipContent>
                            <p>
                                Total revenue from all orders in {getLocationName(territoryData.territory, "territory")}
                            </p>
                        </TooltipContent>
                    </Tooltip>
                </TableCell>
                <TableCell>
                    <Tooltip>
                        <TooltipTrigger asChild>
                            <div className="flex items-center">
                                <TrendingUp className="h-4 w-4 mr-1.5" />
                                {formatCurrency(calculateAverage(territoryData.total_amount, territoryData.count))}
                            </div>
                        </TooltipTrigger>
                        <TooltipContent>
                            <p>Average order value in {getLocationName(territoryData.territory, "territory")}</p>
                        </TooltipContent>
                    </Tooltip>
                </TableCell>
            </TableRow>

            {/* Render cities in a separate row when expanded */}
            {isOpen &&
                territoryData.cities.map((cityData, cityIndex) => (
                    <CityRow
                        key={createUniqueKey(cityData.city, "city", cityIndex)}
                        cityData={cityData}
                        cityIndex={cityIndex}
                        getLocationName={getLocationName}
                        formatCurrency={formatCurrency}
                        calculateAverage={calculateAverage}
                        createUniqueKey={createUniqueKey}
                        getStatusColor={getStatusColor}
                        getTypeColor={getTypeColor}
                        registerRow={registerRow}
                        isFullExpansion={isFullExpansion}
                        getERPUrl={getERPUrl}
                        getDepartmentAcronym={getDepartmentAcronym}
                        getDepartmentColor={getDepartmentColor}
                    />
                ))}
        </>
    );
};

interface CityRowProps {
    cityData: CityData;
    cityIndex: number;
    getLocationName: (
        value: string | null,
        type: "state" | "city" | "district" | "territory",
        districtName?: string | null,
    ) => string;
    formatCurrency: (amount: number) => string;
    calculateAverage: (total: number, count: number) => number;
    createUniqueKey: (value: string | null, prefix: string, index: number) => string;
    getStatusColor: (status: string) => string;
    getTypeColor: (type: string) => string;
    registerRow: (key: string, setExpandedFn: (expanded: boolean) => void) => void;
    isFullExpansion: boolean;
    getERPUrl: () => string;
    getDepartmentAcronym: (department: string | null) => string;
    getDepartmentColor: (department: string | null) => string;
}

const CityRow = ({
    cityData,
    cityIndex,
    getLocationName,
    formatCurrency,
    calculateAverage,
    createUniqueKey,
    getStatusColor,
    getTypeColor,
    registerRow,
    isFullExpansion,
    getERPUrl,
    getDepartmentAcronym,
    getDepartmentColor,
}: CityRowProps) => {
    const [isOpen, setIsOpen] = useState(false);
    const rowKey = createUniqueKey(cityData.city, "city", cityIndex);

    // Register this row with the parent component for expand/collapse control
    useRef(() => {
        registerRow(rowKey, setIsOpen);
    }).current();

    // Respond to full expansion flag
    useEffect(() => {
        if (isFullExpansion) {
            setIsOpen(true);
        }
    }, [isFullExpansion]);

    return (
        <>
            <TableRow className="hover:bg-muted/50">
                <TableCell className="pl-12">
                    <div
                        className="flex items-center w-full cursor-pointer"
                        onClick={() => setIsOpen(!isOpen)}
                    >
                        {isOpen ? (
                            <ChevronDown className="h-4 w-4 mr-2 inline transition-transform duration-200" />
                        ) : (
                            <ChevronRight className="h-4 w-4 mr-2 inline transition-transform duration-200" />
                        )}
                        {getLocationName(cityData.city, "city")}
                    </div>
                </TableCell>
                <TableCell>
                    <Tooltip>
                        <TooltipTrigger asChild>
                            <div className="flex items-center">
                                <Package className="h-4 w-4 mr-1.5" />
                                {cityData.count}
                            </div>
                        </TooltipTrigger>
                        <TooltipContent>
                            <p>Total number of orders in {getLocationName(cityData.city, "city")}</p>
                        </TooltipContent>
                    </Tooltip>
                </TableCell>
                <TableCell>
                    <Tooltip>
                        <TooltipTrigger asChild>
                            <div className="flex items-center">
                                <DollarSign className="h-4 w-4 mr-1.5" />
                                {formatCurrency(cityData.total_amount)}
                            </div>
                        </TooltipTrigger>
                        <TooltipContent>
                            <p>Total revenue from all orders in {getLocationName(cityData.city, "city")}</p>
                        </TooltipContent>
                    </Tooltip>
                </TableCell>
                <TableCell>
                    <Tooltip>
                        <TooltipTrigger asChild>
                            <div className="flex items-center">
                                <TrendingUp className="h-4 w-4 mr-1.5" />
                                {formatCurrency(calculateAverage(cityData.total_amount, cityData.count))}
                            </div>
                        </TooltipTrigger>
                        <TooltipContent>
                            <p>Average order value in {getLocationName(cityData.city, "city")}</p>
                        </TooltipContent>
                    </Tooltip>
                </TableCell>
            </TableRow>

            {/* Render districts in a separate row when expanded */}
            {isOpen &&
                cityData.districts.map((districtData, districtIndex) => (
                    <DistrictRow
                        key={createUniqueKey(districtData.district, "district", districtIndex)}
                        districtData={districtData}
                        districtIndex={districtIndex}
                        getLocationName={getLocationName}
                        formatCurrency={formatCurrency}
                        calculateAverage={calculateAverage}
                        createUniqueKey={createUniqueKey}
                        getStatusColor={getStatusColor}
                        getTypeColor={getTypeColor}
                        registerRow={registerRow}
                        isFullExpansion={isFullExpansion}
                        getERPUrl={getERPUrl}
                        getDepartmentAcronym={getDepartmentAcronym}
                        getDepartmentColor={getDepartmentColor}
                    />
                ))}
        </>
    );
};

interface DistrictRowProps {
    districtData: DistrictData;
    districtIndex: number;
    getLocationName: (
        value: string | null,
        type: "state" | "city" | "district" | "territory",
        districtName?: string | null,
    ) => string;
    formatCurrency: (amount: number) => string;
    calculateAverage: (total: number, count: number) => number;
    createUniqueKey: (value: string | null, prefix: string, index: number) => string;
    getStatusColor: (status: string) => string;
    getTypeColor: (type: string) => string;
    registerRow: (key: string, setExpandedFn: (expanded: boolean) => void) => void;
    isFullExpansion: boolean;
    getERPUrl: () => string;
    getDepartmentAcronym: (department: string | null) => string;
    getDepartmentColor: (department: string | null) => string;
}

const DistrictRow = ({
    districtData,
    districtIndex,
    getLocationName,
    formatCurrency,
    calculateAverage,
    createUniqueKey,
    getStatusColor,
    getTypeColor,
    registerRow,
    isFullExpansion,
    getERPUrl,
    getDepartmentAcronym,
    getDepartmentColor,
}: DistrictRowProps) => {
    const [isOpen, setIsOpen] = useState(false);
    const rowKey = createUniqueKey(districtData.district, "district", districtIndex);

    // Register this row with the parent component for expand/collapse control
    useRef(() => {
        registerRow(rowKey, setIsOpen);
    }).current();

    // Respond to full expansion flag
    useEffect(() => {
        if (isFullExpansion) {
            setIsOpen(true);
        }
    }, [isFullExpansion]);

    // State for sales order modal
    const [selectedOrder, setSelectedOrder] = useState<SalesOrder | null>(null);

    // Handle opening and closing the modal
    const handleOrderClick = (order: SalesOrder) => {
        setSelectedOrder(order);
    };

    const closeOrderDetails = () => {
        setSelectedOrder(null);
    };

    return (
        <>
            <TableRow className="hover:bg-muted/50">
                <TableCell className="pl-16">
                    <div
                        className="flex items-center w-full cursor-pointer"
                        onClick={() => setIsOpen(!isOpen)}
                    >
                        {isOpen ? (
                            <ChevronDown className="h-4 w-4 mr-2 inline transition-transform duration-200" />
                        ) : (
                            <ChevronRight className="h-4 w-4 mr-2 inline transition-transform duration-200" />
                        )}
                        {getLocationName(districtData.district, "district", districtData.district_name)}
                    </div>
                </TableCell>
                <TableCell>
                    <Tooltip>
                        <TooltipTrigger asChild>
                            <div className="flex items-center">
                                <Package className="h-4 w-4 mr-1.5" />
                                {districtData.count}
                            </div>
                        </TooltipTrigger>
                        <TooltipContent>
                            <p>
                                Total number of orders in{" "}
                                {getLocationName(districtData.district, "district", districtData.district_name)}
                            </p>
                        </TooltipContent>
                    </Tooltip>
                </TableCell>
                <TableCell>
                    <Tooltip>
                        <TooltipTrigger asChild>
                            <div className="flex items-center">
                                <DollarSign className="h-4 w-4 mr-1.5" />
                                {formatCurrency(districtData.total_amount)}
                            </div>
                        </TooltipTrigger>
                        <TooltipContent>
                            <p>
                                Total revenue from all orders in{" "}
                                {getLocationName(districtData.district, "district", districtData.district_name)}
                            </p>
                        </TooltipContent>
                    </Tooltip>
                </TableCell>
                <TableCell>
                    <Tooltip>
                        <TooltipTrigger asChild>
                            <div className="flex items-center">
                                <TrendingUp className="h-4 w-4 mr-1.5" />
                                {formatCurrency(calculateAverage(districtData.total_amount, districtData.count))}
                            </div>
                        </TooltipTrigger>
                        <TooltipContent>
                            <p>
                                Average order value in{" "}
                                {getLocationName(districtData.district, "district", districtData.district_name)}
                            </p>
                        </TooltipContent>
                    </Tooltip>
                </TableCell>
            </TableRow>

            {/* Render orders in a separate row when expanded */}
            {isOpen && (
                <TableRow>
                    <TableCell
                        colSpan={4}
                        className="p-0"
                    >
                        <div className="border-t border-b border-gray-200 bg-gray-50/50 py-2">
                            {districtData.orders.length > 0 ? (
                                <div className="px-10 mx-auto overflow-x-auto">
                                    <Table className="w-full table-fixed">
                                        <TableHeader className="bg-muted/20">
                                            <TableRow>
                                                <TableHead className="font-medium text-xs h-8 py-1 w-[15%]">
                                                    Order ID
                                                </TableHead>
                                                <TableHead className="font-medium text-xs h-8 py-1 w-[20%]">
                                                    Customer
                                                </TableHead>
                                                <TableHead className="font-medium text-xs h-8 py-1 w-[15%]">
                                                    Amount
                                                </TableHead>
                                                <TableHead className="font-medium text-xs h-8 py-1 w-[15%]">
                                                    Date
                                                </TableHead>
                                                <TableHead className="font-medium text-xs h-8 py-1 w-[35%] text-right">
                                                    Details
                                                </TableHead>
                                            </TableRow>
                                        </TableHeader>
                                        <TableBody>
                                            {districtData.orders.map((order, orderIndex) => (
                                                <TableRow
                                                    key={`order-${order.name}-${orderIndex}`}
                                                    className="hover:bg-muted/50 cursor-pointer"
                                                    onClick={() => handleOrderClick(order)}
                                                >
                                                    <TableCell
                                                        className="py-2 text-sm font-medium text-primary truncate"
                                                        title={order.name}
                                                    >
                                                        {order.name}
                                                    </TableCell>
                                                    <TableCell
                                                        className="py-2 text-sm truncate"
                                                        title={order.customer}
                                                    >
                                                        {order.customer}
                                                    </TableCell>
                                                    <TableCell className="py-2 text-sm whitespace-nowrap">
                                                        {formatCurrency(order.grand_total)}
                                                    </TableCell>
                                                    <TableCell className="py-2 text-sm whitespace-nowrap">
                                                        {new Date(order.creation).toLocaleDateString()}
                                                    </TableCell>
                                                    <TableCell className="py-2 text-sm text-right">
                                                        <div className="flex items-center justify-end gap-1">
                                                            <Badge
                                                                className={getDepartmentColor(order.department)}
                                                                variant="outline"
                                                                title={order.department || "None"}
                                                            >
                                                                {getDepartmentAcronym(order.department)}
                                                            </Badge>
                                                            <Badge
                                                                className={getTypeColor(order.type_of_case)}
                                                                variant="outline"
                                                                title={order.type_of_case}
                                                            >
                                                                {order.type_of_case}
                                                            </Badge>
                                                            <Badge
                                                                className={getStatusColor(order.status)}
                                                                title={order.status}
                                                            >
                                                                {order.status}
                                                            </Badge>
                                                        </div>
                                                    </TableCell>
                                                </TableRow>
                                            ))}
                                        </TableBody>
                                    </Table>
                                </div>
                            ) : (
                                <div className="px-20 py-4 text-center">
                                    <div className="flex flex-col items-center justify-center text-muted-foreground">
                                        <p>No orders found in this district</p>
                                    </div>
                                </div>
                            )}
                        </div>
                    </TableCell>
                </TableRow>
            )}

            {/* Order Details Modal - Custom implementation instead of Dialog */}
            {selectedOrder && (
                <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50">
                    <div className="bg-white rounded-lg shadow-lg w-full max-w-2xl mx-auto overflow-hidden">
                        <div className="flex items-center justify-between p-4 border-b">
                            <div>
                                <h3 className="text-lg font-semibold">Sales Order Details</h3>
                                <p className="text-sm text-gray-500">Viewing details for order {selectedOrder.name}</p>
                            </div>
                            <Button
                                variant="ghost"
                                size="icon"
                                onClick={closeOrderDetails}
                                className="rounded-full h-8 w-8"
                            >
                                <X className="h-4 w-4" />
                            </Button>
                        </div>

                        <div className="p-4 space-y-4">
                            <div className="grid grid-cols-2 gap-6">
                                <div className="flex items-center gap-2 text-sm">
                                    <User className="h-4 w-4 text-muted-foreground" />
                                    <span className="font-medium">Customer:</span>
                                    <span className="truncate">{selectedOrder.customer}</span>
                                </div>
                                <div className="flex items-center gap-2 text-sm">
                                    <Calendar className="h-4 w-4 text-muted-foreground" />
                                    <span className="font-medium">Date:</span>{" "}
                                    {new Date(selectedOrder.creation).toLocaleDateString()}
                                </div>
                                <div className="flex items-center gap-2 text-sm">
                                    <Building className="h-4 w-4 text-muted-foreground" />
                                    <span className="font-medium">Department:</span> {selectedOrder.department || "N/A"}
                                </div>
                                <div className="flex items-center gap-2 text-sm">
                                    <MapPin className="h-4 w-4 text-muted-foreground" />
                                    <span className="font-medium">Territory:</span> {selectedOrder.territory}
                                </div>
                                <div className="flex items-center gap-2 text-sm">
                                    <span className="font-medium">State:</span> {selectedOrder.state || "Unspecified"}
                                </div>
                                <div className="flex items-center gap-2 text-sm">
                                    <span className="font-medium">City:</span> {selectedOrder.city || "Unspecified"}
                                </div>
                            </div>

                            <div className="flex justify-between items-center mt-4 pt-4 border-t">
                                <div className="flex items-center gap-4">
                                    <Badge className={getStatusColor(selectedOrder.status)}>
                                        {selectedOrder.status}
                                    </Badge>
                                    <Badge className={getTypeColor(selectedOrder.type_of_case)}>
                                        {selectedOrder.type_of_case}
                                    </Badge>
                                </div>
                                <div className="text-lg font-bold">{formatCurrency(selectedOrder.grand_total)}</div>
                            </div>
                        </div>

                        <div className="p-4 border-t flex justify-end gap-2">
                            <Button
                                variant="outline"
                                onClick={closeOrderDetails}
                            >
                                Close
                            </Button>
                            <Button
                                className="flex items-center gap-2"
                                onClick={() =>
                                    window.open(`${getERPUrl()}/app/sales-order/${selectedOrder.name}`, "_blank")
                                }
                            >
                                <ExternalLink className="h-4 w-4" />
                                View in ERP
                            </Button>
                        </div>
                    </div>
                </div>
            )}
        </>
    );
};
