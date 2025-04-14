import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { Tooltip, TooltipContent, TooltipTrigger } from "@/components/ui/tooltip";
import {
    Building,
    Calendar,
    ChevronDown,
    ChevronLeft,
    ChevronRight,
    ChevronsLeft,
    ChevronsRight,
    DollarSign,
    ExternalLink,
    MapPin,
    Package,
    Search,
    TrendingUp,
    User,
    X,
} from "lucide-react";
import { useEffect, useMemo, useRef, useState } from "react";

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

const TableCellMetric = ({
    icon: Icon,
    value,
    tooltip,
}: {
    icon: React.ElementType;
    value: React.ReactNode;
    tooltip: string;
}) => {
    return (
        <Tooltip>
            <TooltipTrigger asChild>
                <div className="inline-flex items-center w-auto">
                    <Icon className="h-4 w-4 mr-1.5" />
                    {value}
                </div>
            </TooltipTrigger>
            <TooltipContent
                side="top"
                align="center"
                sideOffset={5}
            >
                <p>{tooltip}</p>
            </TooltipContent>
        </Tooltip>
    );
};

export const HierarchicalDataTable = ({ data }: HierarchicalDataTableProps) => {
    const stateRowRefs = useRef<Map<string, (expanded: boolean) => void>>(new Map());
    const territoryRowRefs = useRef<Map<string, (expanded: boolean) => void>>(new Map());
    const cityRowRefs = useRef<Map<string, (expanded: boolean) => void>>(new Map());
    const districtRowRefs = useRef<Map<string, (expanded: boolean) => void>>(new Map());

    const [isFullExpansion, setIsFullExpansion] = useState(false);
    const [searchQuery, setSearchQuery] = useState<string>("");

    const normalizedData = useMemo(() => {
        const dataCopy: StateData[] = JSON.parse(JSON.stringify(data));

        const unspecifiedStateRows = dataCopy.filter((state) => !state.state || state.state.trim() === "");

        if (unspecifiedStateRows.length <= 1) {
            return dataCopy;
        }

        const filteredData = dataCopy.filter((state) => state.state && state.state.trim() !== "");

        const mergedRow: StateData = {
            state: null,
            total_amount: 0,
            count: 0,
            territories: [],
        };

        unspecifiedStateRows.forEach((stateRow) => {
            mergedRow.total_amount += stateRow.total_amount;
            mergedRow.count += stateRow.count;

            stateRow.territories.forEach((territory) => {
                const existingTerritory = mergedRow.territories.find((t) => t.territory === territory.territory);

                if (existingTerritory) {
                    existingTerritory.total_amount += territory.total_amount;
                    existingTerritory.count += territory.count;

                    territory.cities.forEach((city) => {
                        const existingCity = existingTerritory.cities.find(
                            (c) => (!c.city && !city.city) || c.city === city.city,
                        );

                        if (existingCity) {
                            existingCity.total_amount += city.total_amount;
                            existingCity.count += city.count;

                            city.districts.forEach((district) => {
                                const existingDistrict = existingCity.districts.find(
                                    (d) => (!d.district && !district.district) || d.district === district.district,
                                );

                                if (existingDistrict) {
                                    existingDistrict.total_amount += district.total_amount;
                                    existingDistrict.count += district.count;

                                    existingDistrict.orders = [...existingDistrict.orders, ...district.orders];
                                } else {
                                    existingCity.districts.push(district);
                                }
                            });
                        } else {
                            existingTerritory.cities.push(city);
                        }
                    });
                } else {
                    mergedRow.territories.push(territory);
                }
            });
        });

        filteredData.push(mergedRow);

        return filteredData;
    }, [data]);

    const getERPUrl = useMemo(() => {
        return () => {
            return window.location.origin;
        };
    }, []);

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

    const registerStateRow = (key: string, setExpandedFn: (expanded: boolean) => void) => {
        stateRowRefs.current.set(key, setExpandedFn);
    };

    const expandAll = () => {
        setIsFullExpansion(true);

        stateRowRefs.current.forEach((setExpanded) => setExpanded(true));
    };

    const collapseAll = () => {
        setIsFullExpansion(false);
        stateRowRefs.current.forEach((setExpanded) => setExpanded(false));
        territoryRowRefs.current.forEach((setExpanded) => setExpanded(false));
        cityRowRefs.current.forEach((setExpanded) => setExpanded(false));
        districtRowRefs.current.forEach((setExpanded) => setExpanded(false));
    };

    const getLocationName = useMemo(() => {
        return (
            value: string | null,
            type: "state" | "city" | "district" | "territory",
            districtName?: string | null,
        ) => {
            if (!value || value.trim() === "") {
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
                Cancelled: "bg-rose-100 text-rose-800",
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

    const createUniqueKey = useMemo(() => {
        return (value: string | null, prefix: string, index: number): string => {
            if (value) return `${prefix}-${value}`;
            return `${prefix}-unknown-${index}`;
        };
    }, []);

    const formatCurrency = useMemo(() => {
        return (amount: number) => {
            return `₹${amount.toLocaleString()}`;
        };
    }, []);

    const calculateAverage = useMemo(() => {
        return (total: number, count: number) => {
            return count > 0 ? total / count : 0;
        };
    }, []);

    const [selectedOrder, setSelectedOrder] = useState<SalesOrder | null>(null);

    const closeOrderDetails = () => {
        setSelectedOrder(null);
    };

    const filterOrders = (order: SalesOrder) => {
        if (!searchQuery.trim()) return true;

        const searchTerms = searchQuery
            .toLowerCase()
            .split(",")
            .map((term) => term.trim())
            .filter((term) => term);

        if (searchTerms.length === 0) return true;

        return searchTerms.every((term) => {
            if (term.startsWith(">") || term.startsWith("<") || term.startsWith("=")) {
                const operator = term.charAt(0);
                const amountStr = term.substring(1);
                const amount = parseFloat(amountStr);

                if (!isNaN(amount)) {
                    if (operator === ">") return order.grand_total > amount;
                    if (operator === "<") return order.grand_total < amount;
                    if (operator === "=") return order.grand_total === amount;
                }
            }

            return (
                order.name.toLowerCase().includes(term) ||
                order.customer.toLowerCase().includes(term) ||
                (order.type_of_case?.toLowerCase() || "").includes(term) ||
                (order.department?.toLowerCase() || "").includes(term) ||
                order.status.toLowerCase().includes(term) ||
                order.grand_total.toString().includes(term) ||
                (order.city?.toLowerCase() || "").includes(term) ||
                (order.state?.toLowerCase() || "").includes(term) ||
                order.territory.toLowerCase().includes(term) ||
                (order.district?.toLowerCase() || "").includes(term) ||
                (order.district_name?.toLowerCase() || "").includes(term)
            );
        });
    };

    const filteredData = useMemo(() => {
        if (!searchQuery.trim()) return normalizedData;

        if (searchQuery.trim()) {
            setTimeout(() => {
                expandAll();
            }, 0);
        }

        return normalizedData
            .map((stateData) => {
                // Create a deep copy of the state data
                const filteredState = {
                    ...stateData,
                    territories: stateData.territories
                        .map((territory) => {
                            // Create a deep copy of the territory data
                            const filteredTerritory = {
                                ...territory,
                                cities: territory.cities
                                    .map((city) => {
                                        // Create a deep copy of the city data
                                        const filteredCity = {
                                            ...city,
                                            districts: city.districts
                                                .map((district) => {
                                                    // Filter orders and create a deep copy of the district data
                                                    const filteredOrders = district.orders.filter(filterOrders);
                                                    return {
                                                        ...district,
                                                        orders: filteredOrders,
                                                        // Update count based on filtered orders
                                                        count: filteredOrders.length,
                                                        // Update total_amount based on filtered orders
                                                        total_amount: filteredOrders.reduce(
                                                            (sum, order) => sum + (order.grand_total || 0),
                                                            0,
                                                        ),
                                                    };
                                                })
                                                .filter((district) => district.orders.length > 0),
                                        };

                                        // Update city count and total_amount based on filtered districts
                                        const districtCount = filteredCity.districts.reduce(
                                            (sum, district) => sum + district.count,
                                            0,
                                        );
                                        const districtTotal = filteredCity.districts.reduce(
                                            (sum, district) => sum + district.total_amount,
                                            0,
                                        );

                                        return {
                                            ...filteredCity,
                                            count: districtCount,
                                            total_amount: districtTotal,
                                        };
                                    })
                                    .filter((city) => city.districts.length > 0),
                            };

                            // Update territory count and total_amount based on filtered cities
                            const cityCount = filteredTerritory.cities.reduce((sum, city) => sum + city.count, 0);
                            const cityTotal = filteredTerritory.cities.reduce(
                                (sum, city) => sum + city.total_amount,
                                0,
                            );

                            return {
                                ...filteredTerritory,
                                count: cityCount,
                                total_amount: cityTotal,
                            };
                        })
                        .filter((territory) => territory.cities.length > 0),
                };

                // Update state count and total_amount based on filtered territories
                const territoryCount = filteredState.territories.reduce((sum, territory) => sum + territory.count, 0);
                const territoryTotal = filteredState.territories.reduce(
                    (sum, territory) => sum + territory.total_amount,
                    0,
                );

                return {
                    ...filteredState,
                    count: territoryCount,
                    total_amount: territoryTotal,
                };
            })
            .filter((state) => state.territories.length > 0);
    }, [normalizedData, searchQuery, expandAll]);

    const toggleExpansion = () => {
        if (isFullExpansion) {
            collapseAll();
        } else {
            expandAll();
        }
    };

    return (
        <>
            <Card className="overflow-hidden border border-gray-200 shadow-sm rounded-lg">
                <div className="p-2 flex justify-between items-center border-b">
                    <div className="flex items-center gap-4">
                        <div className="relative w-96">
                            <Search className="absolute left-2 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
                            <Input
                                placeholder="Search by ID, customer, status, amount or location..."
                                value={searchQuery}
                                onChange={(e) => setSearchQuery(e.target.value)}
                                className="pl-8 h-9"
                            />
                            {searchQuery.trim() && (
                                <>
                                    <div className="absolute right-2 top-1/2 transform -translate-y-1/2 text-xs text-gray-500 bg-gray-100 px-2 py-0.5 rounded">
                                        {filteredData.reduce((total, state) => total + state.count, 0)} items
                                    </div>
                                    <Button
                                        variant="ghost"
                                        size="sm"
                                        onClick={() => setSearchQuery("")}
                                        className="absolute right-10 top-1/2 transform -translate-y-1/2 h-6 w-6 p-0"
                                    >
                                        <X className="h-4 w-4" />
                                    </Button>
                                </>
                            )}
                        </div>
                        <Badge
                            variant="outline"
                            className="h-9 px-3 flex items-center"
                        >
                            Showing {filteredData.reduce((total, state) => total + state.count, 0)} items
                        </Badge>
                    </div>
                    <Button
                        variant="outline"
                        size="sm"
                        onClick={toggleExpansion}
                        className="flex items-center gap-1"
                    >
                        {isFullExpansion ? (
                            <>
                                <ChevronRight className="h-4 w-4 transition-transform duration-300" /> Collapse All
                            </>
                        ) : (
                            <>
                                <ChevronDown className="h-4 w-4 transition-transform duration-300" /> Expand All
                            </>
                        )}
                    </Button>
                </div>
                <ScrollArea className="h-[calc(80vh-140px)] min-h-[500px]">
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
                                {filteredData.length === 0 ? (
                                    <TableRow>
                                        <TableCell
                                            colSpan={4}
                                            className="h-24 text-center"
                                        >
                                            <div className="flex flex-col items-center justify-center text-muted-foreground">
                                                <p>No sales data found.</p>
                                                <p className="text-sm">
                                                    {searchQuery.trim()
                                                        ? "No results match your search. Try a different query."
                                                        : "Try adjusting the filters or refresh the data."}
                                                </p>
                                            </div>
                                        </TableCell>
                                    </TableRow>
                                ) : (
                                    filteredData.map((stateData, stateIndex) => (
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

    useRef(() => {
        registerRow(rowKey, setIsOpen);
    }).current();

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
                        <ChevronRight
                            className={`h-4 w-4 mr-2 inline transition-transform duration-300 ease-in-out ${
                                isOpen ? "rotate-90" : "rotate-0"
                            }`}
                        />
                        {getLocationName(stateData.state, "state")}
                    </div>
                </TableCell>
                <TableCell>
                    <TableCellMetric
                        icon={Package}
                        value={stateData.count}
                        tooltip={`Total number of orders in ${getLocationName(stateData.state, "state")}`}
                    />
                </TableCell>
                <TableCell>
                    <TableCellMetric
                        icon={DollarSign}
                        value={formatCurrency(stateData.total_amount)}
                        tooltip={`Total revenue from all orders in ${getLocationName(stateData.state, "state")}`}
                    />
                </TableCell>
                <TableCell>
                    <TableCellMetric
                        icon={TrendingUp}
                        value={formatCurrency(calculateAverage(stateData.total_amount, stateData.count))}
                        tooltip={`Average order value in ${getLocationName(stateData.state, "state")}`}
                    />
                </TableCell>
            </TableRow>

            <TableRow
                className={`transition-all duration-300 ease-in-out overflow-hidden ${isOpen ? "opacity-100" : "opacity-0 h-0"}`}
            >
                <TableCell
                    colSpan={4}
                    className={`p-0 ${!isOpen ? "py-0" : ""}`}
                >
                    <div
                        className={`overflow-hidden transition-all duration-300 ease-in-out ${isOpen ? "max-h-[5000px]" : "max-h-0"}`}
                    >
                        <Table className="w-full">
                            <TableBody>
                                {stateData.territories.map((territoryData, territoryIndex) => (
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
                            </TableBody>
                        </Table>
                    </div>
                </TableCell>
            </TableRow>
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

    useRef(() => {
        registerRow(rowKey, setIsOpen);
    }).current();

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
                        <ChevronRight
                            className={`h-4 w-4 mr-2 inline transition-transform duration-300 ease-in-out ${
                                isOpen ? "rotate-90" : "rotate-0"
                            }`}
                        />
                        {getLocationName(territoryData.territory, "territory")}
                    </div>
                </TableCell>
                <TableCell>
                    <TableCellMetric
                        icon={Package}
                        value={territoryData.count}
                        tooltip={`Total number of orders in ${getLocationName(territoryData.territory, "territory")}`}
                    />
                </TableCell>
                <TableCell>
                    <TableCellMetric
                        icon={DollarSign}
                        value={formatCurrency(territoryData.total_amount)}
                        tooltip={`Total revenue from all orders in ${getLocationName(territoryData.territory, "territory")}`}
                    />
                </TableCell>
                <TableCell>
                    <TableCellMetric
                        icon={TrendingUp}
                        value={formatCurrency(calculateAverage(territoryData.total_amount, territoryData.count))}
                        tooltip={`Average order value in ${getLocationName(territoryData.territory, "territory")}`}
                    />
                </TableCell>
            </TableRow>

            <TableRow
                className={`transition-all duration-300 ease-in-out overflow-hidden ${isOpen ? "opacity-100" : "opacity-0 h-0"}`}
            >
                <TableCell
                    colSpan={4}
                    className={`p-0 ${!isOpen ? "py-0" : ""}`}
                >
                    <div
                        className={`overflow-hidden transition-all duration-300 ease-in-out ${isOpen ? "max-h-[5000px]" : "max-h-0"}`}
                    >
                        <Table className="w-full">
                            <TableBody>
                                {territoryData.cities.map((cityData, cityIndex) => (
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
                            </TableBody>
                        </Table>
                    </div>
                </TableCell>
            </TableRow>
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

    useRef(() => {
        registerRow(rowKey, setIsOpen);
    }).current();

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
                        <ChevronRight
                            className={`h-4 w-4 mr-2 inline transition-transform duration-300 ease-in-out ${
                                isOpen ? "rotate-90" : "rotate-0"
                            }`}
                        />
                        {getLocationName(cityData.city, "city")}
                    </div>
                </TableCell>
                <TableCell>
                    <TableCellMetric
                        icon={Package}
                        value={cityData.count}
                        tooltip={`Total number of orders in ${getLocationName(cityData.city, "city")}`}
                    />
                </TableCell>
                <TableCell>
                    <TableCellMetric
                        icon={DollarSign}
                        value={formatCurrency(cityData.total_amount)}
                        tooltip={`Total revenue from all orders in ${getLocationName(cityData.city, "city")}`}
                    />
                </TableCell>
                <TableCell>
                    <TableCellMetric
                        icon={TrendingUp}
                        value={formatCurrency(calculateAverage(cityData.total_amount, cityData.count))}
                        tooltip={`Average order value in ${getLocationName(cityData.city, "city")}`}
                    />
                </TableCell>
            </TableRow>

            <TableRow
                className={`transition-all duration-300 ease-in-out overflow-hidden ${isOpen ? "opacity-100" : "opacity-0 h-0"}`}
            >
                <TableCell
                    colSpan={4}
                    className={`p-0 ${!isOpen ? "py-0" : ""}`}
                >
                    <div
                        className={`overflow-hidden transition-all duration-300 ease-in-out ${isOpen ? "max-h-[5000px]" : "max-h-0"}`}
                    >
                        <Table className="w-full">
                            <TableBody>
                                {cityData.districts.map((districtData, districtIndex) => (
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
                            </TableBody>
                        </Table>
                    </div>
                </TableCell>
            </TableRow>
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

    const [currentPage, setCurrentPage] = useState(1);
    const ordersPerPage = 20;

    const totalPages = Math.ceil(districtData.orders.length / ordersPerPage);

    const indexOfLastOrder = currentPage * ordersPerPage;
    const indexOfFirstOrder = indexOfLastOrder - ordersPerPage;
    const currentOrders = districtData.orders.slice(indexOfFirstOrder, indexOfLastOrder);

    const previousPage = () => {
        setCurrentPage((prev) => Math.max(1, prev - 1));
    };

    const nextPage = () => {
        setCurrentPage((prev) => Math.min(totalPages, prev + 1));
    };

    const firstPage = () => {
        setCurrentPage(1);
    };

    const lastPage = () => {
        setCurrentPage(totalPages);
    };

    const rowKey = createUniqueKey(districtData.district, "district", districtIndex);

    useRef(() => {
        registerRow(rowKey, setIsOpen);
    }).current();

    useEffect(() => {
        if (isFullExpansion) {
            setIsOpen(true);
        }
    }, [isFullExpansion]);

    const [selectedOrder, setSelectedOrder] = useState<SalesOrder | null>(null);

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
                        <ChevronRight
                            className={`h-4 w-4 mr-2 inline transition-transform duration-300 ease-in-out ${
                                isOpen ? "rotate-90" : "rotate-0"
                            }`}
                        />
                        {getLocationName(districtData.district, "district", districtData.district_name)}
                    </div>
                </TableCell>
                <TableCell>
                    <TableCellMetric
                        icon={Package}
                        value={districtData.count}
                        tooltip={`Total number of orders in ${getLocationName(districtData.district, "district", districtData.district_name)}`}
                    />
                </TableCell>
                <TableCell>
                    <TableCellMetric
                        icon={DollarSign}
                        value={formatCurrency(districtData.total_amount)}
                        tooltip={`Total revenue from all orders in ${getLocationName(districtData.district, "district", districtData.district_name)}`}
                    />
                </TableCell>
                <TableCell>
                    <TableCellMetric
                        icon={TrendingUp}
                        value={formatCurrency(calculateAverage(districtData.total_amount, districtData.count))}
                        tooltip={`Average order value in ${getLocationName(districtData.district, "district", districtData.district_name)}`}
                    />
                </TableCell>
            </TableRow>

            <TableRow
                className={`transition-all duration-300 ease-in-out overflow-hidden ${isOpen ? "opacity-100" : "opacity-0 h-0"}`}
            >
                <TableCell
                    colSpan={4}
                    className={`p-0 ${!isOpen ? "py-0" : ""}`}
                >
                    <div
                        className={`overflow-hidden transition-all duration-300 ease-in-out ${isOpen ? "max-h-[5000px]" : "max-h-0"}`}
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
                                            {currentOrders.map((order, orderIndex) => (
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

                                    {totalPages > 1 && (
                                        <div className="flex items-center justify-between mt-3 mb-1 px-2">
                                            <div className="text-sm text-muted-foreground">
                                                Showing {indexOfFirstOrder + 1}-
                                                {Math.min(indexOfLastOrder, districtData.orders.length)} of{" "}
                                                {districtData.orders.length} orders
                                            </div>
                                            <div className="flex items-center space-x-2">
                                                <Button
                                                    variant="outline"
                                                    size="icon"
                                                    className="h-7 w-7"
                                                    onClick={firstPage}
                                                    disabled={currentPage === 1}
                                                    title="First Page"
                                                >
                                                    <ChevronsLeft className="h-4 w-4" />
                                                </Button>
                                                <Button
                                                    variant="outline"
                                                    size="icon"
                                                    className="h-7 w-7"
                                                    onClick={previousPage}
                                                    disabled={currentPage === 1}
                                                    title="Previous Page"
                                                >
                                                    <ChevronLeft className="h-4 w-4" />
                                                </Button>

                                                <span className="text-sm mx-2">
                                                    Page {currentPage} of {totalPages}
                                                </span>

                                                <Button
                                                    variant="outline"
                                                    size="icon"
                                                    className="h-7 w-7"
                                                    onClick={nextPage}
                                                    disabled={currentPage === totalPages}
                                                    title="Next Page"
                                                >
                                                    <ChevronRight className="h-4 w-4" />
                                                </Button>
                                                <Button
                                                    variant="outline"
                                                    size="icon"
                                                    className="h-7 w-7"
                                                    onClick={lastPage}
                                                    disabled={currentPage === totalPages}
                                                    title="Last Page"
                                                >
                                                    <ChevronsRight className="h-4 w-4" />
                                                </Button>
                                            </div>
                                        </div>
                                    )}
                                </div>
                            ) : (
                                <div className="px-20 py-4 text-center">
                                    <div className="flex flex-col items-center justify-center text-muted-foreground">
                                        <p>No orders found in this district</p>
                                    </div>
                                </div>
                            )}
                        </div>
                    </div>
                </TableCell>
            </TableRow>

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
