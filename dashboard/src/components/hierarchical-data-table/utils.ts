import { SalesOrder, StateData } from "./types";

export const getLocationName = (
    value: string | null,
    type: "state" | "city" | "district" | "territory",
    districtName?: string | null,
): string => {
    if (!value || value.trim() === "") {
        return `Unspecified ${type.charAt(0).toUpperCase() + type.slice(1)}`;
    }
    if (type === "district" && districtName) return districtName;
    if (type === "territory") return `${value} (Zone)`;
    return value;
};

export const getStatusColor = (status: string): string => {
    const colors: { [key: string]: string } = {
        "To Deliver and Bill": "bg-yellow-100 text-yellow-800",
        Completed: "bg-green-100 text-green-800",
        Closed: "bg-gray-100 text-gray-800",
        Draft: "bg-blue-100 text-blue-800",
        Cancelled: "bg-rose-100 text-rose-800",
    };
    return colors[status] || "bg-gray-100 text-gray-800";
};

export const getTypeColor = (type: string): string => {
    const colors: { [key: string]: string } = {
        Subsidy: "bg-purple-100 text-purple-800",
        "Non Subsidy": "bg-orange-100 text-orange-800",
    };
    return colors[type] || "bg-gray-100 text-gray-800";
};

export const getDepartmentAcronym = (department: string | null): string => {
    if (!department) return "None";

    switch (department) {
        case "Domestic (Residential) Sales Team - SESP":
            return "Domestic";
        case "Commercial & Industrial (C&I) - SESP":
            return "C&I";
        case "Channel Partner - SESP":
            return "Channel Partner";
        default:
            return department === "not defined" ? "None" : "Other";
    }
};

export const getDepartmentColor = (department: string | null): string => {
    const acronym = getDepartmentAcronym(department);
    const colors: { [key: string]: string } = {
        Domestic: "bg-blue-100 text-blue-800",
        "C&I": "bg-emerald-100 text-emerald-800",
        "Channel Partner": "bg-indigo-100 text-indigo-800",
        None: "bg-gray-100 text-gray-800",
        Other: "bg-pink-100 text-pink-800",
    };
    return colors[acronym] || "bg-gray-100 text-gray-800";
};

export const formatCurrency = (amount: number): string => {
    const formatter = new Intl.NumberFormat("en-IN", {
        maximumFractionDigits: 0,
    });
    return `₹${formatter.format(amount)}`;
};

export const calculateAverage = (total: number, count: number): number => {
    const validCount = count > 0 ? count : 1;
    return total / validCount;
};

export const formatDate = (dateString: string): string => {
    const date = new Date(dateString);
    return `${date.getDate().toString().padStart(2, "0")}/${(date.getMonth() + 1).toString().padStart(2, "0")}/${date.getFullYear()}`;
};

export const createUniqueKey = (value: string | null, prefix: string, index: number): string => {
    if (value) return `${prefix}-${value}`;
    return `${prefix}-unknown-${index}`;
};

export const getERPUrl = (): string => {
    return window.location.origin;
};

export const filterOrders = (order: SalesOrder, searchQuery: string): boolean => {
    if (!searchQuery.trim()) return true;

    const searchTerms = searchQuery
        .toLowerCase()
        .split(",")
        .map((term) => term.trim())
        .filter((term) => term);

    if (searchTerms.length === 0) return true;

    return searchTerms.every((term) => {
        if (term.startsWith(">") || term.startsWith("<")) {
            const parts = term.match(/([><])(\d+)/);
            if (parts && parts.length >= 3) {
                const operator = parts[1];
                const amount = parseFloat(parts[2]);

                if (!isNaN(amount)) {
                    if (operator === ">") return order.grand_total > amount;
                    if (operator === "<") return order.grand_total < amount;
                }
            }

            if (searchTerms.length >= 2) {
                const otherTermIndex = searchTerms.findIndex(
                    (t) => t !== term && (t.startsWith(">") || t.startsWith("<")),
                );

                if (otherTermIndex !== -1) {
                    const otherTerm = searchTerms[otherTermIndex];
                    const otherParts = otherTerm.match(/([><])(\d+)/);

                    if (parts && otherParts && parts.length >= 3 && otherParts.length >= 3) {
                        const thisOp = parts[1];
                        const thisAmount = parseFloat(parts[2]);
                        const otherOp = otherParts[1];
                        const otherAmount = parseFloat(otherParts[2]);

                        if (!isNaN(thisAmount) && !isNaN(otherAmount)) {
                            if (thisOp === ">" && otherOp === "<") {
                                return order.grand_total > thisAmount && order.grand_total < otherAmount;
                            } else if (thisOp === "<" && otherOp === ">") {
                                return order.grand_total < thisAmount && order.grand_total > otherAmount;
                            }
                        }
                    }
                }
            }
        }

        if (order.status.toLowerCase() === term) {
            return true;
        }

        if (order.department?.toLowerCase() === term) {
            return true;
        }

        return (
            order.name.toLowerCase().includes(term) ||
            order.customer.toLowerCase().includes(term) ||
            (order.type_of_case?.toLowerCase() || "").includes(term) ||
            (order.type_of_structure?.toLowerCase() || "").includes(term) ||
            (order.department?.toLowerCase() || "").includes(term) ||
            (order.sales_person?.toLowerCase() || "").includes(term) ||
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

export const processDataWithFilters = (normalizedData: StateData[], searchQuery: string): StateData[] => {
    if (!searchQuery.trim()) return normalizedData;

    return normalizedData
        .map((stateData) => {
            const filteredState = {
                ...stateData,
                territories: stateData.territories
                    .map((territory) => {
                        const filteredTerritory = {
                            ...territory,
                            cities: territory.cities
                                .map((city) => {
                                    const filteredCity = {
                                        ...city,
                                        districts: city.districts
                                            .map((district) => {
                                                const filteredOrders = district.orders.filter((order) =>
                                                    filterOrders(order, searchQuery),
                                                );

                                                const validOrders = filteredOrders.filter(
                                                    (order) => order.status !== "Cancelled" && order.status !== "Draft",
                                                );

                                                const inactiveOrders = filteredOrders.filter(
                                                    (order) => order.status === "Cancelled" || order.status === "Draft",
                                                );

                                                const total_capacity = validOrders.reduce(
                                                    (sum, order) => sum + (order.capacity_value || 0),
                                                    0,
                                                );

                                                return {
                                                    ...district,
                                                    orders: filteredOrders,
                                                    count: filteredOrders.length,
                                                    inactive_count: inactiveOrders.length,
                                                    total_amount: validOrders.reduce(
                                                        (sum, order) => sum + (order.grand_total || 0),
                                                        0,
                                                    ),
                                                    total_capacity: total_capacity,
                                                };
                                            })
                                            .filter((district) => district.orders.length > 0),
                                    };

                                    const districtTotalCount = filteredCity.districts.reduce(
                                        (sum, district) => sum + district.count,
                                        0,
                                    );

                                    const districtInactiveCount = filteredCity.districts.reduce(
                                        (sum, district) => sum + district.inactive_count,
                                        0,
                                    );

                                    const districtTotal = filteredCity.districts.reduce(
                                        (sum, district) => sum + district.total_amount,
                                        0,
                                    );

                                    const cityTotalCapacity = filteredCity.districts.reduce(
                                        (sum, district) => sum + district.total_capacity,
                                        0,
                                    );

                                    return {
                                        ...filteredCity,
                                        count: districtTotalCount,
                                        inactive_count: districtInactiveCount,
                                        total_amount: districtTotal,
                                        total_capacity: cityTotalCapacity,
                                    };
                                })
                                .filter((city) => city.districts.length > 0),
                        };

                        const cityTotalCount = filteredTerritory.cities.reduce((sum, city) => sum + city.count, 0);

                        const cityInactiveCount = filteredTerritory.cities.reduce(
                            (sum, city) => sum + city.inactive_count,
                            0,
                        );

                        const cityTotal = filteredTerritory.cities.reduce((sum, city) => sum + city.total_amount, 0);

                        const territoryTotalCapacity = filteredTerritory.cities.reduce(
                            (sum, city) => sum + city.total_capacity,
                            0,
                        );

                        return {
                            ...filteredTerritory,
                            count: cityTotalCount,
                            inactive_count: cityInactiveCount,
                            total_amount: cityTotal,
                            total_capacity: territoryTotalCapacity,
                        };
                    })
                    .filter((territory) => territory.cities.length > 0),
            };

            const territoryTotalCount = filteredState.territories.reduce((sum, territory) => sum + territory.count, 0);

            const territoryInactiveCount = filteredState.territories.reduce(
                (sum, territory) => sum + territory.inactive_count,
                0,
            );

            const territoryTotal = filteredState.territories.reduce(
                (sum, territory) => sum + territory.total_amount,
                0,
            );

            const stateTotalCapacity = filteredState.territories.reduce(
                (sum, territory) => sum + territory.total_capacity,
                0,
            );

            return {
                ...filteredState,
                count: territoryTotalCount,
                inactive_count: territoryInactiveCount,
                total_amount: territoryTotal,
                total_capacity: stateTotalCapacity,
            };
        })
        .filter((state) => state.territories.length > 0);
};
