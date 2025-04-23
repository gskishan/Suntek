import { SalesOrder, StateData, DepartmentStateData } from "./types";

export const getLocationName = (
    value: string | null,
    type: "state" | "city" | "district" | "territory" | "department",
    districtName?: string | null,
): string => {
    if (!value) {
        return `Unspecified ${type.charAt(0).toUpperCase() + type.slice(1)}`;
    }
    if (type === "district" && districtName) {
        return districtName;
    }
    if (type === "territory") {
        return `${value} (Zone)`;
    }
    if (type === "department") {
        return value;
    }
    return value;
};

export const getStatusColor = (status: string): string => {
    const colors: { [key: string]: string } = {
        "To Deliver and Bill": "bg-yellow-100 text-yellow-800",
        Completed: "bg-green-100 text-green-800",
        Closed: "bg-gray-100 text-gray-800",
        Draft: "bg-blue-100 text-blue-800",
        Cancelled: "bg-red-100 text-red-800",
    };
    return colors[status] || "bg-gray-100 text-gray-800";
};

export const getTypeColor = (type: string): string => {
    if (type === "No Type of Case") {
        return "bg-gray-100 text-gray-600";
    }

    const colors: { [key: string]: string } = {
        Subsidy: "bg-purple-100 text-purple-800",
        "Non Subsidy": "bg-orange-100 text-orange-800",
    };

    return colors[type] || "bg-gray-100 text-gray-800";
};

export const getDepartmentAcronym = (department: string | null): string => {
    if (!department || department === "Unassigned Department") {
        return "DEPT";
    }

    // Use department_abbr from the backend if available
    if (typeof department === "object" && department !== null && "department_abbr" in department) {
        return (department as any).department_abbr;
    }

    // Handle special cases first
    if (department.includes("Domestic") || department.includes("Residential")) {
        return "Domestic";
    } else if (department.includes("Channel Partner")) {
        return "CHP";
    } else if (department.includes("Commercial & Industrial") || department.includes("C&I")) {
        return "C&I";
    }

    // Remove any suffix like -SESP or -S before creating acronym
    const baseDepartment = department.replace(/\s*[-–—]\s*(SESP|S)$/, "");

    // Split by space and take first letter of each word
    return baseDepartment
        .split(" ")
        .map((word) => word.charAt(0).toUpperCase())
        .join("");
};

export const getDepartmentColor = (department: string | null): string => {
    if (!department || department === "Unassigned Department") {
        return "bg-gray-100 text-gray-600";
    }

    const colors: { [key: string]: string } = {
        "Residential Team": "bg-blue-100 text-blue-800",
        "Commercial Team": "bg-green-100 text-green-800",
        "Government Team": "bg-purple-100 text-purple-800",
        "Industrial Team": "bg-orange-100 text-orange-800",
        "Marketing Team": "bg-pink-100 text-pink-800",
        "Sales Team": "bg-indigo-100 text-indigo-800",
    };

    return colors[department] || "bg-emerald-100 text-emerald-800";
};

export const formatCurrency = (value: number): string => {
    return new Intl.NumberFormat("en-IN", {
        maximumFractionDigits: 0,
    }).format(value);
};

export const calculateAverage = (total: number, count: number): number => {
    if (count === 0) return 0;
    return total / count;
};

export const formatDate = (dateString: string): string => {
    try {
        const date = new Date(dateString);
        return date.toLocaleDateString();
    } catch (error) {
        return dateString;
    }
};

export const createUniqueKey = (value: string | null, prefix: string, index: number): string => {
    if (value) return value;
    return `${prefix}-unknown-${index}`;
};

export const getERPUrl = (doctype: string, name: string): string => {
    return `/app/${doctype.toLowerCase().replace(/ /g, "-")}/${name}`;
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

export const processDataWithFilters = (
    data: StateData[] | DepartmentStateData[],
    query: string,
): StateData[] | DepartmentStateData[] => {
    if (!query.trim()) {
        return data;
    }

    // Multi-term search (comma separated)
    const terms = query
        .toLowerCase()
        .split(",")
        .map((term) => term.trim())
        .filter((term) => term);

    if (terms.length === 0) {
        return data;
    }

    const isQueryMatch = (text: string | null | undefined): boolean => {
        if (!text) return false;
        return terms.some((term) => text.toLowerCase().includes(term));
    };

    const isPriceMatch = (price: number, term: string): boolean => {
        if (term.startsWith(">")) {
            const value = parseFloat(term.substring(1).trim());
            return !isNaN(value) && price > value;
        }
        if (term.startsWith("<")) {
            const value = parseFloat(term.substring(1).trim());
            return !isNaN(value) && price < value;
        }
        if (term.startsWith("=")) {
            const value = parseFloat(term.substring(1).trim());
            return !isNaN(value) && price === value;
        }
        return price.toString().includes(term);
    };

    const filteredData: StateData[] | DepartmentStateData[] = JSON.parse(JSON.stringify(data));

    if ("cities" in (filteredData[0]?.territories[0] || {})) {
        // Location view filtering
        const locationData = filteredData as StateData[];
        locationData.forEach((state) => {
            state.territories.forEach((territory) => {
                territory.cities.forEach((city) => {
                    city.districts.forEach((district) => {
                        district.orders = district.orders.filter((order) => {
                            return terms.some((term) => {
                                // Check various fields for match
                                return (
                                    isQueryMatch(order.name) ||
                                    isQueryMatch(order.customer) ||
                                    isQueryMatch(order.type_of_case) ||
                                    isQueryMatch(order.type_of_structure) ||
                                    isQueryMatch(order.department) ||
                                    isQueryMatch(order.sales_person) ||
                                    isQueryMatch(order.status) ||
                                    isQueryMatch(state.state) ||
                                    isQueryMatch(territory.territory) ||
                                    isQueryMatch(city.city) ||
                                    isQueryMatch(district.district) ||
                                    isQueryMatch(district.district_name) ||
                                    isPriceMatch(order.grand_total, term)
                                );
                            });
                        });
                    });

                    // Filter out empty districts
                    city.districts = city.districts.filter((district) => district.orders.length > 0);

                    // Recalculate counts for city
                    if (city.districts.length > 0) {
                        city.count = city.districts.reduce((sum, district) => sum + district.count, 0);
                        city.total_amount = city.districts.reduce((sum, district) => sum + district.total_amount, 0);
                        city.inactive_count = city.districts.reduce(
                            (sum, district) => sum + (district.inactive_count || 0),
                            0,
                        );
                        city.total_capacity = city.districts.reduce(
                            (sum, district) => sum + (district.total_capacity || 0),
                            0,
                        );
                    }
                });

                // Filter out empty cities
                territory.cities = territory.cities.filter((city) => city.districts.length > 0);

                // Recalculate counts for territory
                if (territory.cities.length > 0) {
                    territory.count = territory.cities.reduce((sum, city) => sum + city.count, 0);
                    territory.total_amount = territory.cities.reduce((sum, city) => sum + city.total_amount, 0);
                    territory.inactive_count = territory.cities.reduce(
                        (sum, city) => sum + (city.inactive_count || 0),
                        0,
                    );
                    territory.total_capacity = territory.cities.reduce(
                        (sum, city) => sum + (city.total_capacity || 0),
                        0,
                    );
                }
            });

            // Filter out empty territories
            state.territories = state.territories.filter((territory) => territory.cities.length > 0);

            // Recalculate counts for state
            if (state.territories.length > 0) {
                state.count = state.territories.reduce((sum, territory) => sum + territory.count, 0);
                state.total_amount = state.territories.reduce((sum, territory) => sum + territory.total_amount, 0);
                state.inactive_count = state.territories.reduce(
                    (sum, territory) => sum + (territory.inactive_count || 0),
                    0,
                );
                state.total_capacity = state.territories.reduce(
                    (sum, territory) => sum + (territory.total_capacity || 0),
                    0,
                );
            }
        });

        return locationData.filter((state) => state.territories.length > 0);
    } else {
        // Department view filtering
        const departmentData = filteredData as DepartmentStateData[];
        departmentData.forEach((state) => {
            state.territories.forEach((territory) => {
                territory.departments.forEach((department) => {
                    department.orders = department.orders.filter((order) => {
                        return terms.some((term) => {
                            // Check various fields for match
                            return (
                                isQueryMatch(order.name) ||
                                isQueryMatch(order.customer) ||
                                isQueryMatch(order.type_of_case) ||
                                isQueryMatch(order.type_of_structure) ||
                                isQueryMatch(order.department) ||
                                isQueryMatch(order.sales_person) ||
                                isQueryMatch(order.status) ||
                                isQueryMatch(state.state) ||
                                isQueryMatch(territory.territory) ||
                                isPriceMatch(order.grand_total, term)
                            );
                        });
                    });
                });

                // Filter out empty departments
                territory.departments = territory.departments.filter((department) => department.orders.length > 0);

                // Recalculate counts for territory
                if (territory.departments.length > 0) {
                    territory.count = territory.departments.reduce((sum, department) => sum + department.count, 0);
                    territory.total_amount = territory.departments.reduce(
                        (sum, department) => sum + department.total_amount,
                        0,
                    );
                    territory.inactive_count = territory.departments.reduce(
                        (sum, department) => sum + (department.inactive_count || 0),
                        0,
                    );
                    territory.total_capacity = territory.departments.reduce(
                        (sum, department) => sum + (department.total_capacity || 0),
                        0,
                    );
                }
            });

            // Filter out empty territories
            state.territories = state.territories.filter((territory) => territory.departments.length > 0);

            // Recalculate counts for state
            if (state.territories.length > 0) {
                state.count = state.territories.reduce((sum, territory) => sum + territory.count, 0);
                state.total_amount = state.territories.reduce((sum, territory) => sum + territory.total_amount, 0);
                state.inactive_count = state.territories.reduce(
                    (sum, territory) => sum + (territory.inactive_count || 0),
                    0,
                );
                state.total_capacity = state.territories.reduce(
                    (sum, territory) => sum + (territory.total_capacity || 0),
                    0,
                );
            }
        });

        return departmentData.filter((state) => state.territories.length > 0);
    }
};
