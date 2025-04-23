import { useEffect, useRef, useState } from "react";
import { Table, TableCell, TableRow, TableBody } from "@/components/ui/table";
import { ChevronRight } from "lucide-react";
import { Battery, Coins, Package, TrendingUp } from "lucide-react";
import { TerritoryRowProps } from "./types";
import { CityRow } from "./CityRow";
import { DepartmentRow } from "./DepartmentRow";
import { TableCellMetric } from "./TableCellMetric";

export const TerritoryRow = ({
    territoryData,
    territoryIndex,
    getLocationName,
    formatCurrency,
    formatDate,
    calculateAverage,
    createUniqueKey,
    getStatusColor,
    getTypeColor,
    registerRow,
    isFullExpansion,
    getERPUrl,
    getDepartmentColor,
    viewType = "location",
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

    const activeOrdersCount = territoryData.count - (territoryData.inactive_count || 0);

    return (
        <>
            <TableRow className="hover:bg-muted/50">
                <TableCell className="w-[300px] pl-8">
                    <div
                        className="flex items-center w-full cursor-pointer"
                        onClick={() => setIsOpen(!isOpen)}
                    >
                        <ChevronRight
                            className={`h-4 w-4 mr-2 inline transition-transform duration-300 ease-in-out ${isOpen ? "rotate-90" : "rotate-0"}`}
                        />
                        <span className="inline-block">{getLocationName(territoryData.territory, "territory")}</span>
                    </div>
                </TableCell>
                <TableCell className="w-[120px] text-center">
                    <TableCellMetric
                        icon={Package}
                        value={territoryData.count}
                        tooltip={`Total number of orders in ${getLocationName(territoryData.territory, "territory")}`}
                    />
                </TableCell>
                <TableCell className="w-[120px] text-center">
                    <TableCellMetric
                        icon={Package}
                        value={territoryData.inactive_count || 0}
                        tooltip={`Number of draft and cancelled orders in ${getLocationName(territoryData.territory, "territory")}`}
                    />
                </TableCell>
                <TableCell className="w-[150px] text-center">
                    <TableCellMetric
                        icon={Coins}
                        value={formatCurrency(territoryData.total_amount)}
                        tooltip={`Total revenue from all orders in ${getLocationName(territoryData.territory, "territory")}`}
                    />
                </TableCell>
                <TableCell className="w-[120px] text-center">
                    <TableCellMetric
                        icon={TrendingUp}
                        value={formatCurrency(calculateAverage(territoryData.total_amount, activeOrdersCount))}
                        tooltip={`Average order value in ${getLocationName(territoryData.territory, "territory")}`}
                    />
                </TableCell>
                <TableCell className="w-[120px] text-center">
                    <TableCellMetric
                        icon={Battery}
                        value={`${(territoryData.total_capacity || 0).toFixed(2)} kW`}
                        tooltip={`Total capacity in ${getLocationName(territoryData.territory, "territory")}`}
                    />
                </TableCell>
            </TableRow>

            <TableRow
                className={`transition-all duration-300 ease-in-out overflow-hidden ${isOpen ? "opacity-100" : "opacity-0 h-0"}`}
            >
                <TableCell
                    colSpan={6}
                    className={`p-0 ${!isOpen ? "py-0" : ""}`}
                >
                    <div
                        className={`overflow-hidden transition-all duration-300 ease-in-out ${isOpen ? "max-h-[5000px]" : "max-h-0"}`}
                    >
                        <Table className="w-full">
                            <TableBody>
                                {viewType === "location" &&
                                    "cities" in territoryData &&
                                    territoryData.cities.map((cityData, cityIndex) => (
                                        <CityRow
                                            key={createUniqueKey(cityData.city, "city", cityIndex)}
                                            cityData={cityData}
                                            cityIndex={cityIndex}
                                            getLocationName={getLocationName}
                                            formatCurrency={formatCurrency}
                                            formatDate={formatDate}
                                            calculateAverage={calculateAverage}
                                            createUniqueKey={createUniqueKey}
                                            getStatusColor={getStatusColor}
                                            getTypeColor={getTypeColor}
                                            registerRow={registerRow}
                                            isFullExpansion={isFullExpansion}
                                            getERPUrl={getERPUrl}
                                            getDepartmentColor={getDepartmentColor}
                                        />
                                    ))}
                                {viewType === "department" &&
                                    "departments" in territoryData &&
                                    territoryData.departments.map((departmentData, departmentIndex) => (
                                        <DepartmentRow
                                            key={createUniqueKey(
                                                departmentData.department,
                                                "department",
                                                departmentIndex,
                                            )}
                                            departmentData={departmentData}
                                            departmentIndex={departmentIndex}
                                            getLocationName={getLocationName}
                                            formatCurrency={formatCurrency}
                                            formatDate={formatDate}
                                            calculateAverage={calculateAverage}
                                            createUniqueKey={createUniqueKey}
                                            getStatusColor={getStatusColor}
                                            getTypeColor={getTypeColor}
                                            registerRow={registerRow}
                                            isFullExpansion={isFullExpansion}
                                            getERPUrl={getERPUrl}
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
