import { useState } from "react";
import { ChevronDown, ChevronRight, TrendingUp, DollarSign, Package } from "lucide-react";
import { Tooltip, TooltipContent, TooltipTrigger } from "@/components/ui/tooltip";
import { Card } from "@/components/ui/card";

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
}

interface DistrictData {
    district: string | null;
    district_name: string | null;
    total_amount: number;
    count: number;
    cities: {
        city: string | null;
        total_amount: number;
        count: number;
        orders: SalesOrder[];
    }[];
}

interface StateData {
    state: string | null;
    total_amount: number;
    count: number;
    districts: DistrictData[];
}

interface TerritoryData {
    territory: string;
    total_amount: number;
    count: number;
    states: StateData[];
}

interface SalesOrderTableProps {
    data: TerritoryData[];
}

export const SalesOrderTable = ({ data }: SalesOrderTableProps) => {
    const [expandedTerritories, setExpandedTerritories] = useState<Set<string>>(new Set());
    const [expandedStates, setExpandedStates] = useState<Set<string>>(new Set());
    const [expandedDistricts, setExpandedDistricts] = useState<Set<string>>(new Set());
    const [expandedCities, setExpandedCities] = useState<Set<string>>(new Set());
    const [expandedOrders, setExpandedOrders] = useState<Set<string>>(new Set());

    const toggleTerritory = (territory: string) => {
        const newExpanded = new Set(expandedTerritories);
        if (newExpanded.has(territory)) {
            newExpanded.delete(territory);
        } else {
            newExpanded.add(territory);
        }
        setExpandedTerritories(newExpanded);
    };

    const toggleState = (state: string | null) => {
        const stateKey = state || "unknown";
        const newExpanded = new Set(expandedStates);
        if (newExpanded.has(stateKey)) {
            newExpanded.delete(stateKey);
        } else {
            newExpanded.add(stateKey);
        }
        setExpandedStates(newExpanded);
    };

    const toggleDistrict = (district: string | null) => {
        const districtKey = district || "unknown";
        const newExpanded = new Set(expandedDistricts);
        if (newExpanded.has(districtKey)) {
            newExpanded.delete(districtKey);
        } else {
            newExpanded.add(districtKey);
        }
        setExpandedDistricts(newExpanded);
    };

    const toggleCity = (city: string | null) => {
        const cityKey = city || "unknown";
        const newExpanded = new Set(expandedCities);
        if (newExpanded.has(cityKey)) {
            newExpanded.delete(cityKey);
        } else {
            newExpanded.add(cityKey);
        }
        setExpandedCities(newExpanded);
    };

    const toggleOrder = (orderName: string) => {
        const newExpanded = new Set(expandedOrders);
        if (newExpanded.has(orderName)) {
            newExpanded.delete(orderName);
        } else {
            newExpanded.add(orderName);
        }
        setExpandedOrders(newExpanded);
    };

    const getLocationName = (
        value: string | null,
        type: "state" | "district" | "city",
        districtName?: string | null,
    ) => {
        if (!value) return `Unspecified ${type.charAt(0).toUpperCase() + type.slice(1)}`;
        if (type === "district" && districtName) return districtName;
        return value;
    };

    const getStatusColor = (status: string) => {
        const colors: { [key: string]: string } = {
            "To Deliver and Bill": "bg-yellow-100 text-yellow-800",
            Completed: "bg-green-100 text-green-800",
            Closed: "bg-gray-100 text-gray-800",
            Draft: "bg-blue-100 text-blue-800",
        };
        return colors[status] || "bg-gray-100 text-gray-800";
    };

    const getTypeColor = (type: string) => {
        const colors: { [key: string]: string } = {
            Subsidy: "bg-purple-100 text-purple-800",
            "Non Subsidy": "bg-orange-100 text-orange-800",
        };
        return colors[type] || "bg-gray-100 text-gray-800";
    };

    // Helper function to process states and handle null states
    const processStates = (states: StateData[]) => {
        const specifiedStates = states.filter((s) => s.state !== null);
        const unspecifiedState = states.find((s) => s.state === null);

        // If we have an unspecified state, merge its data with any other unspecified states
        if (unspecifiedState) {
            const otherUnspecifiedStates = states.filter((s) => s.state === null && s !== unspecifiedState);

            if (otherUnspecifiedStates.length > 0) {
                // Merge all unspecified states
                otherUnspecifiedStates.forEach((state) => {
                    unspecifiedState.total_amount += state.total_amount;
                    unspecifiedState.count += state.count;
                    state.districts.forEach((district) => {
                        const existingDistrict = unspecifiedState.districts.find(
                            (d) => d.district === district.district,
                        );
                        if (existingDistrict) {
                            existingDistrict.total_amount += district.total_amount;
                            existingDistrict.count += district.count;
                            district.cities.forEach((city) => {
                                const existingCity = existingDistrict.cities.find((c) => c.city === city.city);
                                if (existingCity) {
                                    existingCity.total_amount += city.total_amount;
                                    existingCity.count += city.count;
                                    existingCity.orders.push(...city.orders);
                                } else {
                                    existingDistrict.cities.push(city);
                                }
                            });
                        } else {
                            unspecifiedState.districts.push(district);
                        }
                    });
                });
            }
        }

        return specifiedStates;
    };

    return (
        <div className="w-full space-y-6">
            {data.map((territoryData) => {
                const processedStates = processStates(territoryData.states);
                const unspecifiedState = territoryData.states.find((s) => s.state === null);

                return (
                    <Card
                        key={territoryData.territory}
                        className="overflow-hidden"
                    >
                        <div className="p-4 border-b bg-gray-50/50">
                            <button
                                onClick={() => toggleTerritory(territoryData.territory)}
                                className="flex items-center justify-between w-full text-lg font-semibold text-gray-900 hover:bg-gray-100/50 p-2 rounded-lg transition-colors"
                            >
                                <div className="flex items-center">
                                    {expandedTerritories.has(territoryData.territory) ? (
                                        <ChevronDown className="h-5 w-5 mr-2 text-gray-500" />
                                    ) : (
                                        <ChevronRight className="h-5 w-5 mr-2 text-gray-500" />
                                    )}
                                    {territoryData.territory}
                                </div>
                                <div className="flex items-center space-x-6">
                                    <Tooltip>
                                        <TooltipTrigger asChild>
                                            <div className="flex items-center text-sm text-gray-600 bg-white px-3 py-1 rounded-full shadow-sm">
                                                <Package className="h-4 w-4 mr-1.5" />
                                                {territoryData.count} Orders
                                            </div>
                                        </TooltipTrigger>
                                        <TooltipContent>
                                            <p>Total number of orders in {territoryData.territory}</p>
                                        </TooltipContent>
                                    </Tooltip>

                                    <Tooltip>
                                        <TooltipTrigger asChild>
                                            <div className="flex items-center text-sm text-gray-600 bg-white px-3 py-1 rounded-full shadow-sm">
                                                <DollarSign className="h-4 w-4 mr-1.5" />₹
                                                {territoryData.total_amount.toLocaleString()}
                                            </div>
                                        </TooltipTrigger>
                                        <TooltipContent>
                                            <p>Total revenue from all orders in {territoryData.territory}</p>
                                        </TooltipContent>
                                    </Tooltip>

                                    <Tooltip>
                                        <TooltipTrigger asChild>
                                            <div className="flex items-center text-sm text-gray-600 bg-white px-3 py-1 rounded-full shadow-sm">
                                                <TrendingUp className="h-4 w-4 mr-1.5" />₹
                                                {(territoryData.total_amount / territoryData.count).toLocaleString()}
                                            </div>
                                        </TooltipTrigger>
                                        <TooltipContent>
                                            <p>Average Order Value (AOV) in {territoryData.territory}</p>
                                        </TooltipContent>
                                    </Tooltip>
                                </div>
                            </button>
                        </div>

                        {expandedTerritories.has(territoryData.territory) && (
                            <div className="p-4 space-y-4">
                                {/* Render specified states first */}
                                {processedStates.map((stateData) => (
                                    <div
                                        key={stateData.state || "unknown"}
                                        className="bg-white rounded-lg shadow-sm border"
                                    >
                                        <button
                                            onClick={() => toggleState(stateData.state)}
                                            className="flex items-center justify-between w-full text-md font-medium text-gray-800 hover:bg-gray-50 p-3 rounded-lg transition-colors"
                                        >
                                            <div className="flex items-center">
                                                {expandedStates.has(stateData.state || "unknown") ? (
                                                    <ChevronDown className="h-4 w-4 mr-2 text-gray-500" />
                                                ) : (
                                                    <ChevronRight className="h-4 w-4 mr-2 text-gray-500" />
                                                )}
                                                {getLocationName(stateData.state, "state")}
                                            </div>
                                            <div className="flex items-center space-x-4">
                                                <Tooltip>
                                                    <TooltipTrigger asChild>
                                                        <span className="text-sm text-gray-600 bg-gray-50 px-2.5 py-1 rounded-full">
                                                            {stateData.count} Orders
                                                        </span>
                                                    </TooltipTrigger>
                                                    <TooltipContent>
                                                        <p>
                                                            Total number of orders in{" "}
                                                            {getLocationName(stateData.state, "state")}
                                                        </p>
                                                    </TooltipContent>
                                                </Tooltip>
                                                <Tooltip>
                                                    <TooltipTrigger asChild>
                                                        <span className="text-sm text-gray-600 bg-gray-50 px-2.5 py-1 rounded-full">
                                                            ₹{stateData.total_amount.toLocaleString()}
                                                        </span>
                                                    </TooltipTrigger>
                                                    <TooltipContent>
                                                        <p>
                                                            Total revenue from all orders in{" "}
                                                            {getLocationName(stateData.state, "state")}
                                                        </p>
                                                    </TooltipContent>
                                                </Tooltip>
                                            </div>
                                        </button>

                                        {expandedStates.has(stateData.state || "unknown") && (
                                            <div className="px-6 pb-4 space-y-3">
                                                {stateData.districts.map((districtData) => (
                                                    <div
                                                        key={districtData.district || "unknown"}
                                                        className="bg-gray-50 rounded-lg p-3"
                                                    >
                                                        <button
                                                            onClick={() => toggleDistrict(districtData.district)}
                                                            className="flex items-center justify-between w-full text-sm text-gray-700 hover:bg-gray-100/50 p-2 rounded-lg transition-colors"
                                                        >
                                                            <div className="flex items-center">
                                                                {expandedDistricts.has(
                                                                    districtData.district || "unknown",
                                                                ) ? (
                                                                    <ChevronDown className="h-4 w-4 mr-2 text-gray-500" />
                                                                ) : (
                                                                    <ChevronRight className="h-4 w-4 mr-2 text-gray-500" />
                                                                )}
                                                                {getLocationName(
                                                                    districtData.district,
                                                                    "district",
                                                                    districtData.district_name,
                                                                )}
                                                            </div>
                                                            <div className="flex items-center space-x-4">
                                                                <Tooltip>
                                                                    <TooltipTrigger asChild>
                                                                        <span className="text-sm text-gray-600 bg-white px-2.5 py-1 rounded-full">
                                                                            {districtData.count} Orders
                                                                        </span>
                                                                    </TooltipTrigger>
                                                                    <TooltipContent>
                                                                        <p>
                                                                            Total number of orders in{" "}
                                                                            {getLocationName(
                                                                                districtData.district,
                                                                                "district",
                                                                                districtData.district_name,
                                                                            )}
                                                                        </p>
                                                                    </TooltipContent>
                                                                </Tooltip>
                                                                <Tooltip>
                                                                    <TooltipTrigger asChild>
                                                                        <span className="text-sm text-gray-600 bg-white px-2.5 py-1 rounded-full">
                                                                            ₹
                                                                            {districtData.total_amount.toLocaleString()}
                                                                        </span>
                                                                    </TooltipTrigger>
                                                                    <TooltipContent>
                                                                        <p>
                                                                            Total revenue from all orders in{" "}
                                                                            {getLocationName(
                                                                                districtData.district,
                                                                                "district",
                                                                                districtData.district_name,
                                                                            )}
                                                                        </p>
                                                                    </TooltipContent>
                                                                </Tooltip>
                                                            </div>
                                                        </button>

                                                        {expandedDistricts.has(districtData.district || "unknown") && (
                                                            <div className="px-6 mt-3 space-y-3">
                                                                {districtData.cities.map((cityData) => (
                                                                    <div
                                                                        key={cityData.city || "unknown"}
                                                                        className="bg-white rounded-lg p-3"
                                                                    >
                                                                        <button
                                                                            onClick={() => toggleCity(cityData.city)}
                                                                            className="flex items-center justify-between w-full text-sm text-gray-700 hover:bg-gray-100/50 p-2 rounded-lg transition-colors"
                                                                        >
                                                                            <div className="flex items-center">
                                                                                {expandedCities.has(
                                                                                    cityData.city || "unknown",
                                                                                ) ? (
                                                                                    <ChevronDown className="h-4 w-4 mr-2 text-gray-500" />
                                                                                ) : (
                                                                                    <ChevronRight className="h-4 w-4 mr-2 text-gray-500" />
                                                                                )}
                                                                                {getLocationName(cityData.city, "city")}
                                                                            </div>
                                                                            <div className="flex items-center space-x-4">
                                                                                <Tooltip>
                                                                                    <TooltipTrigger asChild>
                                                                                        <span className="text-sm text-gray-600 bg-gray-50 px-2.5 py-1 rounded-full">
                                                                                            {cityData.count} Orders
                                                                                        </span>
                                                                                    </TooltipTrigger>
                                                                                    <TooltipContent>
                                                                                        <p>
                                                                                            Total number of orders in{" "}
                                                                                            {getLocationName(
                                                                                                cityData.city,
                                                                                                "city",
                                                                                            )}
                                                                                        </p>
                                                                                    </TooltipContent>
                                                                                </Tooltip>
                                                                                <Tooltip>
                                                                                    <TooltipTrigger asChild>
                                                                                        <span className="text-sm text-gray-600 bg-gray-50 px-2.5 py-1 rounded-full">
                                                                                            ₹
                                                                                            {cityData.total_amount.toLocaleString()}
                                                                                        </span>
                                                                                    </TooltipTrigger>
                                                                                    <TooltipContent>
                                                                                        <p>
                                                                                            Total revenue from all
                                                                                            orders in{" "}
                                                                                            {getLocationName(
                                                                                                cityData.city,
                                                                                                "city",
                                                                                            )}
                                                                                        </p>
                                                                                    </TooltipContent>
                                                                                </Tooltip>
                                                                            </div>
                                                                        </button>

                                                                        {expandedCities.has(
                                                                            cityData.city || "unknown",
                                                                        ) && (
                                                                            <div className="px-6 mt-3 space-y-2">
                                                                                {cityData.orders.map((order) => (
                                                                                    <div
                                                                                        key={order.name}
                                                                                        className="bg-gray-50 rounded-lg p-3 hover:bg-gray-100/50 transition-colors"
                                                                                    >
                                                                                        <button
                                                                                            onClick={() =>
                                                                                                toggleOrder(order.name)
                                                                                            }
                                                                                            className="w-full text-left"
                                                                                        >
                                                                                            <div className="flex items-center justify-between">
                                                                                                <div>
                                                                                                    <div className="font-medium text-gray-900">
                                                                                                        {order.name}
                                                                                                    </div>
                                                                                                    <div className="text-sm text-gray-600">
                                                                                                        {order.customer}
                                                                                                    </div>
                                                                                                </div>
                                                                                                <div className="text-right">
                                                                                                    <div className="font-medium text-gray-900">
                                                                                                        ₹
                                                                                                        {order.grand_total.toLocaleString()}
                                                                                                    </div>
                                                                                                    <div className="text-sm text-gray-600">
                                                                                                        {new Date(
                                                                                                            order.creation,
                                                                                                        ).toLocaleDateString()}
                                                                                                    </div>
                                                                                                </div>
                                                                                            </div>
                                                                                        </button>

                                                                                        {expandedOrders.has(
                                                                                            order.name,
                                                                                        ) && (
                                                                                            <div className="mt-3 pt-3 border-t border-gray-200">
                                                                                                <div className="flex flex-wrap gap-2">
                                                                                                    <span
                                                                                                        className={`px-2.5 py-1 rounded-full text-xs font-medium ${getStatusColor(order.status)}`}
                                                                                                    >
                                                                                                        {order.status}
                                                                                                    </span>
                                                                                                    <span
                                                                                                        className={`px-2.5 py-1 rounded-full text-xs font-medium ${getTypeColor(order.type_of_case)}`}
                                                                                                    >
                                                                                                        {order.type_of_case ||
                                                                                                            "Unspecified Type"}
                                                                                                    </span>
                                                                                                </div>
                                                                                            </div>
                                                                                        )}
                                                                                    </div>
                                                                                ))}
                                                                            </div>
                                                                        )}
                                                                    </div>
                                                                ))}
                                                            </div>
                                                        )}
                                                    </div>
                                                ))}
                                            </div>
                                        )}
                                    </div>
                                ))}

                                {/* Render unspecified state data if it exists */}
                                {unspecifiedState && (
                                    <div
                                        key="unspecified"
                                        className="bg-gray-50 rounded-lg shadow-sm border"
                                    >
                                        <button
                                            onClick={() => toggleState(null)}
                                            className="flex items-center justify-between w-full text-md font-medium text-gray-800 hover:bg-gray-100 p-3 rounded-lg transition-colors"
                                        >
                                            <div className="flex items-center">
                                                {expandedStates.has("unknown") ? (
                                                    <ChevronDown className="h-4 w-4 mr-2 text-gray-500" />
                                                ) : (
                                                    <ChevronRight className="h-4 w-4 mr-2 text-gray-500" />
                                                )}
                                                Unspecified State
                                            </div>
                                            <div className="flex items-center space-x-4">
                                                <Tooltip>
                                                    <TooltipTrigger asChild>
                                                        <span className="text-sm text-gray-600 bg-white px-2.5 py-1 rounded-full">
                                                            {unspecifiedState.count} Orders
                                                        </span>
                                                    </TooltipTrigger>
                                                    <TooltipContent>
                                                        <p>Total number of orders with unspecified state</p>
                                                    </TooltipContent>
                                                </Tooltip>
                                                <Tooltip>
                                                    <TooltipTrigger asChild>
                                                        <span className="text-sm text-gray-600 bg-white px-2.5 py-1 rounded-full">
                                                            ₹{unspecifiedState.total_amount.toLocaleString()}
                                                        </span>
                                                    </TooltipTrigger>
                                                    <TooltipContent>
                                                        <p>Total revenue from all orders with unspecified state</p>
                                                    </TooltipContent>
                                                </Tooltip>
                                            </div>
                                        </button>

                                        {expandedStates.has("unknown") && (
                                            <div className="px-6 pb-4 space-y-3">
                                                {unspecifiedState.districts.map((districtData) => (
                                                    <div
                                                        key={districtData.district || "unknown"}
                                                        className="bg-white rounded-lg p-3"
                                                    >
                                                        <button
                                                            onClick={() => toggleDistrict(districtData.district)}
                                                            className="flex items-center justify-between w-full text-sm text-gray-700 hover:bg-gray-50 p-2 rounded-lg transition-colors"
                                                        >
                                                            <div className="flex items-center">
                                                                {expandedDistricts.has(
                                                                    districtData.district || "unknown",
                                                                ) ? (
                                                                    <ChevronDown className="h-4 w-4 mr-2 text-gray-500" />
                                                                ) : (
                                                                    <ChevronRight className="h-4 w-4 mr-2 text-gray-500" />
                                                                )}
                                                                {getLocationName(
                                                                    districtData.district,
                                                                    "district",
                                                                    districtData.district_name,
                                                                )}
                                                            </div>
                                                            <div className="flex items-center space-x-4">
                                                                <Tooltip>
                                                                    <TooltipTrigger asChild>
                                                                        <span className="text-sm text-gray-600 bg-gray-50 px-2.5 py-1 rounded-full">
                                                                            {districtData.count} Orders
                                                                        </span>
                                                                    </TooltipTrigger>
                                                                    <TooltipContent>
                                                                        <p>
                                                                            Total number of orders in{" "}
                                                                            {getLocationName(
                                                                                districtData.district,
                                                                                "district",
                                                                                districtData.district_name,
                                                                            )}
                                                                        </p>
                                                                    </TooltipContent>
                                                                </Tooltip>
                                                                <Tooltip>
                                                                    <TooltipTrigger asChild>
                                                                        <span className="text-sm text-gray-600 bg-gray-50 px-2.5 py-1 rounded-full">
                                                                            ₹
                                                                            {districtData.total_amount.toLocaleString()}
                                                                        </span>
                                                                    </TooltipTrigger>
                                                                    <TooltipContent>
                                                                        <p>
                                                                            Total revenue from all orders in{" "}
                                                                            {getLocationName(
                                                                                districtData.district,
                                                                                "district",
                                                                                districtData.district_name,
                                                                            )}
                                                                        </p>
                                                                    </TooltipContent>
                                                                </Tooltip>
                                                            </div>
                                                        </button>

                                                        {expandedDistricts.has(districtData.district || "unknown") && (
                                                            <div className="px-6 mt-3 space-y-3">
                                                                {districtData.cities.map((cityData) => (
                                                                    <div
                                                                        key={cityData.city || "unknown"}
                                                                        className="bg-gray-50 rounded-lg p-3"
                                                                    >
                                                                        <button
                                                                            onClick={() => toggleCity(cityData.city)}
                                                                            className="flex items-center justify-between w-full text-sm text-gray-700 hover:bg-gray-100/50 p-2 rounded-lg transition-colors"
                                                                        >
                                                                            <div className="flex items-center">
                                                                                {expandedCities.has(
                                                                                    cityData.city || "unknown",
                                                                                ) ? (
                                                                                    <ChevronDown className="h-4 w-4 mr-2 text-gray-500" />
                                                                                ) : (
                                                                                    <ChevronRight className="h-4 w-4 mr-2 text-gray-500" />
                                                                                )}
                                                                                {getLocationName(cityData.city, "city")}
                                                                            </div>
                                                                            <div className="flex items-center space-x-4">
                                                                                <Tooltip>
                                                                                    <TooltipTrigger asChild>
                                                                                        <span className="text-sm text-gray-600 bg-white px-2.5 py-1 rounded-full">
                                                                                            {cityData.count} Orders
                                                                                        </span>
                                                                                    </TooltipTrigger>
                                                                                    <TooltipContent>
                                                                                        <p>
                                                                                            Total number of orders in{" "}
                                                                                            {getLocationName(
                                                                                                cityData.city,
                                                                                                "city",
                                                                                            )}
                                                                                        </p>
                                                                                    </TooltipContent>
                                                                                </Tooltip>
                                                                                <Tooltip>
                                                                                    <TooltipTrigger asChild>
                                                                                        <span className="text-sm text-gray-600 bg-white px-2.5 py-1 rounded-full">
                                                                                            ₹
                                                                                            {cityData.total_amount.toLocaleString()}
                                                                                        </span>
                                                                                    </TooltipTrigger>
                                                                                    <TooltipContent>
                                                                                        <p>
                                                                                            Total revenue from all
                                                                                            orders in{" "}
                                                                                            {getLocationName(
                                                                                                cityData.city,
                                                                                                "city",
                                                                                            )}
                                                                                        </p>
                                                                                    </TooltipContent>
                                                                                </Tooltip>
                                                                            </div>
                                                                        </button>

                                                                        {expandedCities.has(
                                                                            cityData.city || "unknown",
                                                                        ) && (
                                                                            <div className="px-6 mt-3 space-y-2">
                                                                                {cityData.orders.map((order) => (
                                                                                    <div
                                                                                        key={order.name}
                                                                                        className="bg-white rounded-lg p-3 hover:bg-gray-50 transition-colors"
                                                                                    >
                                                                                        <button
                                                                                            onClick={() =>
                                                                                                toggleOrder(order.name)
                                                                                            }
                                                                                            className="w-full text-left"
                                                                                        >
                                                                                            <div className="flex items-center justify-between">
                                                                                                <div>
                                                                                                    <div className="font-medium text-gray-900">
                                                                                                        {order.name}
                                                                                                    </div>
                                                                                                    <div className="text-sm text-gray-600">
                                                                                                        {order.customer}
                                                                                                    </div>
                                                                                                </div>
                                                                                                <div className="text-right">
                                                                                                    <div className="font-medium text-gray-900">
                                                                                                        ₹
                                                                                                        {order.grand_total.toLocaleString()}
                                                                                                    </div>
                                                                                                    <div className="text-sm text-gray-600">
                                                                                                        {new Date(
                                                                                                            order.creation,
                                                                                                        ).toLocaleDateString()}
                                                                                                    </div>
                                                                                                </div>
                                                                                            </div>
                                                                                        </button>

                                                                                        {expandedOrders.has(
                                                                                            order.name,
                                                                                        ) && (
                                                                                            <div className="mt-3 pt-3 border-t border-gray-200">
                                                                                                <div className="flex flex-wrap gap-2">
                                                                                                    <span
                                                                                                        className={`px-2.5 py-1 rounded-full text-xs font-medium ${getStatusColor(order.status)}`}
                                                                                                    >
                                                                                                        {order.status}
                                                                                                    </span>
                                                                                                    <span
                                                                                                        className={`px-2.5 py-1 rounded-full text-xs font-medium ${getTypeColor(order.type_of_case)}`}
                                                                                                    >
                                                                                                        {order.type_of_case ||
                                                                                                            "Unspecified Type"}
                                                                                                    </span>
                                                                                                </div>
                                                                                            </div>
                                                                                        )}
                                                                                    </div>
                                                                                ))}
                                                                            </div>
                                                                        )}
                                                                    </div>
                                                                ))}
                                                            </div>
                                                        )}
                                                    </div>
                                                ))}
                                            </div>
                                        )}
                                    </div>
                                )}
                            </div>
                        )}
                    </Card>
                );
            })}
        </div>
    );
};
