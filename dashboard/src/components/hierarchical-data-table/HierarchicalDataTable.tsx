import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import {
    BarChart4,
    Building,
    ChevronDown,
    ChevronRight,
    Coins,
    Package,
    Search,
    TrendingUp,
    X,
    CheckCircle,
} from "lucide-react";
import { useMemo, useRef, useState, useCallback } from "react";
import { StateData, HierarchicalDataTableProps } from "./types";
import { StateRow } from "./StateRow";
import {
    calculateAverage,
    createUniqueKey,
    formatCurrency,
    formatDate,
    getDepartmentAcronym,
    getDepartmentColor,
    getERPUrl,
    getLocationName,
    getStatusColor,
    getTypeColor,
    processDataWithFilters,
} from "./utils";

export const HierarchicalDataTable = ({ data, viewType = "location" }: HierarchicalDataTableProps) => {
    const stateRowRefs = useRef<Map<string, (expanded: boolean) => void>>(new Map());
    const territoryRowRefs = useRef<Map<string, (expanded: boolean) => void>>(new Map());
    const cityRowRefs = useRef<Map<string, (expanded: boolean) => void>>(new Map());
    const districtRowRefs = useRef<Map<string, (expanded: boolean) => void>>(new Map());
    const departmentRowRefs = useRef<Map<string, (expanded: boolean) => void>>(new Map());

    const [isFullExpansion, setIsFullExpansion] = useState(false);
    const [searchQuery, setSearchQuery] = useState<string>("");

    const initialProcessedData = useMemo(() => {
        const processedData = [...data];

        processedData.forEach((stateData) => {
            stateData.inactive_count = 0;
            stateData.total_capacity = 0;

            stateData.territories.forEach((territory) => {
                territory.inactive_count = 0;
                territory.total_capacity = 0;

                // Check if this is location view data structure
                if (viewType === "location" && "cities" in territory) {
                    territory.cities.forEach((city) => {
                        city.inactive_count = 0;
                        city.total_capacity = 0;

                        city.districts.forEach((district) => {
                            const inactiveOrders = district.orders.filter(
                                (order) => order.status === "Cancelled" || order.status === "Draft",
                            );
                            district.inactive_count = inactiveOrders.length;

                            district.total_capacity = district.orders
                                .filter((order) => order.status !== "Cancelled" && order.status !== "Draft")
                                .reduce((sum, order) => sum + (order.capacity_value || 0), 0);

                            city.inactive_count += district.inactive_count;
                            city.total_capacity += district.total_capacity;
                        });

                        territory.inactive_count += city.inactive_count;
                        territory.total_capacity += city.total_capacity;
                    });
                }
                // Check if this is department view data structure
                else if (viewType === "department" && "departments" in territory) {
                    territory.departments.forEach((department) => {
                        const inactiveOrders = department.orders.filter(
                            (order) => order.status === "Cancelled" || order.status === "Draft",
                        );
                        department.inactive_count = inactiveOrders.length;

                        department.total_capacity = department.orders
                            .filter((order) => order.status !== "Cancelled" && order.status !== "Draft")
                            .reduce((sum, order) => sum + (order.capacity_value || 0), 0);

                        territory.inactive_count += department.inactive_count;
                        territory.total_capacity += department.total_capacity;
                    });
                }

                stateData.inactive_count += territory.inactive_count;
                stateData.total_capacity += territory.total_capacity;
            });
        });

        return processedData;
    }, [data, viewType]);

    const normalizedData = useMemo(() => {
        if (!data || data.length === 0) {
            return [];
        }

        // Early return for department view to avoid unnecessary processing
        if (viewType === "department") {
            return initialProcessedData;
        }

        const dataCopy: StateData[] = JSON.parse(JSON.stringify(initialProcessedData));

        // Only proceed with location view normalization
        if (viewType === "location") {
            dataCopy.forEach((stateData) => {
                stateData.territories.forEach((territory) => {
                    if ("cities" in territory) {
                        territory.cities.forEach((city) => {
                            city.districts.forEach((district) => {
                                const inactiveOrders = district.orders.filter(
                                    (order) => order.status === "Cancelled" || order.status === "Draft",
                                );
                                district.inactive_count = inactiveOrders.length;
                            });

                            city.inactive_count = city.districts.reduce(
                                (sum, district) => sum + (district.inactive_count || 0),
                                0,
                            );
                        });

                        territory.inactive_count = territory.cities.reduce(
                            (sum, city) => sum + (city.inactive_count || 0),
                            0,
                        );
                    }
                });

                stateData.inactive_count = stateData.territories.reduce(
                    (sum, territory) => sum + (territory.inactive_count || 0),
                    0,
                );
            });

            const unspecifiedStateRows = dataCopy.filter((state) => !state.state || state.state.trim() === "");

            if (unspecifiedStateRows.length <= 1) {
                return dataCopy;
            }

            const filteredData = dataCopy.filter((state) => state.state && state.state.trim() !== "");

            const mergedRow: StateData = {
                state: null,
                total_amount: 0,
                count: 0,
                inactive_count: 0,
                total_capacity: 0,
                territories: [],
            };

            unspecifiedStateRows.forEach((stateRow) => {
                mergedRow.total_amount += stateRow.total_amount;
                mergedRow.count += stateRow.count;
                mergedRow.inactive_count += stateRow.inactive_count || 0;
                mergedRow.total_capacity += stateRow.total_capacity || 0;

                stateRow.territories.forEach((territory) => {
                    const existingTerritory = mergedRow.territories.find((t) => t.territory === territory.territory);

                    if (existingTerritory) {
                        existingTerritory.total_amount += territory.total_amount;
                        existingTerritory.count += territory.count;
                        existingTerritory.inactive_count += territory.inactive_count || 0;
                        existingTerritory.total_capacity += territory.total_capacity || 0;

                        if ("cities" in territory && "cities" in existingTerritory) {
                            territory.cities.forEach((city) => {
                                const existingCity = existingTerritory.cities.find(
                                    (c) => (!c.city && !city.city) || c.city === city.city,
                                );

                                if (existingCity) {
                                    existingCity.total_amount += city.total_amount;
                                    existingCity.count += city.count;
                                    existingCity.inactive_count += city.inactive_count || 0;
                                    existingCity.total_capacity += city.total_capacity || 0;

                                    city.districts.forEach((district) => {
                                        const existingDistrict = existingCity.districts.find(
                                            (d) =>
                                                (!d.district && !district.district) || d.district === district.district,
                                        );

                                        if (existingDistrict) {
                                            existingDistrict.total_amount += district.total_amount;
                                            existingDistrict.count += district.count;
                                            existingDistrict.inactive_count += district.inactive_count || 0;
                                            existingDistrict.total_capacity += district.total_capacity || 0;

                                            existingDistrict.orders = [...existingDistrict.orders, ...district.orders];
                                        } else {
                                            existingCity.districts.push(district);
                                        }
                                    });
                                } else {
                                    existingTerritory.cities.push(city);
                                }
                            });
                        }
                    } else {
                        mergedRow.territories.push(territory);
                    }
                });
            });

            filteredData.push(mergedRow);
            return filteredData;
        }

        return dataCopy;
    }, [initialProcessedData, viewType, data]);

    const registerStateRow = (key: string, setExpandedFn: (expanded: boolean) => void) => {
        stateRowRefs.current.set(key, setExpandedFn);
    };

    const expandAll = useCallback(() => {
        setIsFullExpansion(true);
        stateRowRefs.current.forEach((setExpanded) => setExpanded(true));
    }, []);

    const collapseAll = useCallback(() => {
        setIsFullExpansion(false);
        stateRowRefs.current.forEach((setExpanded) => setExpanded(false));
        territoryRowRefs.current.forEach((setExpanded) => setExpanded(false));
        if (viewType === "location") {
            cityRowRefs.current.forEach((setExpanded) => setExpanded(false));
            districtRowRefs.current.forEach((setExpanded) => setExpanded(false));
        } else {
            departmentRowRefs.current.forEach((setExpanded) => setExpanded(false));
        }
    }, [viewType]);

    const filteredData = useMemo(() => {
        if (searchQuery.trim()) {
            setTimeout(() => {
                expandAll();
            }, 0);
        }

        return processDataWithFilters(normalizedData, searchQuery);
    }, [normalizedData, searchQuery, expandAll]);

    const toggleExpansion = () => {
        if (isFullExpansion) {
            collapseAll();
        } else {
            expandAll();
        }
    };

    // Adjust column headers based on viewType
    const getColumnHeaders = () => {
        if (viewType === "location") {
            return (
                <TableRow>
                    <TableHead className="w-[300px]">Location</TableHead>
                    <TableHead className="w-[120px]">Orders</TableHead>
                    <TableHead className="w-[120px]">Draft/Cancelled</TableHead>
                    <TableHead className="w-[150px]">Total Revenue</TableHead>
                    <TableHead className="w-[120px]">Avg. Order Value</TableHead>
                    <TableHead className="w-[120px]">Total Capacity</TableHead>
                </TableRow>
            );
        } else {
            return (
                <TableRow>
                    <TableHead className="w-[300px]">Department</TableHead>
                    <TableHead className="w-[120px]">Orders</TableHead>
                    <TableHead className="w-[120px]">Draft/Cancelled</TableHead>
                    <TableHead className="w-[150px]">Total Revenue</TableHead>
                    <TableHead className="w-[120px]">Avg. Order Value</TableHead>
                    <TableHead className="w-[120px]">Total Capacity</TableHead>
                </TableRow>
            );
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
                                placeholder="Search"
                                value={searchQuery}
                                onChange={(e) => setSearchQuery(e.target.value)}
                                className="pl-8 h-9"
                                title="Separate multiple search terms with commas. Use > or < for price ranges."
                            />
                            {searchQuery.trim() && (
                                <>
                                    <Button
                                        variant="destructive"
                                        size="sm"
                                        onClick={() => setSearchQuery("")}
                                        className="absolute right-2 top-1/2 transform -translate-y-1/2 h-6 bg-rose-500 hover:bg-rose-600 text-white px-2 py-0 text-xs rounded"
                                    >
                                        <X className="h-3 w-3 mr-1" />
                                        Clear
                                    </Button>
                                </>
                            )}
                        </div>
                        {searchQuery.trim() && (
                            <Badge
                                variant="outline"
                                className="h-9 px-3 flex items-center"
                            >
                                <Search className="h-3.5 w-3.5 mr-1.5" /> Filtered results
                            </Badge>
                        )}
                    </div>
                    <Button
                        variant="outline"
                        size="sm"
                        onClick={toggleExpansion}
                        className="flex items-center gap-1 cursor-pointer"
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

                {/* Stats Section */}
                <div className="p-2 bg-muted/20 border-b">
                    {(() => {
                        // Calculate summary stats
                        const totalOrders = filteredData.reduce((total, state) => total + state.count, 0);
                        const inactiveOrders = filteredData.reduce(
                            (total, state) => total + (state.inactive_count || 0),
                            0,
                        );

                        let completedOrders = 0;

                        // Calculate completed orders - handle both view types
                        if (viewType === "location") {
                            filteredData.forEach((state) => {
                                state.territories.forEach((territory) => {
                                    if ("cities" in territory) {
                                        territory.cities.forEach((city) => {
                                            city.districts.forEach((district) => {
                                                completedOrders += district.orders.filter(
                                                    (order) =>
                                                        order.status === "Completed" || order.status === "Closed",
                                                ).length;
                                            });
                                        });
                                    }
                                });
                            });
                        } else if (viewType === "department") {
                            filteredData.forEach((state) => {
                                state.territories.forEach((territory) => {
                                    if ("departments" in territory) {
                                        territory.departments.forEach((department) => {
                                            completedOrders += department.orders.filter(
                                                (order) => order.status === "Completed" || order.status === "Closed",
                                            ).length;
                                        });
                                    }
                                });
                            });
                        }

                        const activeOrders = totalOrders - inactiveOrders - completedOrders;
                        const totalRevenue = filteredData.reduce((total, state) => total + state.total_amount, 0);
                        const avgOrderValue = totalOrders > 0 ? totalRevenue / totalOrders : 0;

                        // Calculate department distribution
                        const departmentCounts: Record<string, number> = {};
                        let topDepartment = { name: "None", count: 0 };

                        // Handle both view types for department counts
                        if (viewType === "location") {
                            filteredData.forEach((state) => {
                                state.territories.forEach((territory) => {
                                    if ("cities" in territory) {
                                        territory.cities.forEach((city) => {
                                            city.districts.forEach((district) => {
                                                district.orders.forEach((order) => {
                                                    if (order.department) {
                                                        departmentCounts[order.department] =
                                                            (departmentCounts[order.department] || 0) + 1;
                                                        if (departmentCounts[order.department] > topDepartment.count) {
                                                            topDepartment = {
                                                                name: order.department,
                                                                count: departmentCounts[order.department],
                                                            };
                                                        }
                                                    }
                                                });
                                            });
                                        });
                                    }
                                });
                            });
                        } else if (viewType === "department") {
                            filteredData.forEach((state) => {
                                state.territories.forEach((territory) => {
                                    if ("departments" in territory) {
                                        territory.departments.forEach((department) => {
                                            if (department.department) {
                                                departmentCounts[department.department] =
                                                    (departmentCounts[department.department] || 0) + department.count;
                                                if (departmentCounts[department.department] > topDepartment.count) {
                                                    topDepartment = {
                                                        name: department.department,
                                                        count: departmentCounts[department.department],
                                                    };
                                                }
                                            }
                                        });
                                    }
                                });
                            });
                        }

                        const formatter = new Intl.NumberFormat("en-IN", { maximumFractionDigits: 0 });
                        const percentFormatter = new Intl.NumberFormat("en-IN", {
                            minimumFractionDigits: 1,
                            maximumFractionDigits: 1,
                        });

                        const activePercentage = totalOrders > 0 ? (activeOrders / totalOrders) * 100 : 0;
                        const completedPercentage = totalOrders > 0 ? (completedOrders / totalOrders) * 100 : 0;

                        return (
                            <div className="flex flex-wrap items-center gap-x-6 gap-y-1 text-sm">
                                <div className="flex items-center gap-1.5 p-1">
                                    <Package className="h-4 w-4 text-primary" />
                                    <span className="font-medium mr-1">Total:</span>
                                    <span>{totalOrders}</span>
                                </div>
                                <div className="flex items-center gap-1.5 p-1">
                                    <TrendingUp className="h-4 w-4 text-green-600" />
                                    <span className="font-medium mr-1">Active:</span>
                                    <span className="text-green-600">{activeOrders}</span>
                                    <span className="text-xs text-green-500">
                                        ({percentFormatter.format(activePercentage)}%)
                                    </span>
                                </div>
                                <div className="flex items-center gap-1.5 p-1">
                                    <CheckCircle className="h-4 w-4 text-purple-600" />
                                    <span className="font-medium mr-1">Completed:</span>
                                    <span className="text-purple-600">{completedOrders}</span>
                                    <span className="text-xs text-purple-500">
                                        ({percentFormatter.format(completedPercentage)}%)
                                    </span>
                                </div>
                                <div className="flex items-center gap-1.5 p-1">
                                    <X className="h-4 w-4 text-yellow-600" />
                                    <span className="font-medium mr-1">Draft/Cancelled:</span>
                                    <span className="text-yellow-600">{inactiveOrders}</span>
                                </div>
                                <div className="flex items-center gap-1.5 p-1">
                                    <Coins className="h-4 w-4 text-blue-600" />
                                    <span className="font-medium mr-1">Revenue:</span>
                                    <span className="text-blue-600">₹{formatter.format(totalRevenue)}</span>
                                </div>
                                <div className="flex items-center gap-1.5 p-1">
                                    <BarChart4 className="h-4 w-4 text-emerald-600" />
                                    <span className="font-medium mr-1">Avg Value:</span>
                                    <span className="text-emerald-600">₹{formatter.format(avgOrderValue)}</span>
                                </div>
                                <div className="flex items-center gap-1.5 p-1">
                                    <Building className="h-4 w-4 text-gray-600" />
                                    <span className="font-medium mr-1">Top Dept:</span>
                                    <span
                                        className="truncate max-w-[150px]"
                                        title={topDepartment.name}
                                    >
                                        {getDepartmentAcronym(topDepartment.name)}
                                    </span>
                                </div>
                            </div>
                        );
                    })()}
                </div>

                <div className="overflow-auto">
                    <ScrollArea className="h-[calc(80vh-180px)] min-h-[450px] w-full">
                        <div className="min-w-[750px]">
                            <Table className="w-full table-fixed">
                                <TableHeader className="bg-gray-50 sticky top-0 z-10">{getColumnHeaders()}</TableHeader>
                                <TableBody>
                                    {filteredData.length === 0 ? (
                                        <TableRow>
                                            <TableCell
                                                colSpan={6}
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
                                                formatDate={formatDate}
                                                calculateAverage={calculateAverage}
                                                createUniqueKey={createUniqueKey}
                                                getStatusColor={getStatusColor}
                                                getTypeColor={getTypeColor}
                                                registerRow={registerStateRow}
                                                isFullExpansion={isFullExpansion}
                                                getERPUrl={getERPUrl}
                                                getDepartmentAcronym={getDepartmentAcronym}
                                                getDepartmentColor={getDepartmentColor}
                                                viewType={viewType}
                                            />
                                        ))
                                    )}
                                </TableBody>
                            </Table>
                        </div>
                    </ScrollArea>
                </div>
            </Card>
        </>
    );
};
